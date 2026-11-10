"""Create epics → stories → sub-issues on GitHub, add them to the Project and fill the fields.

Usage:  python create-backlog-issues-on-github.py [--dry-run]
Resumable: progress is kept in github-push-state.json; re-run continues where it stopped.
"""
import json
import sys
import time

import issue_body_renderer as R
from github_graphql_client import CONFIG_FILE, HERE, STATE_FILE, gql, load_json, save_json
from mock_owner_assignment import assign_owners

CREATE_Q = ("mutation($i:CreateIssueInput!){createIssue(input:$i){issue{id number url "
            "projectItems(first:5){nodes{id project{id}}}}}}")
KIND_VI = {"epic": "Epic", "story": "Issue", "task": "Sub-issue"}
FIELD_BATCH = 60  # aliased mutations per request


def option_id(cfg, field, name):
    for o in cfg["fields"][field]["options"]:
        if o["name"] == name:
            return o["id"]
    raise KeyError(f"{field}: option {name!r} not found")


def field_updates(cfg, it, owner, epic_names):
    """[(fieldId, valueLiteral)] for one item."""
    f = cfg["fields"]
    vals = [(f["Status"]["id"], option_id(cfg, "Status", "Todo")),
            (f["Loại"]["id"], option_id(cfg, "Loại", KIND_VI[it["kind"]])),
            (f["Epic"]["id"], option_id(cfg, "Epic", epic_names[it["epic_id"]])),
            (f["Phụ trách"]["id"], option_id(cfg, "Phụ trách", owner[it["id"]]))]
    if it["kind"] == "task":
        d = it["data"]
        vals += [(f["Vai trò"]["id"], option_id(cfg, "Vai trò", R.ROLE_VI[d["role"]])),
                 (f["Cỡ"]["id"], option_id(cfg, "Cỡ", R.SIZE_VI[d["size_hint"]]))]
    return [(fid, f'{{singleSelectOptionId:"{oid}"}}') for fid, oid in vals]


def create_issues(cfg, items, by_id, owner, state):
    for it in items:
        if it["id"] in state["issues"]:
            continue
        parent = state["issues"][it["parent_id"]]["node_id"] if it["parent_id"] else None
        inp = {"repositoryId": cfg["repo_id"], "title": R.title(it), "body": R.body(it, by_id, owner),
               "labelIds": [cfg["labels"][l] for l in R.labels(it)], "projectV2Ids": [cfg["project_id"]]}
        if parent:
            inp["parentIssueId"] = parent
        iss = gql(CREATE_Q, {"i": inp})["createIssue"]["issue"]
        item_id = next((n["id"] for n in iss["projectItems"]["nodes"]
                        if n["project"]["id"] == cfg["project_id"]), None)
        state["issues"][it["id"]] = {"number": iss["number"], "node_id": iss["id"], "url": iss["url"],
                                     "item_id": item_id, "fields_done": False}
        save_json(STATE_FILE, state)
        print(f"  #{iss['number']:<4} {R.title(it)[:70]}", flush=True)
        if iss["number"] != it["number"]:
            sys.exit(f"STOP: expected #{it['number']} for {it['id']} but got #{iss['number']} — "
                     "body references would be wrong; fix before continuing.")
        time.sleep(1.0)  # stay well under 80 content-creating requests / minute


def fill_fields(cfg, items, owner, epic_names, state):
    todo = [it for it in items if not state["issues"][it["id"]]["fields_done"]]
    batch, batch_ids = [], []
    for it in todo + [None]:
        if it is not None:
            item_id = state["issues"][it["id"]]["item_id"]
            for fid, val in field_updates(cfg, it, owner, epic_names):
                batch.append(f'm{len(batch)}:updateProjectV2ItemFieldValue(input:{{projectId:"'
                             f'{cfg["project_id"]}",itemId:"{item_id}",fieldId:"{fid}",value:{val}}})'
                             "{clientMutationId}")
            batch_ids.append(it["id"])
        if batch and (it is None or len(batch) >= FIELD_BATCH):
            gql("mutation{" + " ".join(batch) + "}")
            for i in batch_ids:
                state["issues"][i]["fields_done"] = True
            save_json(STATE_FILE, state)
            print(f"  fields set for {len(batch_ids)} items", flush=True)
            batch, batch_ids = [], []
            time.sleep(2)


def main():
    bd = json.loads((HERE.parent / "breakdown" / "breakdown.json").read_text(encoding="utf-8"))
    epics = bd["epics"]
    items = R.build_items(epics)
    by_id = {it["id"]: it for it in items}
    owner, load = assign_owners(epics)
    save_json(HERE / "mock-owner-assignment.json", {"load_hours_by_size_hint": load, "owner": owner})
    if "--dry-run" in sys.argv:
        print(len(items), "issues;", load)
        for key in ("E9", "S9.6", "BE-9.6.1"):
            print("=" * 60, "\n", R.title(by_id[key]), R.labels(by_id[key]), "\n", R.body(by_id[key], by_id, owner))
        return
    cfg = load_json(CONFIG_FILE, None)
    if not cfg or "fields" not in cfg:
        sys.exit("Run setup-github-project-and-fields.py first.")
    epic_names = {e["id"]: f"{e['id']} {e['name']}"[:50] for e in epics}
    state = load_json(STATE_FILE, {"issues": {}})
    create_issues(cfg, items, by_id, owner, state)
    fill_fields(cfg, items, owner, epic_names, state)
    save_json(HERE / "issue-number-map.json",
              {k: {"number": v["number"], "url": v["url"]} for k, v in state["issues"].items()})
    print("Done:", len(state["issues"]), "issues ->", cfg["project_url"])


if __name__ == "__main__":
    main()
