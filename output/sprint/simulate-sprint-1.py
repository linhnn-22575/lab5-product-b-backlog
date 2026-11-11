"""Deterministic simulation of Sprint 1 (2026/11/16–2026/11/27, 10 working days).

1. Commit: walk tasks in priority/dependency order; each owner takes up to CAPACITY_SWP.
2. Execute: each owner works 6 focus hours/day on the first committed task whose deps are done.
   Actual effort = SWP × PLAN_H_PER_SWP × factor (default ACTUAL_FACTOR, overrides below).
3. Close: Done (finished ≤ day 9) · In Review (finished day 10) · In Progress · Blocked · Todo.
Output: sprint-1-simulation.json (input for the Project update, burndown and progress-report.md).
"""
import json
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).parent / "sprint-1-simulation.json"
START, DAYS, HOURS_PER_DAY = date(2026, 11, 16), 10, 6
PLAN_H_PER_SWP, CAPACITY_SWP, ACTUAL_FACTOR = 2, 30, 1.25
EPIC_PRIORITY = ["E1", "E10", "E9", "E2", "E3", "E6", "E4", "E5", "E8", "E7", "E11"]
# Simulated events (documented in progress-report.md §3/§4)
OVERRUN = {"BE-1.1.2": 2.0}  # migration: balance after migrate did not match qty_on_hand → re-run twice
# Sprint-management work is committed first; E11 tasks that need a running system are held back
# (breakdown.json gives them no depends_on on feature work — gap found during this simulation).
PINNED = ["PM-11.3.1", "PM-11.3.2"]
HOLD = {"QA-11.1.2", "QA-11.2.1", "BRSE-11.2.2", "INFRA-11.3.3"}
EXTERNAL_BLOCK = {  # waiting on parties outside the team; no progress possible this sprint
    "BRSE-10.1.3": "Khách chưa trả lời bộ Q&A gửi ngày 2026/11/18 (hẹn 2026/12/02)",
    "PM-9.13.1": "Chưa có xác nhận pháp lý OPS-LAW-01 từ bộ phận pháp chế của khách",
}


def workdays():
    d, out = START, []
    while len(out) < DAYS:
        if d.weekday() < 5:
            out.append(d)
        d += timedelta(days=1)
    return out


def load():
    bd = json.loads((ROOT / "output/breakdown/breakdown.json").read_text(encoding="utf-8"))
    owner = json.loads((ROOT / "output/github/mock-owner-assignment.json").read_text(encoding="utf-8"))["owner"]
    est = json.loads((ROOT / "output/estimate/swp-by-issue.json").read_text(encoding="utf-8"))["items"]
    tasks = []
    for e in sorted(bd["epics"], key=lambda e: EPIC_PRIORITY.index(e["id"])):
        for s in e["stories"]:
            for t in s["tasks"]:
                tasks.append({"id": t["id"], "epic": e["id"], "story": s["id"], "owner": owner[t["id"]],
                              "swp": est[t["id"]]["swp"], "number": est[t["id"]]["number"],
                              "deps": t.get("depends_on", []), "drv": bool(t.get("special_constraint"))})
    return tasks


def commit(tasks):
    load_by, chosen = {}, {}
    ordered = sorted(tasks, key=lambda t: t["id"] not in PINNED)  # stable: pinned first, rest keep priority
    changed = True
    while changed:
        changed = False
        for t in ordered:
            if t["id"] in chosen or t["id"] in HOLD or not all(d in chosen for d in t["deps"]):
                continue
            if load_by.get(t["owner"], 0) + t["swp"] <= CAPACITY_SWP:
                chosen[t["id"]] = t
                load_by[t["owner"]] = load_by.get(t["owner"], 0) + t["swp"]
                changed = True
    return [t for t in ordered if t["id"] in chosen]


def execute(sprint):
    days = workdays()
    for t in sprint:
        t["effort_h"] = t["swp"] * PLAN_H_PER_SWP * OVERRUN.get(t["id"], ACTUAL_FACTOR)
        t.update(spent_h=0.0, done_day=None, started=False)
    by_owner = {}
    for t in sprint:
        by_owner.setdefault(t["owner"], []).append(t)
    done = set()
    for di in range(DAYS):
        finished_today = []
        for queue in by_owner.values():
            hours = HOURS_PER_DAY
            while hours > 0:
                ready = [t for t in queue if t["done_day"] is None and t["id"] not in EXTERNAL_BLOCK
                         and all(d in done or d not in {x["id"] for x in sprint} for d in t["deps"])]
                ready = [t for t in ready if all(d in done for d in t["deps"] if d in {x["id"] for x in sprint})]
                if not ready:
                    break
                t = next((x for x in ready if x["started"]), ready[0])
                t["started"] = True
                use = min(hours, t["effort_h"] - t["spent_h"])
                t["spent_h"] += use
                hours -= use
                if t["spent_h"] >= t["effort_h"] - 1e-9:
                    t["done_day"] = di + 1
                    finished_today.append(t["id"])
        done.update(finished_today)  # dependants can start from the next day
    for t in sprint:
        if t["id"] in EXTERNAL_BLOCK:
            t["status"], t["note"] = "Blocked", EXTERNAL_BLOCK[t["id"]]
        elif t["done_day"] and t["done_day"] < DAYS:
            t["status"], t["note"] = "Done", ""
        elif t["done_day"] == DAYS:
            t["status"], t["note"] = "In Review", "Xong code ngày cuối, PR chưa review"
        elif t["started"]:
            t["status"], t["note"] = "In Progress", f"Đã làm {t['spent_h']:.0f}/{t['effort_h']:.0f}h"
        else:
            t["status"], t["note"] = "Todo", "Chưa bắt đầu (chờ việc phụ thuộc hoặc hết giờ)"
    return days


def main():
    tasks = load()
    sprint = commit(tasks)
    days = execute(sprint)
    total = sum(t["swp"] for t in sprint)
    burndown = []
    for di, d in enumerate(days, start=1):
        burned = sum(t["swp"] for t in sprint if t["status"] == "Done" and t["done_day"] <= di)
        burndown.append({"day": di, "date": d.isoformat(), "ideal": round(total - total * di / DAYS, 1),
                         "remaining": total - burned})
    out = {"iteration": "Sprint 1", "start": START.isoformat(), "end": days[-1].isoformat(),
           "assumptions": {"plan_h_per_swp": PLAN_H_PER_SWP, "actual_factor": ACTUAL_FACTOR,
                           "capacity_swp_per_person": CAPACITY_SWP, "focus_h_per_day": HOURS_PER_DAY,
                           "overrun": OVERRUN, "external_block": EXTERNAL_BLOCK},
           "committed_swp": total, "burndown": [{"day": 0, "date": START.isoformat(), "ideal": total,
                                                 "remaining": total}] + burndown,
           "tasks": [{k: t[k] for k in ("id", "number", "epic", "story", "owner", "swp", "drv", "status",
                                        "note", "done_day", "deps")} | {"spent_h": round(t["spent_h"], 1),
                                                                         "effort_h": t["effort_h"]}
                     for t in sprint]}
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    from collections import Counter
    c = Counter(t["status"] for t in sprint)
    print("committed", len(sprint), "tasks", total, "SWP;", dict(c))
    print({s: sum(t["swp"] for t in sprint if t["status"] == s) for s in c})
    print({o: sum(t["swp"] for t in sprint if t["owner"] == o) for o in sorted({t["owner"] for t in sprint})})
    print([(b["day"], b["remaining"]) for b in out["burndown"]])


if __name__ == "__main__":
    main()
