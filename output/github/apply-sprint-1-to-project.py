"""Push the simulated Sprint 1 result to GitHub: Iteration + Status on each item, close Done issues.

Input: output/sprint/sprint-1-simulation.json. Idempotent (re-setting the same values is harmless;
closing an already-closed issue is skipped).
"""
import json
import time

from github_graphql_client import CONFIG_FILE, HERE, STATE_FILE, gql, load_json

BATCH = 12


def option(cfg, field, name):
    return next(o["id"] for o in cfg["fields"][field]["options"] if o["name"] == name)


def reset_dropped(cfg, state, sim, it_title):
    """Items still on the iteration but no longer in the simulation → clear Iteration, Todo, reopen."""
    keep = {t["id"] for t in sim["tasks"]}
    by_item = {v["item_id"]: (k, v["node_id"]) for k, v in state["issues"].items()}
    q = ("query($p:ID!,$c:String){node(id:$p){... on ProjectV2{items(first:100,after:$c){pageInfo{hasNextPage "
         "endCursor} nodes{id fieldValueByName(name:\"Iteration\"){... on ProjectV2ItemFieldIterationValue{title}}}}}}}")
    dropped, cursor = [], None
    while True:
        page = gql(q, {"p": cfg["project_id"], "c": cursor})["node"]["items"]
        dropped += [n["id"] for n in page["nodes"] if (n.get("fieldValueByName") or {}).get("title") == it_title
                    and by_item.get(n["id"], ("", ""))[0] not in keep]
        if not page["pageInfo"]["hasNextPage"]:
            break
        cursor = page["pageInfo"]["endCursor"]
    pid, todo = cfg["project_id"], option(cfg, "Status", "Todo")
    for k, item in enumerate(dropped):
        gql(f'mutation{{a:clearProjectV2ItemFieldValue(input:{{projectId:"{pid}",itemId:"{item}",'
            f'fieldId:"{cfg["fields"]["Iteration"]["id"]}"}}){{clientMutationId}} '
            f'b:updateProjectV2ItemFieldValue(input:{{projectId:"{pid}",itemId:"{item}",'
            f'fieldId:"{cfg["fields"]["Status"]["id"]}",value:{{singleSelectOptionId:"{todo}"}}}}){{clientMutationId}} '
            f'c:reopenIssue(input:{{issueId:"{by_item[item][1]}"}}){{issue{{number}}}}}}')
        print(f"  reset {by_item[item][0]}", flush=True)


def main():
    cfg, state = load_json(CONFIG_FILE, None), load_json(STATE_FILE, None)
    sim = json.loads((HERE.parent / "sprint" / "sprint-1-simulation.json").read_text(encoding="utf-8"))
    it_field = cfg["fields"]["Iteration"]
    it_id = next(i["id"] for i in it_field["configuration"]["iterations"] if i["title"] == sim["iteration"])
    reset_dropped(cfg, state, sim, sim["iteration"])
    pid, muts, to_close = cfg["project_id"], [], []
    for t in sim["tasks"]:
        item = state["issues"][t["id"]]["item_id"]
        muts.append((item, it_field["id"], f'{{iterationId:"{it_id}"}}'))
        muts.append((item, cfg["fields"]["Status"]["id"],
                     f'{{singleSelectOptionId:"{option(cfg, "Status", t["status"])}"}}'))
        if t["status"] == "Done":
            to_close.append(state["issues"][t["id"]]["node_id"])
    for i in range(0, len(muts), BATCH):
        body = " ".join(f'm{k}:updateProjectV2ItemFieldValue(input:{{projectId:"{pid}",itemId:"{item}",'
                        f'fieldId:"{fid}",value:{val}}}){{clientMutationId}}'
                        for k, (item, fid, val) in enumerate(muts[i:i + BATCH]))
        gql("mutation{" + body + "}")
        print(f"  {min(i + BATCH, len(muts))}/{len(muts)} field values", flush=True)
        time.sleep(1.5)
    open_ids = [state["issues"][t["id"]]["node_id"] for t in sim["tasks"] if t["status"] != "Done"]
    states = gql("query($ids:[ID!]!){nodes(ids:$ids){... on Issue{id state}}}", {"ids": open_ids})["nodes"]
    for n in (n for n in states if n["state"] == "CLOSED"):  # closed by an earlier run but no longer Done
        gql(f'mutation{{reopenIssue(input:{{issueId:"{n["id"]}"}}){{issue{{number}}}}}}')
    for i in range(0, len(to_close), BATCH):
        body = " ".join(f'c{k}:closeIssue(input:{{issueId:"{nid}",stateReason:COMPLETED}}){{issue{{number}}}}'
                        for k, nid in enumerate(to_close[i:i + BATCH]))
        gql("mutation{" + body + "}")
        print(f"  closed {min(i + BATCH, len(to_close))}/{len(to_close)} Done issues", flush=True)
        time.sleep(1.5)


if __name__ == "__main__":
    main()
