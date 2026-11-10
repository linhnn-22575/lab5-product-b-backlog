"""Merge parts/E*.json into breakdown.json and validate against the task-breakdown schema rules."""
import json
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
PARTS = HERE / "parts"
ROLES = ["be", "fe", "qa_manual", "infra", "pm", "brse"]
PREFIX = {"be": "BE", "fe": "FE", "qa_manual": "QA", "infra": "INFRA", "pm": "PM", "brse": "BRSE"}
SIZE_H = {"S": 4, "M": 8, "L": 16}


def load_epics():
    files = sorted(PARTS.glob("E*.json"), key=lambda p: int(re.sub(r"\D", "", p.stem)))
    return [json.loads(f.read_text(encoding="utf-8")) for f in files]


def validate(epics):
    errors, ids = [], Counter()
    for e in epics:
        ids[e["id"]] += 1
        if not e.get("stories"):
            errors.append(f"{e['id']}: no stories")
        for s in e.get("stories", []):
            ids[s["id"]] += 1
            if not s["id"].startswith(f"S{e['id'][1:]}."):
                errors.append(f"{s['id']}: story id not under {e['id']}")
            if not s.get("tasks"):
                errors.append(f"{s['id']}: no tasks")
            for t in s.get("tasks", []):
                ids[t["id"]] += 1
                role = t.get("role")
                if role not in ROLES:
                    errors.append(f"{t['id']}: bad role {role}")
                elif not t["id"].startswith(PREFIX[role] + "-"):
                    errors.append(f"{t['id']}: prefix does not match role {role}")
                if t.get("size_hint") not in SIZE_H:
                    errors.append(f"{t['id']}: bad size_hint {t.get('size_hint')}")
                if t.get("special_constraint") and not t["name"].startswith("[DRV]"):
                    errors.append(f"{t['id']}: special_constraint without [DRV] prefix")
                if len(t.get("name", "")) > 90:
                    errors.append(f"{t['id']}: name too long")
    errors += [f"duplicate id {i}" for i, n in ids.items() if n > 1]
    all_task_ids = {t["id"] for e in epics for s in e["stories"] for t in s["tasks"]}
    for e in epics:
        for s in e["stories"]:
            for t in s["tasks"]:
                for d in t.get("depends_on", []):
                    if d not in all_task_ids:
                        errors.append(f"{t['id']}: depends_on unknown {d}")
    return errors


def main():
    epics = load_epics()
    errors = validate(epics)
    print(f"{'Epic':<5} {'Stories':>7} {'Tasks':>6} {'DRV':>4} {'Hours(hint)':>11}")
    tot = Counter()
    for e in epics:
        tasks = [t for s in e["stories"] for t in s["tasks"]]
        drv = sum(1 for t in tasks if t.get("special_constraint"))
        hrs = sum(SIZE_H.get(t.get("size_hint"), 0) for t in tasks)
        tot.update(stories=len(e["stories"]), tasks=len(tasks), drv=drv, hrs=hrs)
        print(f"{e['id']:<5} {len(e['stories']):>7} {len(tasks):>6} {drv:>4} {hrs:>11}")
    print(f"{'TOTAL':<5} {tot['stories']:>7} {tot['tasks']:>6} {tot['drv']:>4} {tot['hrs']:>11}")
    if errors:
        print("\nERRORS:")
        print("\n".join(errors))
        sys.exit(1)
    out = {
        "project_name": "Product B — Yuki Cold Logistics (LAB-5)",
        "breakdown_level": 3,
        "language": "vi",
        "source": "pre-estimate",
        "source_file": "lab4-product-b-design/specs",
        "generated_date": "2026-11-10",
        "active_roles": ROLES,
        "role_names": {"be": "Backend", "fe": "Frontend", "qa_manual": "QA (Manual)",
                       "infra": "Infra", "pm": "PM", "brse": "BrSE"},
        "epics": epics,
    }
    (HERE / "breakdown.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\nOK -> breakdown.json")


if __name__ == "__main__":
    main()
