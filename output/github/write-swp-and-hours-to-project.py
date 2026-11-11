"""Write reviewed SWP and Estimate (h) to every Project item (sub-issues + rolled-up parents).

Input: output/estimate/swp-by-issue.json (exported from the validated sun-estimate payload).
Hours = SWP × HOURS_PER_SWP (see estimate.md). Parents get the plain sum of their children.
"""
import json
import time

from github_graphql_client import CONFIG_FILE, HERE, STATE_FILE, gql, load_json

BATCH = 12


def main():
    cfg, state = load_json(CONFIG_FILE, None), load_json(STATE_FILE, None)
    data = json.loads((HERE.parent / "estimate" / "swp-by-issue.json").read_text(encoding="utf-8"))
    swp_field, hour_field = cfg["fields"]["SWP"]["id"], cfg["fields"]["Estimate (h)"]["id"]
    muts = []
    for code, row in data["items"].items():
        item_id = state["issues"][code]["item_id"]
        for fid, val in ((swp_field, row["swp"]), (hour_field, row["hours"])):
            muts.append(f'updateProjectV2ItemFieldValue(input:{{projectId:"{cfg["project_id"]}",'
                        f'itemId:"{item_id}",fieldId:"{fid}",value:{{number:{val}}}}}){{clientMutationId}}')
    for i in range(0, len(muts), BATCH):
        chunk = muts[i:i + BATCH]
        gql("mutation{" + " ".join(f"m{k}:{m}" for k, m in enumerate(chunk)) + "}")
        print(f"  {min(i + BATCH, len(muts))}/{len(muts)} field values", flush=True)
        time.sleep(1.5)


if __name__ == "__main__":
    main()
