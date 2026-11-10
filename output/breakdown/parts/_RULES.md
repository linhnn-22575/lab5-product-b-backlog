# Rules for writing one epic part file (shared by all part-writers)

Product B = cold-chain warehouse system (Next.js + Supabase, extending LAB-2 prototype). Backlog → GitHub Project:
epic (issue) → story (issue) → task (sub-issue). Each task is later scored (SWP) + given hours → must be concrete,
single-owner, 4–16h. Course constraint: items affected by the Japan 2024 truck-driver hour cap = SEPARATE issues.

## File format — one file per epic: parts/E<n>.json
{ "id":"E9", "name":"...", "description":"...", "total_md":null,
  "stories":[ { "id":"S9.1", "name":"...", "description":"...", "screen":"SCR-016"|null, "estimate_ref":null, "total_md":null,
     "tasks":[ { "id":"BE-9.1.1", "name":"...", "role":"be", "md":null, "description":"...",
                 "checklist":["..."], "acceptance_criteria":["..."],
                 "size_hint":"S|M|L", "spec_refs":["SCR-016 §9"], "special_constraint":false, "depends_on":[] } ] } ] }

- Roles allowed: be, fe, qa_manual, infra, pm, brse. Id prefix: BE, FE, QA, INFRA, PM, BRSE + "-<epic>.<story>.<n>".
- name: tiếng Việt, ≤ 80 ký tự, bắt đầu bằng động từ. Prefix "[DRV] " if special_constraint=true (touches 2024 driver hours).
- description: 1–2 câu, nêu bảng/RPC/API cụ thể. checklist: 3–4 mục ngắn. acceptance_criteria: 2–3 mục kiểm chứng được.
- size_hint: S ≤4h, M ≤8h, L ≤16h. Nothing larger — split.
- Merge raw S-tasks of the same screen + same role. QA: normally ONE task per screen "Viết test case + chạy test SCR-xxx"
  (large screens SCR-042/053/060/061 may have 2). BrSE: at most one clarification task per epic (E9 excepted).
- Write each epic file with the Write tool SEPARATELY (one epic per Write call) to keep each write small.
- Do not invent scope beyond the extract reports / specs.

## Gap fragment — parts/gaps-<your-epics>.md
Table: Spec (file#section) | Chỗ hở/mâu thuẫn | Loại (hở/mâu thuẫn/lỗi thời) | Xử lý (sửa thiết kế / giả định / tạo issue làm rõ / để mở) | Task id
Only meaningful gaps for your epics (≤ 12). Plus a short list "Phần spec chưa thành task + vì sao".

## Decisions already made by the user (apply)
1. Route changed after publish must NOT block shipping: route keeps `published` while a draft exists; SCR-053
   confirm_shipment checks the current published route_version (sửa thiết kế, đã chốt).
2. New screen SCR-064 「乗務実績入力」: dispatcher enters actual shift/drive/break per driver per day → driver_duty_records
   source=actual_manual (sửa thiết kế, đã chốt) — belongs to E9.
3. SCR-016 lacks params long_day_threshold_h, drive_2week_anchor_date → add (đã chốt). One shared input_hash function
   (061 gap #10). One continuous-drive algorithm (BR-DRV-11) used for both auto-break insertion and checking (060 gap #2).
4. SCR-042 design fixes G-1/G-2/G-4 from group C (on_hold lots visible, no write-on-read, Storage upload outside tx).

Extract reports: lab5-product-b-backlog/plans/reports/screens-group-{a,b,c,d}-extract.md
Prototype gap list: lab4-product-b-design/specs/03-database/prototype-vs-design-gap.md
