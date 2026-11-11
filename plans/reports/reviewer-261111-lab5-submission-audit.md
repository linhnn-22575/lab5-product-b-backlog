# LAB-5 submission audit (read-only)

Scope: README, PREMISE, task-breakdown, estimate, progress-report, AI-report; output/estimate/swp-by-issue.json, output/sprint/sprint-1-simulation.json, output/github/issue-number-map.json, reports/*, live Project (279 items pulled via `gh project item-list`).

## Verdict
Numbers are consistent everywhere I checked. No critical defects. 0 secrets, 0 personal data, 0 broken relative links. A few overstated or contradictory sentences and one unmet requirement (incognito note).

## Verified OK
- Live Project: 11 Epic / 49 Issue / 219 Sub-issue; sub-issue SWP 997, hours 1994 (epic sum = issue sum = 997). Every item has SWP, Estimate (h), Phụ trách. swp-by-issue.json (279 entries) equals Project item by item.
- Per-epic table in estimate.md §3 matches Project exactly (E1 14/71/142 ... E11 7/36/72; issue counts 5,3,4,2,3,6,3,5,13,2,3).
- Sprint 1: 36 items / 147 SWP; Done 23/91, In Review 2/7, In Progress 3/21, Todo 6/24, Blocked 2/4 = Project = simulation JSON. 23 closed issues = Done. Per-epic and per-person tables in progress-report match JSON (297.5h of 420h, 2.5h/SWP, FE 25/120h, QA 32.5/60h, 13 carried / 56 SWP, 183 / 850 outside sprint, 62%, 71%).
- Burndown table (11 rows) equals JSON burndown, deviations recomputed correct (+14.7 ... +56.0); SVG labels agree.
- All 59 `[CODE #n]` links in README/PREMISE/task-breakdown/estimate/progress-report match issue-number-map.json; map matches live titles for all 279 codes (e.g. BE-1.1.2=#4, BE-7.2.1=#156, BE-9.3.2=#212, BRSE-2.3.6=#42, FE-3.4.5=#66, BE-9.1.1=#199, BRSE-9.11.1=#250, QA-9.9.5=#237, PM-9.13.1=#259, BRSE-10.1.3=#265). Every `issues/N` URL exists.
- estimate.md §4: every LAB-1 MD×8, every diff, the MD column sum (1516) and 12,128h / -10,134h, the 66% (6,706h / 10,134h) all recompute correctly. §3 rows sum to 1994. §2: avg SWP by size M 4.02 / L 5.43 / S 2.21, ceiling 2,560h, 78%, E9 ceiling 520h all recompute from breakdown.json. 34h (E10 24h + E11 PM 10h) and 50h (E11 QA 42h + BrSE 8h) correct. Role split of E9 (BE118/QA42/FE40/BrSE6/Infra3/PM1) and QA 174 SWP (17.5%) correct.
- 5 sample issues: Scope/Complexity/SWP in HTML audit payload match the table (#156 1x1, #66 3x2, #4 5x3, #212 1x1, #42 2x1), "Accepted without changes" for all 5.
- Required parts/columns present and in order in all six files. PREMISE: 14 P, 9 A5, 7 D, all columns. task-breakdown: 4 parts incl. DoD, epic→issue→sub-issue usage.
- HTTP 200 without auth for repo, Project, issue #197, HTML blob (I re-ran curl) — README:27 claim holds.
- Relative links: all resolve. Secret/PII grep: nothing in tracked files (only a `.log` hit, which is git-ignored/untracked; no token found on inspection). Root `.env*`, `*.log`, state file ignored.

## Critical
None.

## Warning
1. README.md:30 — assignment requires a note that links were tested in incognito; checkbox still `[ ]`. Honest (AI-report:50 explains), but requirement unmet. Fix: tick it after you really open it in a private window, or reword to "chưa kiểm bằng ẩn danh; đã kiểm HTTP 200 không cookie".
2. Circular evidence: simulate-sprint-1.py hard-codes `actual_factor 1.25`, so "tốc độ thật 2,5h/SWP" (progress-report.md:14,16,80,94,98; estimate.md:46,97) is an input, not a finding. Only AI-report.md:75 discloses it. Fix: in progress-report §2 add "2,5h/SWP là tham số giả lập (×1,25), không phải đo thực"; estimate.md:97 say "nếu thực tế là 2,5h/SWP" rather than "bản giả lập: thực tế cần".
3. "Mỗi rule BR-DRV là một sub-issue" is overstated: README.md:13, task-breakdown.md:78 ("Mỗi rule là một sub-issue riêng"), estimate.md:83, PREMISE.md D-01 (line 50). Table at task-breakdown.md:85,87,93,95,97 groups BR-DRV-04/05, 07/08, 02/03 (2 issues), 20/22/23, 24/25. Fix: "mỗi rule hoặc cặp rule cùng ngưỡng".
4. task-breakdown.md:104 says LAB-1 estimated F07 only generically as "điều phối tuyến", but estimate.md:82-83 shows LAB-1 split F07 into FN-0701/0702/0705 (39 MD) and FN-0703/0704/0706 (42 MD). Contradiction. Fix: delete or rewrite the sentence ("LAB-1 ước F07 giờ lái 42 MD").
5. task-breakdown.md:135 (SCR-010 vs SCR-011 navigation): handling is "Đã sửa thiết kế trong task FE-3.1.3" with no PREMISE row. Assignment: design fixed → must point to a PREMISE row. Fix: add P-15 or A5-10 in PREMISE, or relabel as "chọn 1 cách khi làm, không đổi spec".
6. estimate.md:96 "thấp hơn LAB-1 khoảng 2–5 lần, trừ F07": E1 is 920/142 = 6.5x and F02 536/102 = 5.3x. Fix: "2–6,5 lần".
7. estimate.md:27 says hard parts "BE-9.6.1, BE-9.2.x, BE-9.8.x có điểm cao hơn" — BE-9.6.1 (the "most complex algorithm", task-breakdown.md:90) is only 3 SWP, BE-9.3.1 also 3; others 2–6. Justification for 1–2 SWP rule scoring is thin. Fix: cite real values (9.2.x 3/5/2, 9.8.x 5–6) and concede 9.6.1=3 is low; or flag as reviewer risk in estimate.md §1.
8. Iteration field: 183 of 219 sub-issues and all epics/issues have no Iteration (only Sprint 1 filled). task-breakdown.md:36 says Iteration Sprint 1–10 exists (field yes, values no). Probably acceptable but state it: "chỉ Sprint 1 được gán; các sprint sau chưa lập kế hoạch" in task-breakdown.md:36 or README:32.

## Suggestion
- progress-report.md:6 "Ngày lập báo cáo: 2026/11/27" vs real work date 2026/11/11 (README:27, estimate.md:4). Label as "ngày giả lập".
- progress-report.md:14 "migration trễ 2 ngày": 40h vs 20h = 20h extra = ~3.3 focus days at 6h/day; line 71 says "40h" while #4 is still In Progress at 35/40h. Say "trễ khoảng 3 ngày" or "vượt 20h".
- estimate.md:36-38: S (4.4h) and M (8.04h) averages exceed their own ceilings; text only says "sát trần/đúng bằng". Mention so that "78% of ceiling" is not read as every size under ceiling.
- estimate.md omits the skill's uncertainty band (978–1020 SWP, HTML summary); one line would help.
- README §3 root table omits `.claude/` (untracked, empty) and `.git/`; fine for GitHub, mention only if grader lists local dir.
- task-breakdown.md §2: many rows end with "—" in last column (lines 47,51,54,57,58,60,66,68,70-73). Replace with "Không còn phần nào" so the cell is not read as missing.
- AI-report.md:3 "Claude Opus", "VS Code", :72 "~750 nghìn token", :52 "câu neo P2-11" are not verifiable from the repo; keep only if true, drop "P2-11" (reader cannot resolve it).
- AI-report.md:16 "Quy giờ" row has no prompt text, only a description; assignment asks prompt per job. Add the actual prompt sentence.
- Date format mixes 2026-11-08 (PREMISE.md:3) and 2026/11/08 (README:8).

## Unsupported / overstated claims list (file:line)
- README.md:30 (unchecked incognito) — see W1.
- progress-report.md:6 "Số liệu đọc lại từ Project" — true (I verified), but day-27 date is simulated.
- progress-report.md:16, :80, :94, estimate.md:46, :97 — measured speed is simulation input (W2).
- estimate.md:96 "2–5 lần" (W6); estimate.md:27 (W7).
- README.md:13 / task-breakdown.md:78 / estimate.md:83 / PREMISE.md:50 "mỗi rule một sub-issue" (W3).
- task-breakdown.md:104 (W4).
- estimate.md:70 LAB-1 "gồm buffer 20%, giảm 15% nhờ AI", MD figures: cannot verify, LAB-1 file not in repo (unresolved).
- AI-report.md:72 token count (unverifiable).

## Copied RFP / PII
No RFP text found; README:9 states RFP is not copied; names appear as fictional (YCL-RFP-2026-01, "Yuki Cold Logistics"). No emails, phones, tokens, local paths in tracked files. `output/breakdown/parts/_RULES.md:37` and `plans/reports/*.md` reference `lab4-product-b-design/...` relative paths (not copied content) — fine.

## Unresolved
- LAB-1 MD figures and "nhóm 0 và 21" cannot be cross-checked here.
- Whether the Project page renders publicly with fields visible (HTTP 200 only proves the shell loads).

**Status:** DONE_WITH_CONCERNS (no critical; 8 warnings to fix before submission, mainly W1 incognito note, W2 circular speed claim, W3/W4/W5 wording contradictions)
