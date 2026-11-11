"""One-off setup: labels, public GitHub Project linked to the repo, custom fields, sprints.

Idempotent: re-running reuses what github-project-config.json already records.
Requires `gh auth refresh -s project`.
"""
import json
from datetime import date, timedelta

from github_graphql_client import CONFIG_FILE, OWNER, REPO, gh_json, gql, load_json, save_json
from mock_owner_assignment import ALL_OWNERS

PROJECT_TITLE = "LAB-5 Product B — Yuki Cold Logistics backlog"
LABELS = {
    "type:epic": ("5319e7", "Epic — nhóm chức năng lớn"),
    "type:story": ("1d76db", "Issue — một màn hình / một khối nghiệp vụ"),
    "type:task": ("c5def5", "Sub-issue — việc 4–16h, một người làm"),
    "special-constraint": ("b60205", "Ràng buộc giới hạn giờ lái xe tải 2024 (BR-DRV)"),
    "role:be": ("0e8a16", "Backend"), "role:fe": ("fbca04", "Frontend"),
    "role:qa": ("d93f0b", "QA Manual"), "role:infra": ("006b75", "Infra"),
    "role:pm": ("5319e7", "PM"), "role:brse": ("e99695", "BrSE — tạo và review spec"),
}
STATUS = [("Todo", "GRAY"), ("In Progress", "YELLOW"), ("In Review", "BLUE"),
          ("Blocked", "RED"), ("Done", "GREEN")]
SPRINT_START, SPRINT_DAYS, SPRINT_COUNT = date(2026, 11, 16), 14, 10


def opts(names, color="GRAY"):
    return [{"name": n, "color": color, "description": ""} for n in names]


def ensure_labels(cfg):
    for name, (color, desc) in LABELS.items():
        gh_json(["label", "create", name, "--repo", f"{OWNER}/{REPO}", "--color", color,
                 "--description", desc, "--force"])
    labels = gh_json(["api", f"repos/{OWNER}/{REPO}/labels?per_page=100"])
    cfg["labels"] = {l["name"]: l["node_id"] for l in labels if l["name"] in LABELS}


def ensure_project(cfg):
    if "project_id" in cfg:
        return
    d = gql("query($o:String!,$r:String!){user(login:$o){id} repository(owner:$o,name:$r){id}}",
            {"o": OWNER, "r": REPO})
    cfg["owner_id"], cfg["repo_id"] = d["user"]["id"], d["repository"]["id"]
    p = gql("mutation($o:ID!,$t:String!,$r:ID!){createProjectV2(input:{ownerId:$o,title:$t,"
            "repositoryId:$r}){projectV2{id number url}}}",
            {"o": cfg["owner_id"], "t": PROJECT_TITLE, "r": cfg["repo_id"]})["createProjectV2"]["projectV2"]
    cfg.update(project_id=p["id"], project_number=p["number"], project_url=p["url"])
    gql("mutation($p:ID!,$d:String!){updateProjectV2(input:{projectId:$p,public:true,"
        "shortDescription:$d}){projectV2{id}}}",
        {"p": p["id"], "d": "Backlog LAB-5 (dữ liệu giả lập, nội dung tự viết)"})
    save_json(CONFIG_FILE, cfg)


def create_field(cfg, name, data_type, options=None, iteration=None):
    inp = {"projectId": cfg["project_id"], "dataType": data_type, "name": name}
    if options:
        inp["singleSelectOptions"] = options
    if iteration:
        inp["iterationConfiguration"] = iteration
    q = ("mutation($i:CreateProjectV2FieldInput!){createProjectV2Field(input:$i){projectV2Field{"
         "... on ProjectV2Field{id} ... on ProjectV2SingleSelectField{id options{id name}}"
         "... on ProjectV2IterationField{id configuration{iterations{id title startDate}}}}}}")
    return gql(q, {"i": inp})["createProjectV2Field"]["projectV2Field"]


def ensure_fields(cfg, epic_names):
    fields = cfg.setdefault("fields", {})
    status_q = ("query($p:ID!){node(id:$p){... on ProjectV2{field(name:\"Status\"){"
                "... on ProjectV2SingleSelectField{id}}}}}")
    if "Status" not in fields:
        sid = gql(status_q, {"p": cfg["project_id"]})["node"]["field"]["id"]
        f = gql("mutation($f:ID!,$o:[ProjectV2SingleSelectFieldOptionInput!]){updateProjectV2Field("
                "input:{fieldId:$f,singleSelectOptions:$o}){projectV2Field{... on "
                "ProjectV2SingleSelectField{id options{id name}}}}}",
                {"f": sid, "o": [{"name": n, "color": c, "description": ""} for n, c in STATUS]})
        fields["Status"] = f["updateProjectV2Field"]["projectV2Field"]
    specs = [("Loại", "SINGLE_SELECT", opts(["Epic", "Issue", "Sub-issue"])),
             ("Epic", "SINGLE_SELECT", opts(epic_names, "PURPLE")),
             ("Vai trò", "SINGLE_SELECT", opts(["BE", "FE", "QA Manual", "Infra", "PM", "BrSE"], "BLUE")),
             ("Phụ trách", "SINGLE_SELECT", opts(ALL_OWNERS, "GREEN")),
             ("Cỡ", "SINGLE_SELECT", opts(["S (≤4h)", "M (≤8h)", "L (≤16h)"])),
             ("SWP", "NUMBER", None), ("Estimate (h)", "NUMBER", None)]
    for name, dtype, options in specs:
        if name not in fields:
            fields[name] = create_field(cfg, name, dtype, options)
            save_json(CONFIG_FILE, cfg)
    if "Iteration" not in fields:
        its = [{"title": f"Sprint {i + 1}", "duration": SPRINT_DAYS,
                "startDate": (SPRINT_START + timedelta(days=SPRINT_DAYS * i)).isoformat()}
               for i in range(SPRINT_COUNT)]
        fields["Iteration"] = create_field(cfg, "Iteration", "ITERATION", iteration={
            "startDate": SPRINT_START.isoformat(), "duration": SPRINT_DAYS, "iterations": its})
    save_json(CONFIG_FILE, cfg)


def main():
    cfg = load_json(CONFIG_FILE, {})
    bd = json.loads((CONFIG_FILE.parent.parent / "breakdown" / "breakdown.json").read_text(encoding="utf-8"))
    ensure_labels(cfg)
    ensure_project(cfg)
    ensure_fields(cfg, [f"{e['id']} {e['name']}"[:50].strip() for e in bd["epics"]])
    save_json(CONFIG_FILE, cfg)
    print("Project:", cfg["project_url"])


if __name__ == "__main__":
    main()
