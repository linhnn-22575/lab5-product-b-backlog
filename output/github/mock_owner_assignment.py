"""Deterministic assignment of mock owners (BE 1, FE 2...) to tasks, balanced by size-hint hours.

Rule: within one role, all tasks of one story go to the same person (keeps context together);
stories are handed out largest-first to whoever currently has the fewest hours (LPT greedy).
"""
from collections import defaultdict

SIZE_H = {"S": 4, "M": 8, "L": 16}
OWNERS_BY_ROLE = {
    "be": ["BE 1", "BE 2"],
    "fe": ["FE 1", "FE 2"],
    "qa_manual": ["QA 1"],
    "infra": ["Infra/PM 1"],
    "pm": ["Infra/PM 1"],
    "brse": ["BrSE 1"],
}
EPIC_OWNER = "Infra/PM 1"
ALL_OWNERS = ["BE 1", "BE 2", "FE 1", "FE 2", "QA 1", "Infra/PM 1", "BrSE 1"]


def assign_owners(epics):
    """Return {task_or_story_or_epic_id: owner}."""
    owner, load = {}, defaultdict(int)
    for role, people in OWNERS_BY_ROLE.items():
        bundles = []
        for e in epics:
            for s in e["stories"]:
                tasks = [t for t in s["tasks"] if t["role"] == role]
                if tasks:
                    bundles.append((sum(SIZE_H[t["size_hint"]] for t in tasks), s["id"], tasks))
        for hours, _sid, tasks in sorted(bundles, key=lambda b: (-b[0], b[1])):
            person = min(people, key=lambda p: (load[p], people.index(p)))
            load[person] += hours
            for t in tasks:
                owner[t["id"]] = person
    for e in epics:
        owner[e["id"]] = EPIC_OWNER
        for s in e["stories"]:
            per = defaultdict(int)
            for t in s["tasks"]:
                per[owner[t["id"]]] += SIZE_H[t["size_hint"]]
            owner[s["id"]] = max(per, key=lambda p: (per[p], -ALL_OWNERS.index(p)))
    return owner, dict(load)
