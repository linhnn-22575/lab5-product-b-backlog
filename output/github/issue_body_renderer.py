"""Builds the ordered issue list (epic → story → task) and renders titles/bodies in Vietnamese.

Issue numbers are pre-computed from creation order (fresh repo → #1, #2, ...) so bodies can
reference issues that are created later ("Blocked by #n"). The creator verifies each number.
"""
ROLE_VI = {"be": "BE", "fe": "FE", "qa_manual": "QA Manual", "infra": "Infra", "pm": "PM", "brse": "BrSE"}
ROLE_LABEL = {"be": "role:be", "fe": "role:fe", "qa_manual": "role:qa", "infra": "role:infra",
              "pm": "role:pm", "brse": "role:brse"}
SIZE_VI = {"S": "S (≤4h)", "M": "M (≤8h)", "L": "L (≤16h)"}
DRV_NOTE = ("> **Ràng buộc giờ lái xe tải 2024** — hạng mục tách riêng (nhãn `special-constraint`). "
            "Rule BR-DRV: business-rules §7 + ADR-006 của bộ thiết kế LAB-4.")


def build_items(epics):
    """Flat list in creation order; each item: kind, id, data, parent_id, epic_id, number."""
    items = []
    for e in epics:
        items.append({"kind": "epic", "id": e["id"], "data": e, "parent_id": None, "epic_id": e["id"]})
        for s in e["stories"]:
            items.append({"kind": "story", "id": s["id"], "data": s, "parent_id": e["id"], "epic_id": e["id"]})
            for t in s["tasks"]:
                items.append({"kind": "task", "id": t["id"], "data": t, "parent_id": s["id"],
                              "epic_id": e["id"]})
    for n, it in enumerate(items, start=1):
        it["number"] = n
    return items


def title(it):
    return f"{it['id']} {it['data']['name']}"


def labels(it):
    if it["kind"] == "epic":
        out = ["type:epic"]
        if any(t.get("special_constraint") for s in it["data"]["stories"] for t in s["tasks"]):
            out.append("special-constraint")
        return out
    if it["kind"] == "story":
        drv = any(t.get("special_constraint") for t in it["data"]["tasks"])
        return ["type:story"] + (["special-constraint"] if drv else [])
    t = it["data"]
    return ["type:task", ROLE_LABEL[t["role"]]] + (["special-constraint"] if t.get("special_constraint") else [])


def _ref(by_id, key):
    other = by_id[key]
    return f"#{other['number']} ({key})"


def body(it, by_id, owner):
    d = it["data"]
    parts = []
    if it["kind"] == "epic":
        parts += [f"**Epic {d['id']}** · Phụ trách giả định: {owner[d['id']]}", "", d.get("description", "")]
        if "special-constraint" in labels(it):
            parts += ["", DRV_NOTE]
        parts += ["", "## Issue trong epic"]
        parts += [f"- {_ref(by_id, s['id'])} {s['name']}" for s in d["stories"]]
    elif it["kind"] == "story":
        screen = f" · Màn hình: `{d['screen']}`" if d.get("screen") else ""
        parts += [f"**Issue {d['id']}** · Epic: {_ref(by_id, it['epic_id'])}{screen}", "",
                  d.get("description", "")]
        if "special-constraint" in labels(it):
            parts += ["", DRV_NOTE]
        parts += ["", "## Sub-issue", *[f"- {_ref(by_id, t['id'])} {t['name']}" for t in d["tasks"]]]
    else:
        parts += [f"**{d['id']}** · Vai trò: {ROLE_VI[d['role']]} · Cỡ: {SIZE_VI[d['size_hint']]} · "
                  f"Phụ trách giả định: {owner[d['id']]} · Issue cha: {_ref(by_id, it['parent_id'])}"]
        if d.get("special_constraint"):
            parts += ["", DRV_NOTE]
        parts += ["", "## Mô tả", d.get("description", ""), "", "## Checklist"]
        parts += [f"- [ ] {c}" for c in d.get("checklist", [])]
        parts += ["", "## Tiêu chí hoàn thành (AC)"]
        parts += [f"- {a}" for a in d.get("acceptance_criteria", [])]
        if d.get("spec_refs"):
            parts += ["", "## Spec tham chiếu (bộ thiết kế LAB-4)"]
            parts += [f"- {r}" for r in d["spec_refs"]]
        if d.get("depends_on"):
            parts += ["", "## Phụ thuộc", "Blocked by: " + ", ".join(_ref(by_id, x) for x in d["depends_on"])]
    parts += ["", "---", "_Sinh từ `output/breakdown/breakdown.json`. Dữ liệu giả lập cho bài LAB-5._"]
    return "\n".join(parts)
