# Trích xuất spec màn hình — Nhóm D (SCR-044, 053, 060, 061, 062, 063)

Nguồn: `lab4-product-b-design/specs/05-screens/SCR-<id>_SPEC.md` (đọc toàn bộ), đối chiếu `04-business-rules/business-rules.md`,
`03-database/database-design.md`, `02-adr/ADR-006…`, `06-common/role-permission-matrix.md`, `06-common/message-list.md`.
Quy ước cỡ: S ≤ 4h · M ≤ 8h · L ≤ 16h. Cột "[DRV]" = sub-task dính ràng buộc giờ lái 2024 (ADR-006).
Đường dẫn trích dẫn viết tắt: `044#9` = `SCR-044_SPEC.md` mục 9; `BR#br-drv` = `business-rules.md` §7.

---

## 0. Ràng buộc giờ lái xe 2024 (ADR-006) — tổng quan nhóm D

| Màn | Dính? | Ở đâu |
|---|---|---|
| SCR-044 | Không | — |
| SCR-053 | Gián tiếp | Chỉ xuất khi tuyến `published` (BR-OUT-04) — mà công bố chỉ được khi qua cổng tuân thủ (SCR-062). Không tự tính rule BR-DRV nào. |
| SCR-060 | **Có** | BR-DRV-21 tự chèn nghỉ (dùng chuỗi lái BR-DRV-11, tham số BR-DRV-12/13), 出庫前/帰庫後作業 tính vào 拘束, 1 tài xế/1 tuyến/ngày, M_635 |
| SCR-061 | **Có — lõi** | Engine BR-DRV-01..14, BR-DRV-20 (chặn công bố), 23 (bất biến + hash), 24 (loại sự cố, phần lập kế hoạch), 25 (xác nhận cảnh báo có phân loại) |
| SCR-062 | **Có** | BR-DRV-20 (cổng công bố), BR-DRV-22 (gắn rule version lúc công bố), BR-DRV-23 (tính lại hash), ghi `driver_duty_records` `route_plan` |
| SCR-063 | **Có** | BR-DRV-24 (tách báo cáo lịch thường / sự cố), BR-DRV-23 (không sửa kết quả kiểm) |

**Danh sách rule đúng như spec ghi** (BR#br-drv bảng tham số + "Hành vi"; giá trị mặc định bản `2024-04`, tất cả là tham số
`driver_rule_versions`, không viết cứng):

| Mã | Nội dung (nguyên văn spec, dịch gọn) | Mức | Nguồn |
|---|---|---|---|
| BR-DRV-01 | Tăng ca tối đa/năm 960h; năm tài chính (tháng bắt đầu tham số, mặc định 4). Tăng ca ngày = 拘束 − nghỉ giữa ca − `standard_work_day_h` 8h (INFERRED, Q&A-B06) | Vi phạm | EXTRACTED |
| BR-DRV-02 | 拘束時間/năm 3.300h | Vi phạm | EXTRACTED |
| BR-DRV-03 | 拘束時間/tháng 284h, tháng dương lịch JST | Vi phạm | EXTRACTED |
| BR-DRV-04 | Ràng buộc/ngày chuẩn 13h; "ngày" = 24h tính từ giờ bắt đầu ca | Cảnh báo | EXTRACTED |
| BR-DRV-05 | Ràng buộc/ngày tối đa 15h | Vi phạm | EXTRACTED |
| BR-DRV-06 | Số ngày 拘束 > `long_day_threshold_h` (14h)/tuần = 2; tuần bắt đầu thứ Hai; cảnh báo khi D > 14h và đã là ngày thứ 3 | Cảnh báo | INFERRED |
| BR-DRV-07 | 休息期間 mục tiêu 11h (kết thúc ca → bắt đầu ca kế) | Cảnh báo | EXTRACTED |
| BR-DRV-08 | 休息期間 tối thiểu 9h | Vi phạm | EXTRACTED |
| BR-DRV-09 | Lái TB/ngày (2 ngày) 9h: D vi phạm khi **cả** avg(D−1,D) > 9h **và** avg(D,D+1) > 9h; D+1 chưa có dữ liệu → dùng kế hoạch, chưa có kế hoạch → chỉ cảnh báo | Vi phạm | EXTRACTED |
| BR-DRV-10 | Lái TB/tuần (2 tuần) 44h: khối 2 tuần **cố định** từ `drive_2week_anchor_date`; tổng lái khối/2 > 44h | Vi phạm | EXTRACTED |
| BR-DRV-11 | Lái liên tục tối đa 4h; chuỗi chỉ ngắt bởi nghỉ ≥ 10 phút; tổng nghỉ mỗi khối 4h ≥ 30 phút | Vi phạm | EXTRACTED |
| BR-DRV-12 | Nghỉ ngắt quãng tối thiểu mỗi lần 10 phút (tham số của 11) | — | INFERRED |
| BR-DRV-13 | Nghỉ ngắt quãng tổng mỗi khối 30 phút (tham số của 11) | — | INFERRED |
| BR-DRV-14 | Gia hạn 労使協定 3.400h/năm, 310h/tháng — **tắt** (null), chỉ bật khi khách xác nhận (Q&A-B07) | — | INFERRED |
| BR-DRV-20 | Tuyến có ≥ 1 vi phạm → không công bố; hiện đúng khoảng giờ vi phạm + tham số trượt; cảnh báo không chặn nhưng phải xác nhận đã đọc | — | — |
| BR-DRV-21 | Tự chèn nghỉ 30 phút tại điểm dừng gần nhất trước mốc 4h lái liên tục; hiện trên timeline + lịch trình tài xế | — | 30 phút INFERRED |
| BR-DRV-22 | Tuyến gắn phiên bản quy tắc hiệu lực lúc công bố; bản mới không áp ngược | — | — |
| BR-DRV-23 | Kết quả kiểm bất biến, gắn `route_version_id` + `driver_rule_version_id` + hash đầu vào; chạy lại tạo bản ghi mới | — | — |
| BR-DRV-24 | Sự cố có bằng chứng ghi ở `unforeseeable_events`, báo cáo riêng, không sửa kết quả đã tính; loại khỏi lịch thường **chỉ** BR-DRV-04/05, 09, 11; tháng/năm/nghỉ giữa ca tính đủ (Q&A-B06) | — | Phạm vi INFERRED |
| BR-DRV-25 | Slot vượt kế hoạch phải phân loại + bằng chứng + báo cáo riêng cho `transport_manager` | — | — |
| BR-TIME-02 | Khung dịch vụ 05:00–23:00 JST cho giờ phục vụ tại khách (liên quan lịch tuyến, không phải luật lao động) | Chặn lưu | EXTRACTED |

→ Đề xuất 1 sub-task BE cho mỗi rule/check (xem SCR-060 #8, SCR-061 #4–#14, SCR-062 #1, SCR-063 #6), kèm unit test theo ví dụ ở `061#logic-9` và biên ADR-006 §5 (4h00 đạt, 4h01 vi phạm, nghỉ 9 phút không tính, 3×10 phút = reset).

---

## SCR-044 — 日付逆転例外承認 (Duyệt ngoại lệ đảo ngày)

**1. Mục đích / role.** `sales_manager` duyệt/từ chối yêu cầu ngoại lệ 日付逆転 do `sales_planner` gửi ở SCR-042; duyệt → hệ thống kiểm lại rule 1–4 + SL rồi tự phân bổ. Route `/approvals/date-reversal`. Ghi: `sales_manager`; chỉ xem: `sales_planner`, `quality`, `auditor`; còn lại → M_20 (044#7).

**2. Khu vực.** Tab trạng thái (5 tab + đếm) · bộ lọc khách/SKU/ngày gửi · bảng yêu cầu (DRX-xxxxxx, so hạn bản chụp, badge 本日期限) · panel chi tiết (so hạn, lý do, bằng chứng khách đồng ý, đánh giá lại hiện tại 8.4, nhận xét, 承認/却下, timeline lịch sử) · dialog xác nhận duyệt · banner kết quả.

**3. Dữ liệu.**
- Bảng đọc: `date_reversal_exception_requests`, `order_lines`, `orders`, `customers`, `skus`, `lots`, `profiles`, `delivery_history`, `audit_log`.
- Bảng ghi (khi duyệt): `allocations` (`exception_request_id`, `allocation_evidence`), `inventory_movements` (`allocate`), `lots.qty_allocated`, `order_lines`/`orders` status, yêu cầu, `audit_log`, `exception_events` (rule 1 trượt).
- RPC: `approve_date_reversal_request`, `reject_date_reversal_request`, `expire_date_reversal_requests` (pg_cron 00:05 JST, lô 500), dùng chung `evaluate_lot_for_line`, `last_delivered_expiry()`.
- API: GET list, GET detail, GET evidence (signed URL 5 phút, bucket `consent-evidence`), POST approve, POST reject (044#9).
- BR: BR-DATE-01/02, BR-ALLOC-ORDER, BR-DELWIN-01, BR-EXP-02, BR-INV-02, BR-ORD-03. ADR-005 (+ ADR-002 multi-step RPC).

**4. Validation / trạng thái / luồng.**
- State machine `pending → approved | rejected | expired` (044#8). Duyệt mà kiểm lại trượt → commit `expired` + HTTP 200 `result:'expired'` (không phải lỗi).
- `expire_reason`: `RULE_FAILED:<code>`, `PREVIOUS_CHANGED`, `QTY_INSUFFICIENT`, `ORDER_CANCELLED`, `REQUESTED_DATE_PASSED`, `ORDER_NOT_ALLOCATABLE`.
- Người duyệt ≠ người gửi (M_448, CHECK `decided_by <> requested_by`). Khóa: yêu cầu → `orders` → `order_lines` → `lots`. Xử lý trùng → M_450.
- Từ chối: nhận xét bắt buộc 10–500 (M_06), xác nhận M_454. Duyệt: nhận xét tùy chọn ≤ 500.
- Tab 申請中 bỏ qua lọc ngày (INFERRED). Loading/Empty(M_32)/Error(M_40/41/21/23).

**5. Giờ lái 2024:** Không.

**6. Sub-task.**
1. [BE] Migration `date_reversal_exception_requests` (cột `requested_at`, `decided_at`, `expire_reason`, `previous_delivery_history_id`, `allocation_id`, `is_legacy`; CHECK; UNIQUE partial pending) + chuyển dữ liệu `date_reversal_overrides` → legacy — M
2. [BE] RBAC: vai trò `sales_manager`, permission `date_reversal:approve/request` trong `role-permissions.ts` + RLS SELECT cho 4 vai trò — S
3. [BE] RPC `approve_date_reversal_request` (lock order, 6 nhánh expire, tự phân bổ, `exception_events`, audit) — L
4. [BE] RPC `reject_date_reversal_request` — S
5. [BE] Job pg_cron `expire_date_reversal_requests()` 00:05 JST, lô 500 — S
6. [BE] API GET list (zod, counts theo tab, sort theo tab, paging 50) — M
7. [BE] API GET detail + `recheck` (gọi `evaluate_lot_for_line`, SL, `currentPreviousExpiry`) + `history` từ `audit_log` — M
8. [Infra] Bucket riêng tư `consent-evidence` + storage policy — S
9. [BE] API GET evidence (302 signed URL 5 phút, ghi `audit_log` `evidence_viewed`) — S
10. [BE] API POST approve/reject: map 409 `SELF_DECISION`/`ALREADY_DECIDED`, 403 → M_xx — S
11. [FE] Trang danh sách: tab + đếm, bộ lọc (M_13), query string, sort, paging, badge 本日期限 — M
12. [FE] Panel chi tiết 8.1–8.3 + timeline 8.8 + link bằng chứng — M
13. [FE] Khối 8.4 kiểm lại + nút 承認/却下 theo quyền/trạng thái, dialog 9, M_454, banner kết quả 10, xử lý M_450 reload — M
14. [FE] Mục menu 「日付逆転承認」, guard route, deep-link `?id=` / `?orderId=` — S
15. [QA] Test case: state machine, tự duyệt, 6 lý do expire, RBAC 4 nhóm vai trò, xem bằng chứng ghi audit — M
16. [QA] Chạy test + test đồng thời (2 manager duyệt cùng lúc; duyệt song song `allocate_lot` / `cancel_order`) — M
17. [BrSE] Làm rõ gap #1–#4 dưới — S

**7. Gap / mâu thuẫn.**
| # | Trích | Mô tả | Đề xuất |
|---|---|---|---|
| 1 | 044#logic-8-4 (8.4-2) | Re-check có ✕ vẫn cho bấm 承認 (để ghi `expired`) — INFERRED, phương án khác là disable | Issue làm rõ (BrSE); tạm theo spec |
| 2 | 044#logic-8-6 (8.6-3) vs BR#BR-DATE-02 | Spec màn ghi `PREVIOUS_CHANGED` là INFERRED; BR-DATE-02 ghi rõ là lý do hết hạn **và** job 00:05 cũng phải bắt. Job ở 044#8/#9 dòng 6 chỉ expire theo `requested_date` | Sửa thiết kế: job thêm kiểm `last_delivered_expiry()` ≠ snapshot |
| 3 | 044#logic-10 (10-2), 044#10 dòng 7 | Thông báo cho người gửi khi có kết quả chưa thiết kế | Issue làm rõ; tạm ngoài phạm vi |
| 4 | 044#logic-5, 044#logic-8-3 | Mặc định lọc −30 ngày, URL ký 5 phút, audit `evidence_viewed` đều INFERRED | Giả định, ghi Q&A |
| 5 | 044#3 | Thẻ 「承認待ち」 ở SCR-002 "ngoài phạm vi spec" | Ghi chú cross-screen, không tạo task ở đây |

---

## SCR-053 — 出荷前チェック (Kiểm hàng trước khi xuất)

**1. Mục đích / role.** Kiểm từng dòng phân bổ (quét/nhập tay có kiểm soát mã lô, đếm), quét xe, niêm phong, nhiệt độ xe + hàng rồi 出荷確定 cho đơn thuộc tuyến `published`. Ghi: `warehouse`, `warehouse_lead`, `admin` (`outbound:write`); chỉ xem: `sales_planner`, `sales_manager`, `dispatcher`, `transport_manager`, `quality`, `auditor` (053#7).

**2. Khu vực.** Trang `/outbound`: tab 出荷待ち/出荷済み, lọc ngày xuất + tuyến (gồm 「ルート未割当」), bảng chờ xuất (tuyến/xe/tài xế, nút 検品開始), bảng đã xuất. Trang `/outbound/[orderId]`: header đơn, thông tin tuyến (bản, xe, tài xế, giờ xuất phát), bảng kiểm dòng (SKU, vùng nhiệt, lô, hạn, SL, cách nhập, mã lô đọc, SL đếm, kiểm lại đảo ngày, kết quả đối chiếu), lý do nhập tay, khung 積込確認 (mã xe, niêm phong, nhiệt độ xe, nhiệt độ hàng, ngưỡng áp dụng), cảnh báo nhiệt, nút xác nhận + dialog, khung bị chặn, bản ghi đã xuất, ghi chú chỉ xem.

**3. Dữ liệu.**
- Đọc: `orders`, `order_lines`, `allocations`, `lots`, `skus`, `temp_zones`, `customers`, `route_stops`, `route_versions`, `routes`, `vehicles`, `drivers`, `shipments`, `shipment_checks`, `temp_zone_policy_versions`, `date_reversal_exception_requests`, `delivery_history`.
- Ghi (RPC): `shipments`, `shipment_checks`, `delivery_history`, `inventory_movements` (`ship`), `lots` (+ `depleted`, `lot_status_events`), `orders.status='shipped'`, `deviations` (cả khi bị chặn), `exception_events` (cả khi bị chặn), `idempotency_keys`, `audit_log`.
- RPC/hàm: `confirm_shipment(7 tham số)` (thay bản 3 tham số), `effective_temp_policy(zone,date)` (mới, dùng chung SCR-022), `last_delivered_expiry()`, `is_date_reversal()`, `app_today()`, view `outbound_check_lines_view`.
- API: GET `/api/shipments/pending-and-done`, GET `/api/orders/[id]/outbound-check`, POST `/api/shipments` (header `Idempotency-Key`).
- BR: BR-OUT-01..04, BR-TEMP-01, BR-TEMP-02 C/D, BR-EXP-01/02, BR-DATE-01/02, BR-INV-01/02. ADR-002, 003, 007, 008.
- DB thay đổi đề xuất: `shipment_checks.input_method/manual_reason/scanned_sku_code`, `deviations.measure_type/order_id` (đã có trong ERD database-design).

**4. Validation / trạng thái / luồng.**
- 10 kiểm tra a–j (053#3): a tuyến published (M_465/466); b mã xe + vùng xe = vùng SKU (M_472/473); c lô/SKU khớp (M_469/487/471); d SL đếm = SL phân bổ (M_470); e lô cách ly (M_474); f 消費期限 ≤ hôm nay chặn cứng + `exception_events` (M_475); g 賞味期限 quá → chỉ cảnh báo (M_476); h đảo ngày lúc xuất, chỉ qua nếu ngoại lệ `approved` (M_477/478); i nhiệt xe **và** hàng trong ngưỡng phiên bản hiệu lực, bằng biên = đạt, mỗi giá trị ngoài ngưỡng = 1 deviation (M_406); j `Format_Seal` (M_01/M_13).
- Server gom **mọi** lỗi, không raise → 409 `OUTBOUND_BLOCKED` vẫn commit deviation/exception event.
- Nút xác nhận enable khi đủ trường (không đòi mọi dòng 一致). Idempotency-Key sinh 1 lần/lần mở dialog.
- Ma trận trạng thái đơn × tuyến × vai trò (053#8). Version tuyến đổi sau khi mở trang → M_22. Rời trang có dữ liệu → M_31.
- Phím: quét (Enter) → nhảy ô SL; cấm paste khi `scan` (INFERRED). "Hôm nay" luôn từ server.

**5. Giờ lái 2024:** Không trực tiếp. Gián tiếp: điều kiện BR-OUT-04 (tuyến `published`) chỉ đạt sau cổng tuân thủ SCR-061/062. Hiển thị tài xế + giờ xuất phát dự kiến (053#logic-10-3/10-4). Không có rule BR-DRV nào kiểm ở màn này.

**6. Sub-task.**
1. [BE] Migration: `shipments` (+`cargo_temp_c`, `seal_no`, `route_version_id`, `policy_version_id`), `shipment_checks` (+3 cột), `deviations` (+`measure_type`, `order_id`), `idempotency_keys` (nếu chưa có) — M
2. [BE] Hàm `effective_temp_policy(p_zone, p_date)` + test biên (bằng biên = đạt, 冷凍 không cận dưới) — S
3. [BE] View `outbound_check_lines_view` (security_invoker) tính consumption/best-before/date-reversal/exception — M
4. [BE] RPC `confirm_shipment` phần 1: role, idempotency, khóa đơn, kiểm tuyến + version, khóa lô theo id (bước 1–5) — M
5. [BE] RPC `confirm_shipment` phần 2: gom problems b–j, INSERT `deviations`/`exception_events`, trả blocked không raise — L
6. [BE] RPC `confirm_shipment` phần 3: ghi `shipments`, `shipment_checks`, `delivery_history` (thứ tự expiry, id), `inventory_movements ship`, `depleted` + `lot_status_events`, `orders.shipped`, audit — L
7. [BE] API GET pending-and-done (route/vehicle/driver, `canStartCheck`, `blockReason`, lọc ngày/tuyến/unassigned) — M
8. [BE] API GET outbound-check (DTO mở rộng: route, policy, dateReversal, shipment.checks) — M
9. [BE] API POST `/api/shipments` (zod, header bắt buộc, map 409/400/403 → M_xx) — M
10. [BE] RBAC: thêm `warehouse_lead` vào `outbound:write` + kiểm `has_role` trong RPC — S
11. [FE] Trang `/outbound`: tab + đếm, bộ lọc, 2 bảng, sort, nút 検品開始 + tooltip M_465/M_466 — M
12. [FE] Trang kiểm: header, khung tuyến, render theo ma trận trạng thái 053#8, ghi chú chỉ xem M_484 — M
13. [FE] Bảng kiểm dòng: radio scan/manual, tách mã vạch `{sku}|{lot}` (M_486), cấm paste, điều hướng phím, badge đối chiếu/hạn/cách ly/đảo ngày, lý do nhập tay — L
14. [FE] Khung 積込確認: mã xe (M_472 client), niêm phong, 2 nhiệt độ, nhãn ngưỡng, cảnh báo M_479, M_483/M_473 ẩn nút — M
15. [FE] Luồng xác nhận: enable logic, dialog M_482 + M_488, Idempotency-Key, xử lý 201/409 blocked (khung 17 map `allocationId`/`field`)/409 trạng thái/403/401/500/mạng; khung 18 đã xuất; guard M_31 — L
16. [QA] Test case kiểm a–j (biên nhiệt độ, 消費期限 = hôm nay, 賞味期限 hôm qua), nhập tay có/không lý do — M
17. [QA] Test case idempotency (bấm 2 lần, mạng chập chờn), deviation vẫn lưu khi bị chặn (xe + hàng → 2 deviation), xung đột version tuyến M_22 — M
18. [QA] Chạy test trên thiết bị máy quét giả lập bàn phím + quyền 2 nhóm vai trò — M
19. [BrSE] Làm rõ gap #1, #3, #4, #5, #7 — S

**7. Gap / mâu thuẫn.**
| # | Trích | Mô tả | Đề xuất |
|---|---|---|---|
| 1 | 053#3 (quyết định to-be (h)) | Kiểm lại 日付逆転 lúc xuất là INFERRED, đề xuất Q&A | Issue làm rõ (BrSE); tạm làm theo spec (Must ở 053#10 dòng 7) |
| 2 | 053#logic-10-4 vs 060#logic-6-5 | SCR-053: giờ xuất phát = `planned_arrival` depot đầu. SCR-060: `planned_arrival` depot đầu = **始業**, 出庫 = `planned_arrival + service_min` → SCR-053 hiển thị sai giờ | Sửa thiết kế SCR-053: dùng `planned_arrival + service_min` |
| 3 | 053#9 RPC bước 4 vs 062#logic-12 | Đổi sau công bố → `routes.status='created'`, `current_version` = bản nháp; RPC xuất đòi `routes.status='published'` và đơn nằm ở **bản mới nhất** → trong lúc đổi tuyến, kho **không xuất được** dù tài xế vẫn chạy bản công bố cũ | Issue làm rõ + sửa thiết kế: kiểm theo bản `published` mới nhất thay vì `current_version` / `routes.status` |
| 4 | 053#logic-11-6 | Định dạng mã vạch `{sku_code}|{lot_code}` INFERRED (RFP chưa có) | Issue làm rõ — ảnh hưởng FE parser |
| 5 | 053#logic-12, 053#logic-13-4, 053#logic-13-2 | Danh sách lý do nhập tay; nhiệt độ hàng 1 giá trị/đơn; không kiểm trùng niêm phong — đều INFERRED | Giả định, ghi Q&A |
| 6 | 053#9 RPC bước 6h | Phân bổ có ngoại lệ `approved` luôn qua, kể cả khi mốc giao đổi tiếp sau lúc duyệt (snapshot `previous_expiry` không được so lại) | Issue làm rõ (BrSE + sales) |
| 7 | 053#logic-5 (5-2, 5-3), 053#logic-5-8 (5.8-3) | Hiện đơn chưa gán tuyến; sort `seq` giảm dần; chặn khi tuyến `in_progress` — INFERRED | Giả định |
| 8 | 053#logic-5-4 vs 060#logic-6-8 | Màu badge 「チェック済」 vàng (053) vs xanh dương (060) | Sửa thiết kế: thống nhất `Status_Badge` ở common |
| 9 | 053#logic-17 (17-2) | Link sang màn deviation F08 "giai đoạn sau" | Ghi chú phụ thuộc |

---

## SCR-060 — ルート計画 (Lập tuyến)

**1. Mục đích / role.** Dispatcher lập tuyến cho 1 ngày phục vụ: gán đơn đã phân bổ vào tuyến (xe + tài xế), sắp điểm dừng, chỉnh service time, thêm nghỉ; hệ thống dựng segment từ IF-MAP-01 và tự chèn nghỉ BR-DRV-21. **Không** phán định luật (chỉ span tham khảo). Ghi: `dispatcher`, `transport_manager`; xem: `auditor` (060#7).

**2. Khu vực.** Chọn ngày (URL `?date=`) · badge dịch vụ bản đồ · bảng đơn chưa gán + lý do · nút gán · bảng tuyến (xe, vùng, tài xế, 出庫, tải %, 計画拘束, trạng thái) · dialog 新規ルート · bảng thứ tự điểm dừng (seq, loại, điểm, phút di chuyển, nguồn, giờ đến, service, khớp khung giờ khách, ↑↓/外す) · dialog thêm điểm nghỉ · nút lấy lại thời gian di chuyển / 保存 / 拘束時間チェック · dialog nhập tay thời gian di chuyển.

**3. Dữ liệu.**
- Bảng: `vehicles`, `drivers`, `routes` (+`updated_at`, `current_version`), `route_versions`, `route_stops` (+`travel_min/source/fetched_at/manual_reason`, `place_name`), `route_segments` (`auto_inserted`), `orders`, `order_lines`, `skus`, `customers` (+`delivery_window_*`, `default_service_min`), `route_assignment_rejections` (mới), `travel_time_cache` (mới), `driver_rule_versions`, `audit_log`.
- RPC: `get_route_plan(p_date)`, `create_route(...)`, `assign_orders_to_route(...)`, `save_route_stops(...)`, `build_route_segments(route_version_id)`.
- API: GET `/api/routes/plan`, POST `/api/routes`, POST `/api/routes/{id}/assign`, PUT `/api/routes/{id}/stops`, POST `/api/routes/{id}/travel-times/refresh`.
- Tích hợp: IF-MAP-01 (batch, timeout 10s, cache 7 ngày, > 24h không công bố).
- BR: BR-TIME-02, BR-TEMP-02 D, BR-DRV-21 (+ BR-DRV-11/12), BR-DRV-23 (checked → created), BR-ORD-01, sm-route, sm-order. ADR-006.

**4. Validation / trạng thái / luồng.**
- Lý do không gán theo thứ tự: `NOT_ALLOCATED`(M_610) · `MIXED_TEMP_ZONE`(M_611) tĩnh; `NO_VEHICLE_ZONE`(M_612) · `TEMP_ZONE_MISMATCH`(M_604) · `CAPACITY_EXCEEDED`(M_613) · `SERVICE_HOURS`(M_614) động, 4–6 lưu bền.
- Ngày < hôm nay → M_618. Xe/tài xế trùng ngày → M_603/M_605 (unique partial index). Gán đơn đã ở tuyến khác → M_602.
- Tuyến `checked` sửa → hỏi M_606 → về `created`. `published` trở lên → chỉ đọc + M_607.
- Sửa item 8/9/13 là nháp tới khi 保存 (khóa lạc quan M_22, `beforeunload`). Ngoài 05:00–23:00 sau khi dời giờ → rollback M_614. Ngoài khung khách → chỉ cảnh báo M_615.
- Validate: pre/post 0–120, service giao 5–180, nghỉ 10–180, travel nhập tay 1–720 + căn cứ 10–500 (M_06).
- Bản đồ: 正常 / キャッシュ使用中 (M_621) / 障害 (M_620, nhập tay). Ghi đè đoạn manual phải hỏi M_31.

**5. Giờ lái 2024: Có.**
- BR-DRV-21 tự chèn nghỉ 30 phút khi tổng lái chuỗi sắp vượt `continuous_drive_max_h` 4h, chèn ngay sau phục vụ tại điểm dừng gần nhất trước mốc 4h, lặp tới hết, M_616 (060#logic-11 bước 4).
- Không có điểm dừng trong chuỗi → không chèn, M_617, vi phạm hiện ở SCR-061 (bước 5).
- Tham số từ `driver_rule_versions` hiệu lực hôm nay; không có → M_635, vẫn lưu, không chèn (bước 6).
- Điểm nghỉ tay ≥ 10 phút vì < 10 phút không tính là nghỉ (BR-DRV-12) (060#logic-9-3).
- 出庫前作業 / 帰庫後作業 tính vào 拘束 (060#logic-7-4/7-5); 6.7 計画拘束 chỉ tham khảo, không tô màu 13h/15h (PP-04).
- 1 tài xế tối đa 1 tuyến/ngày (M_605, INFERRED) — ảnh hưởng cách engine SCR-061 gộp ca.

**6. Sub-task.**
1. [BE] Migration nhóm F07 lõi: `vehicles`, `drivers`, `routes`, `route_versions`, `route_stops`, `route_segments` + cột bổ sung + unique partial (ngày, xe)/(ngày, tài xế) — L
2. [BE] Migration: `route_assignment_rejections`, `travel_time_cache`, `customers` cột khung giờ/service, enum `orders.status` thêm `routed/partially_allocated/cancelled` — M
3. [BE] RBAC: vai trò `dispatcher`, `transport_manager`, `auditor` + `route:write`; RLS chỉ SELECT trên 4 bảng tuyến, ghi qua security definer — M
4. [BE] RPC `get_route_plan(p_date)`: đơn chưa gán, lý do 1–3 tính, 4–6 đọc bảng, mapStatus — M
5. [BE] RPC `create_route` + API POST `/api/routes` (Idempotency-Key, 2 depot stop, segment 出庫前/帰庫後) — M
6. [BE] RPC `assign_orders_to_route`: kiểm từng đơn theo thứ tự 1→6 + M_602, lưu rejections, `routed`, confirm M_606 — L
7. [BE] Dựng segment `build_route_segments` (drive/wait/service/break, depot pre/post, giờ đến) — M
8. [BE][DRV] BR-DRV-21 tự chèn nghỉ: dùng chung thuật toán chuỗi lái BR-DRV-11 (tham số 11/12/13 từ rule version), M_616/M_617/M_635 — L
9. [BE] RPC `save_route_stops`: khóa lạc quan, ghi stops, gọi map cho đoạn chờ lấy, dựng segment, chèn nghỉ, kiểm BR-TIME-02 rollback, checked→created, audit — L
10. [BE] Adapter IF-MAP-01: batch, timeout 10s, cache key (from, to, slot 1h), fallback cache → lỗi, đếm M_623 — L
11. [BE] API POST travel-times/refresh (không ghi đè manual nếu chưa confirm, audit giá trị cũ) — M
12. [Infra] Cấu hình IF-MAP-01 (API key qua secret, env, egress) — S
13. [FE] Khung trang: chọn ngày (URL, chặn quá khứ, guard nháp M_31), badge bản đồ — S
14. [FE] Bảng đơn chưa gán: badge lý do + tooltip, rule chọn (disable lý do tĩnh), nút gán + M_606 + M_609 — M
15. [FE] Bảng tuyến + dialog 新規ルート (option xe/tài xế đã dùng disable, giờ bước 5 phút, 始業 hiển thị) — M
16. [FE] Bảng điểm dừng dạng nháp: ↑↓/外す, service time, badge khung giờ khách/サービス時間外/自動 BR-DRV-21, dòng tổng, `beforeunload` — L
17. [FE] Dialog thêm điểm nghỉ + dialog nhập tay thời gian di chuyển (banner M_620) — M
18. [FE] Nút 保存 / 再取得 / 拘束時間チェック (lưu nháp rồi chuyển SCR-061), chế độ chỉ đọc `published`/`auditor` — M
19. [QA] Test case gán đơn: 6 lý do, biên 05:00/23:00, tải 90%/100%, đồng thời M_602/M_603/M_605 — M
20. [QA][DRV] Test case BR-DRV-21: chuỗi 4h00 (không chèn) / 4h01 (chèn), không có điểm dừng → M_617, nghỉ tay < 10 phút bị chặn, thiếu rule version M_635 — M
21. [QA] Test case bản đồ: timeout, cache, nhập tay, > 24h, ghi đè manual — M
22. [QA] Chạy toàn bộ test SCR-060 — M
23. [BrSE] Làm rõ gap #1–#7 — S

**7. Gap / mâu thuẫn.**
| # | Trích | Mô tả | Đề xuất |
|---|---|---|---|
| 1 | 060#logic-6-4 | 1 tài xế 1 tuyến/ngày INFERRED; nếu chạy 2 chuyến/ngày thì engine SCR-061 phải gộp ca | Issue làm rõ — ảnh hưởng lớn tới engine |
| 2 | 060#logic-11 bước 4 vs ADR-006 §3 bước 2 | ADR đặt việc chèn nghỉ **trong engine kiểm** (TS); SCR-060 đặt ở `build_route_segments` (SQL) khi lưu; SCR-061 không chèn. Nguy cơ 2 bản cài đặt chuỗi lái BR-DRV-11 (SQL + TS) lệch nhau | Sửa thiết kế: 1 module TS cho chuỗi lái, dùng cho cả chèn nghỉ và kiểm; RPC chỉ lưu kết quả |
| 3 | 060#logic-3 (3-2), 060#logic-13 (13-2) | Timeout 10s, cách hiểu "ước lượng > 24h", đoạn nhập tay miễn luật 24h — INFERRED | Issue làm rõ |
| 4 | 060#logic-2, 060#logic-4 (4-1), 060#logic-4-6 | Mặc định ngày mai; ngày phục vụ = `requested_date`; đơn vị qty = thùng (Q&A-B17) — INFERRED | Giả định, ghi Q&A |
| 5 | 060#logic-4-7 | Thứ tự lý do + `MIXED_TEMP_ZONE` INFERRED; đơn nhiều vùng phải tách ở bán hàng — không có luồng tách đơn | Issue làm rõ (BrSE) |
| 6 | 060#logic-5 (5-3), 060#logic-7-3 (7.3-2) | `default_service_min` 20 phút; giờ xuất phát không ràng buộc 05:00–23:00 — INFERRED | Giả định |
| 7 | database-design §ERD `route_segments.segment_type` "drive|service|wait|break|rest" | Có cả `break` và `rest`; spec chỉ dùng `break` cho segment, `rest` cho `stop_type` | Sửa thiết kế DB: bỏ `rest` khỏi `segment_type` hoặc định nghĩa |
| 8 | 060#logic-11 bước 6 | Rule version lấy theo **hôm nay**, không theo `service_date` (khớp BR-DRV-22) — nhưng tuyến lập trước ngày đổi luật sẽ dùng bản cũ | Ghi rủi ro, BrSE xác nhận |

---

## SCR-061 — ルートタイムライン・違反確認 (Timeline & vi phạm)

**1. Mục đích / role.** Dựng Gantt timeline tài xế cho 1 version tuyến (kèm D−1/D+1), chạy engine kiểm giờ làm theo `driver_rule_versions` hiệu lực, tô đúng khoảng vi phạm, xác nhận cảnh báo, mở cổng sang công bố. Ghi: `dispatcher`, `transport_manager`; xem (cả lần kiểm cũ): `auditor` (061#7).

**2. Khu vực.** Header tuyến · badge trạng thái · phiên bản quy tắc (link SCR-016) · nút チェック実行 · chọn lần kiểm (gồm cũ) + hash · Gantt (trục giờ 04–23, segment, nghỉ tự chèn, dải vi phạm/cảnh báo, dải 4h đỏ đậm, dải 休息 vắt 2 hàng, overlay sự cố, chú giải 8 ký hiệu) · bảng phát hiện (rule, mức, khoảng giờ, giới hạn, giá trị, chênh, diễn giải, gợi ý sửa, xác nhận) · bảng phán định theo rule + lũy kế · link về lập tuyến / ghi sự cố · nút 公開へ進む.

**3. Dữ liệu.**
- Bảng: `route_segments`, `route_stops`, `route_versions`, `routes`, `driver_duty_records` (thực tế `actual_manual/actual_app` + `route_plan` tuyến khác đã công bố), `driver_rule_versions` (+`long_day_threshold_h`, `drive_2week_anchor_date`), `compliance_check_results`, `compliance_violations` (+`detail` jsonb), `compliance_warning_acks` (mới), `unforeseeable_events` (overlay), `audit_log`.
- Engine TS thuần `src/lib/compliance/*` (ADR-006 phương án A) + RPC `save_compliance_check(p_route_version_id, p_rule_version_id, p_input_hash, p_findings)`, `ack_compliance_warning(...)`, `get_route_timeline(...)`.
- API: GET `/api/routes/{id}/timeline`, POST `/api/routes/{id}/compliance-checks`, POST `/api/compliance-violations/{id}/acks`, GET `/api/compliance-reports/over-plan` (view `over_plan_acks_view`).
- BR: BR-DRV-01..14, 20..25. ADR-006.

**4. Validation / trạng thái / luồng.**
- Chạy kiểm khi tuyến `created/checked`, version hiện hành chưa công bố; thiếu tài xế M_637, thiếu điểm giao M_608, không rule version M_635, version đã công bố M_607.
- Kết quả bất biến (INSERT only, trigger chặn UPDATE/DELETE). 0 vi phạm → `checked`; có vi phạm khi đang `checked` → `created`.
- `input_hash` = SHA-256 JSON chuẩn hóa {segments, id + giá trị duty records, rule version id}. Hash lệch → M_634; rule version đổi → M_633.
- Xác nhận cảnh báo: chỉ `warning`; bắt buộc 区分 (6 giá trị, M_639) + 根拠メモ 10–500 (M_06); bất biến; không chuyển sang lần kiểm mới (INFERRED).
- Cổng 公開へ進む: `checked` + lần kiểm mới nhất + 0 vi phạm + mọi cảnh báo đã xác nhận + hash khớp + rule version còn hiệu lực (M_631/632/634/633).
- Hiển thị: thời lượng cắt xuống phút, so sánh bằng giây.

**5. Giờ lái 2024: Có — màn lõi.** Rule và cách tính đúng như 061#logic-9 (bảng) — đã liệt kê ở §0. Điểm riêng của màn:
- Nguồn dữ liệu mỗi ngày: thực tế nếu có, không thì kế hoạch đã công bố (bản mới nhất) của tuyến khác; bỏ bản ghi của chính tuyến; ngày đã qua không có dữ liệu = 0h + M_636 (INFERRED); D+1 chưa có → không coi 0h (061#logic-5 bước 2.2).
- Phạm vi dữ liệu: đầu năm tài chính → `service_date + 14 ngày`.
- Window từng rule (061#logic-9): 01 từ lúc lũy kế vượt hạn ("đồng hồ làm việc" trừ break) → 終業; 02/03 `始業 + (hạn − lũy kế)` → 終業; 04 `[始業+13h, 終業]`, 05 `[始業+15h, 終業]` + chồng ngày D−1; 06 `[始業+14h, 終業]`; 07/08 chính khoảng nghỉ; 09/10 [đầu lái đầu tiên, cuối lái cuối] của D; 11 [đầu chuỗi, cuối chuỗi] + đỏ đậm từ lúc chạm 4h.
- `wait` (荷待ち) và `service` không phải nghỉ, không cắt chuỗi lái (061#logic-7-2).
- BR-DRV-24 trong kiểm lập kế hoạch chỉ ảnh hưởng BR-DRV-09 (trừ giờ lái D−1 chồng sự cố approved, tối đa `drive_h` — INFERRED) (061#logic-9 mục 4).
- BR-DRV-25: xác nhận cảnh báo có phân loại → báo cáo over-plan cho `transport_manager`.

**6. Sub-task (1 sub-task/rule như yêu cầu; mỗi task BE engine kèm unit test theo ví dụ 061#logic-9).**
1. [BE][DRV] Khung engine `src/lib/compliance/`: types, model finding (rule_code, severity, window, limit, actual, detail), nạp rule version, đơn vị giây — M
2. [BE][DRV] Bộ lắp dữ liệu đầu vào: chọn nguồn theo ngày (thực tế > kế hoạch công bố mới nhất, loại tuyến này), phạm vi FY → D+14, ngày trống = 0h + M_636 — M
3. [BE][DRV] Hàm `input_hash` (JSON chuẩn hóa, SHA-256) — dùng chung với `publish_route` — S
4. [BE][DRV] BR-DRV-01 tăng ca/năm 960h + window "đồng hồ làm việc" — M
5. [BE][DRV] BR-DRV-02 拘束/năm 3.300h + window — S
6. [BE][DRV] BR-DRV-03 拘束/tháng 284h + window — S
7. [BE][DRV] BR-DRV-04/05 拘束/ngày 13h cảnh báo / 15h vi phạm, ngày = 24h từ 始業, tính chồng sang D−1 — M
8. [BE][DRV] BR-DRV-06 số ngày > 14h/tuần (thứ Hai–CN, ngày thứ 3) cảnh báo — S
9. [BE][DRV] BR-DRV-07/08 休息 11h cảnh báo / 9h vi phạm, nghỉ trước và sau ca, 1 dòng/khoảng nghỉ — S
10. [BE][DRV] BR-DRV-09 lái TB 2 ngày 9h (cả avg1 và avg2; D+1 theo kế hoạch; chưa có → cảnh báo) — M
11. [BE][DRV] BR-DRV-10 lái TB 2 tuần 44h, khối cố định từ `drive_2week_anchor_date` — S
12. [BE][DRV] BR-DRV-11 lái liên tục 4h với tham số BR-DRV-12 (10 phút) / BR-DRV-13 (30 phút), wait/service không cắt chuỗi, mốc chạm 4h — M
13. [BE][DRV] BR-DRV-14 công tắc gia hạn (null = tắt → 3.300h/284h; khác null → thay hạn 02/03) — S
14. [BE][DRV] BR-DRV-24 phần lập kế hoạch: trừ giờ lái D−1 chồng sự cố `approved` (tối đa `drive_h`) cho BR-DRV-09 — S
15. [BE][DRV] Migration + RPC `save_compliance_check` (khóa, INSERT result + violations, chuyển `created↔checked`, audit) + trigger bất biến 3 bảng (BR-DRV-23) — M
16. [BE][DRV] Migration `compliance_warning_acks` + RPC `ack_compliance_warning` (UNIQUE, chặn severity violation, chặn lần kiểm cũ) (BR-DRV-20/25) — S
17. [BE] API GET timeline (prev/next day, checks, acks, accumulation, events, `stale`) — M
18. [BE][DRV] API POST compliance-checks: guard M_637/M_608/M_635/M_607, gọi engine, gọi RPC — S
19. [BE][DRV] View `over_plan_acks_view` + API báo cáo over-plan (BR-DRV-25) — S
20. [FE] Header, nhãn rule version (ghi chú không áp ngược), nút chạy kiểm, chọn lần kiểm cũ (chỉ đọc), banner M_633/M_634 — M
21. [FE] Component Gantt: hàng D−1/D/D+1, màu segment, nghỉ tự chèn, dải vi phạm/cảnh báo, dải 4h đỏ đậm, dải 休息, overlay sự cố, trục + vùng ngoài khung dịch vụ, chú giải (WCAG) — L
22. [FE] Bảng phát hiện + popover gợi ý sửa + dialog xác nhận cảnh báo (区分, 根拠メモ) — M
23. [FE] Bảng phán định theo rule + lũy kế (Format_Hours / XhYYm, avg1/avg2) — S
24. [FE] Cổng 公開へ進む + lý do disable đầu tiên — S
25. [QA][DRV] Thiết kế test case theo từng rule từ ví dụ 061#logic-9 (LY2, layout 1/2) + biên ADR-006 §5 — M
26. [QA][DRV] Test case luồng: kiểm → vi phạm → sửa → kiểm lại → checked → xác nhận → mở công bố; hash lệch khi ghi thực tế mới; đổi rule version; xem lần kiểm cũ (auditor) — M
27. [QA][DRV] Chạy test với seed R-06 `routes-and-drivers.csv` — L
28. [BrSE][DRV] Làm rõ Q&A-B06 (công thức tăng ca, phạm vi loại sự cố), Q&A-B07 (労使協定), anchor date, ngày trống = 0h, xác nhận không chuyển, nhập thực tế — S
29. [PM][DRV] Lấy xác nhận pháp lý người phụ trách vận tải (OPS-LAW-01, Q&A-B06) trước khi chốt bảng BR-DRV (ADR-006 §6) — S

**7. Gap / mâu thuẫn.**
| # | Trích | Mô tả | Đề xuất |
|---|---|---|---|
| 1 | ADR-006 §5 "Hệ quả tiêu cực"; 061#logic-5 bước 2.2 | Engine cần `driver_duty_records` thực tế (`actual_manual`), nhưng không màn nào trong nhóm D (và grep chỉ thấy SCR-002 nhắc) định nghĩa **màn nhập thực tế giờ làm** | Issue làm rõ (PM/BrSE): thiếu màn/epic nhập thực tế — chặn độ đúng của 01/02/03/07/09/10 |
| 2 | ADR-006 §3 bước 1 vs 061#logic-5 bước 2.2 | ADR: "14 ngày trước + năm tài chính"; SCR-061: FY → `service_date + 14 ngày` (về phía sau) | Sửa ADR cho khớp spec màn |
| 3 | ADR-006 §3 bước 4 vs 061#logic-5 bước 2.2 | ADR: nghỉ giữa ca so với "ca trước (thực tế)"; SCR-061 dùng thực tế **hoặc** kế hoạch đã công bố | Sửa ADR |
| 4 | 061#logic-9 (BR-DRV-01), BR#br-drv "Định nghĩa dùng chung" | Công thức tăng ca INFERRED (Q&A-B06) | Issue làm rõ, chặn chốt rule 01 |
| 5 | 061#logic-9 (BR-DRV-10), database-design §3.2 | `drive_2week_anchor_date` seed 2024-04-01 INFERRED | Issue làm rõ — khách chốt ngày khởi điểm |
| 6 | 061#logic-9 (BR-DRV-14) | Điều kiện phụ 告示 (số tháng được vượt 284h…) chưa có trong BR → chưa kiểm | Giả định tắt; Q&A-B07 |
| 7 | 061#logic-5 bước 2.2 | Ngày quá khứ không dữ liệu = 0h (M_636) INFERRED — có thể làm lọt vi phạm nếu thiếu nhập | Issue làm rõ; cân nhắc cảnh báo thay vì im lặng |
| 8 | 061#logic-5 bước 3 | Xác nhận cảnh báo không chuyển sang lần kiểm mới — INFERRED | Giả định |
| 9 | 061#logic-9 mục 4 | Trừ giờ lái D−1 chồng sự cố "tối đa bằng `drive_h`" vì duty record không có segment — INFERRED | Giả định |
| 10 | 061#9 (POST compliance-checks) vs 062#logic-5 bước 3.5 | Hash tính ở TS khi kiểm, nhưng `publish_route` (SQL) phải "tính lại" → 2 cài đặt hash phải giống hệt từng byte | Sửa thiết kế: 1 hàm SQL `compute_route_input_hash()` dùng cho cả hai, hoặc publish gọi qua route handler TS |

---

## SCR-062 — ルート公開・版履歴 (Công bố & lịch sử phiên bản)

**1. Mục đích / role.** Công bố tuyến cho tài xế (gắn rule version hiệu lực), quản lý phiên bản: đổi sau công bố tạo bản mới có lý do, bỏ nháp, hủy tuyến, so sánh bản, trạng thái thông báo, KPI đổi tuyến sau công bố. Ghi: `dispatcher`, `transport_manager`; xem: `auditor` (062#7).

**2. Khu vực.** Header + badge kèm chú thích bản · dải 5 bước trạng thái · checklist trước công bố (lần kiểm mới nhất, xác nhận cảnh báo, rule version, độ mới thời gian di chuyển, số đoạn nhập tay) · nút 公開 · 公開後の変更 · ルート取消 · bảng phiên bản + chọn so sánh · bảng diff · trạng thái thông báo · KPI · dialog đổi sau công bố · nút bỏ nháp.

**3. Dữ liệu.**
- Bảng: `routes`, `route_versions` (+`status`, `change_category`, `change_reason`, `driver_rule_version_id`, `published_at/by`), `route_stops`, `route_segments`, `compliance_check_results`, `compliance_warning_acks`, `driver_rule_versions`, `driver_duty_records` (INSERT `route_plan`), `notification_outbox` (mới), `orders`, `profiles`, `drivers`, `audit_log`.
- RPC: `publish_route(p_route_id, p_check_id)`, `create_route_version`, `discard_route_draft`, `cancel_route`, `route_version_diff`, `get_route_versions`; view `route_post_publish_change_kpi`.
- API: GET versions, GET diff, POST publish, POST versions, POST discard, POST cancel, GET KPI.
- Tích hợp: IF-MAIL-01 (mail relay, **không SMS**), worker outbox (cron/edge function). F06 app tài xế đọc bản `published` mới nhất (ngoài phạm vi).
- BR: BR-DRV-20, 22, 23, BR-OUT-04, sm-route. ADR-006, ADR-002.

**4. Validation / trạng thái / luồng.**
- Publish kiểm server theo thứ tự, dừng ở lỗi đầu: `checked` (M_642) → lần kiểm mới nhất & 0 vi phạm (M_631) → cảnh báo đã xác nhận (M_632) → rule version còn hiệu lực (M_633) → hash tính lại khớp (M_634) → không đoạn map/cache > 24h (M_622). Đoạn nhập tay → M_648 (không chặn, INFERRED).
- Ghi: version → `published`, bản trước → `superseded`, `routes.published`, `driver_duty_records`, outbox (`route_published`/`route_changed`), audit.
- Đổi sau công bố: lý do 10–500 + 区分 7 giá trị → bản `draft`, `routes.created`; bản công bố không đổi (M_644/M_645). Bỏ nháp → `discarded`, khôi phục trạng thái đơn, không thông báo. Hủy: lý do bắt buộc, đơn `routed → allocated`, thông báo nếu đã công bố.
- `in_progress/completed/cancelled` → không đổi/hủy (M_646). So sánh đúng 2 bản (M_649).
- Thông báo: 送信待ち/送信済/送信失敗, retry 1/5/15/60 phút rồi mỗi 60 phút tới 24h (INFERRED), thất bại cảnh báo trên SCR-002.

**5. Giờ lái 2024: Có.**
- BR-DRV-20: không công bố khi còn vi phạm / cảnh báo chưa xác nhận (bước 2, 3).
- BR-DRV-22: gắn `driver_rule_version_id` lúc công bố, bản mới không áp ngược; rule version đổi → M_633 (bước 4).
- BR-DRV-23 / ADR-006 §3: tính lại `input_hash` (segments + duty records + rule version) phải khớp lần kiểm (bước 5).
- Ghi `driver_duty_records` `route_plan` (`shift_start/end`, `drive_h`, `break_h` từ segment) để kiểm tuyến khác của cùng tài xế (bước 8).
- Hủy tuyến: duty records của tuyến bị bỏ qua khi tính (lọc theo trạng thái tuyến) (062#logic-7).

**6. Sub-task.**
1. [BE][DRV] RPC `publish_route`: khóa, 6 kiểm tra theo thứ tự (gọi hàm hash dùng chung), publish/supersede, INSERT `driver_duty_records`, outbox, audit — L
2. [BE] RPC `create_route_version` (copy stops/segments, `draft`, `routes.created`, Idempotency-Key) + API — M
3. [BE] RPC `discard_route_draft` (khôi phục `current_version`, trạng thái đơn theo bản công bố) + API — M
4. [BE] RPC `cancel_route` (đơn `routed → allocated`, outbox nếu đã công bố) + API — M
5. [BE] Hàm `route_version_diff` (ghép theo order_id / place_name+vị trí / depot) + API — M
6. [BE] View KPI `route_post_publish_change_kpi` + API — M
7. [BE] API GET versions (prePublish, notification, kpi) — M
8. [Infra] Bảng `notification_outbox` + worker gửi mail (Supabase cron/edge function), retry, cấu hình IF-MAIL-01, cảnh báo thất bại lên SCR-002 — L
9. [FE] Header + dải trạng thái + checklist trước công bố (badge, link SCR-061) — M
10. [FE] Nút 公開 + dialog M_640 (+M_648) + xử lý lỗi 422 làm mới checklist — S
11. [FE] Bảng phiên bản + chọn so sánh (M_649) + bảng diff + danh sách đơn ảnh hưởng — M
12. [FE] Dialog 公開後の変更 (M_644, 区分, lý do, đơn ảnh hưởng), dialog hủy tuyến (M_647), nút bỏ nháp (M_31) — M
13. [FE] Khối trạng thái thông báo + KPI (目標 / 基準値, badge) — S
14. [QA][DRV] Test case cổng công bố: từng kiểm tra 1–6 riêng lẻ, rule version mới ra đời giữa kiểm và công bố, hash lệch do ghi thực tế — M
15. [QA] Test case vòng đời phiên bản (đổi → nháp → bỏ / công bố lại), hủy tuyến, thông báo thất bại + retry, auditor — M
16. [QA] Chạy test SCR-062 — M
17. [BrSE] Làm rõ gap #2, #3, #5, #6 — S

**7. Gap / mâu thuẫn.**
| # | Trích | Mô tả | Đề xuất |
|---|---|---|---|
| 1 | 062#logic-12 vs 053#9 bước 4 | Đổi sau công bố đưa tuyến về `created` → kho không xuất được (xem SCR-053 gap #3) | Issue làm rõ + sửa thiết kế (cross-screen) |
| 2 | 062#logic-7 (7-3) | Hủy tuyến `published`: "mọi đơn routed → allocated" — không nói đơn đã `shipped` trên tuyến | Issue làm rõ; đề xuất chặn hủy khi có đơn đã xuất |
| 3 | 062#logic-11 | Công thức KPI + ngưỡng 15 phút INFERRED | Issue làm rõ (PM với khách) |
| 4 | 062#logic-4-4, 060#logic-10 (10-4) | Ước lượng > 24h chặn công bố; lấy lại thời gian di chuyển đưa tuyến `checked → created` → phải kiểm lại → tuyến kiểm hôm trước, công bố hôm sau luôn phải làm lại 2 bước | Ghi rủi ro vận hành; BrSE xác nhận cách hiểu IF-MAP-01 |
| 5 | 062#7 | Người lập ≠ người công bố chưa yêu cầu (INFERRED) | Issue làm rõ |
| 6 | 062#logic-10 (10-2, 10-3) | Lịch retry, tài xế không email không chặn — INFERRED | Giả định |
| 7 | 062#logic-5 bước 3.8, database-design `driver_duty_records` | Khi bản mới công bố, duty records `route_plan` của bản `superseded` vẫn còn; spec chỉ nói đọc "bản published mới nhất" (061#logic-5) — không nói xóa/đánh dấu | Sửa thiết kế: ghi rõ lọc theo `route_versions.status='published'` ở mọi chỗ đọc (gồm thẻ SCR-002) |
| 8 | 062#logic-8-3 | Enum `route_versions.status` ghi "database-design chưa liệt kê" nhưng database-design §3.2 đã có | Sửa câu trong spec (nhỏ) |
| 9 | 062#3 | `in_progress/completed` do F06 chuyển — ngoài phạm vi; trước khi có F06 tuyến kẹt ở `published` | Ghi phụ thuộc; PM quyết định có cần nút chuyển tay tạm |

---

## SCR-063 — 予期し得ない事象記録 (Ghi sự cố bất khả kháng)

**1. Mục đích / role.** Ghi sự cố có bằng chứng khách quan (tai nạn, hỏng xe, thiên tai, chậm có bằng chứng) gắn tuyến/tài xế/khoảng giờ; duyệt 2 người; sự cố duyệt bị loại khỏi báo cáo tuân thủ lịch thường và đưa vào báo cáo riêng; không sửa kết quả kiểm cũ. Ghi: `dispatcher`, `transport_manager`; duyệt: `transport_manager`; xem: `auditor` (063#7).

**2. Khu vực.** Bộ lọc (khoảng ngày, tài xế, trạng thái) · nút 事象を登録 · bảng sự cố (EV-xxxxxx, loại, khoảng, tuyến/tài xế, người ghi, trạng thái, người duyệt) · chi tiết (mô tả, bằng chứng tải signed URL, kết quả kiểm liên quan "không đổi", 承認/却下 + nhận xét) · khối tổng hợp báo cáo tuân thủ (lịch thường / theo sự cố + CSV) · dialog đăng ký (tuyến, tài xế tự lấy, loại, bắt đầu/kết thúc, mô tả, file, số tham chiếu).

**3. Dữ liệu.**
- Bảng: `unforeseeable_events` (+`evidence_file_path`, `evidence_sha256`, `evidence_ref_no`, `decision_comment`, `decided_at`, `created_at`), `routes`, `drivers`, `profiles`, `driver_duty_records`, `route_segments`, `compliance_check_results`, `notification_outbox`, `audit_log`; Storage bucket riêng `event-evidence`.
- RPC: `create_unforeseeable_event` (khóa `drivers` FOR UPDATE), `decide_unforeseeable_event`, `get_unforeseeable_event`, `compliance_report_summary(p_month)`; view `unforeseeable_events_list_view`.
- API: GET list, GET detail, POST create (multipart, Idempotency-Key), POST approve, POST reject, GET `/api/compliance-reports/summary`, GET `/api/compliance-reports/events.csv` (UTF-8 BOM).
- BR: BR-DRV-24, BR-DRV-23, BR-INV-03, sm-unforeseeable. ADR-007 (append-only), ADR-006.

**4. Validation / trạng thái / luồng.**
- State machine `submitted → approved | rejected` (kết thúc). Bất biến: trigger chỉ cho 1 lần chuyển, UPDATE khác → M_667.
- Người duyệt ≠ người ghi (M_665, CHECK). Từ chối: nhận xét 10–500 bắt buộc (M_06); duyệt: tùy chọn ≤ 500.
- Đăng ký: tuyến bắt buộc (published/in_progress/completed, 30 ngày gần nhất — INFERRED); loại bắt buộc; start/end bước 5 phút, không tương lai (M_668), end > start (M_661), ≤ 24h (M_05, INFERRED); phải chồng ca tài xế (thực tế hoặc kế hoạch bản công bố) (M_662); không chồng sự cố khác `submitted/approved` của cùng tài xế (M_671); mô tả 1–1000; file PDF/JPEG/PNG ≤ 10MB (M_670) hoặc số tham chiếu ≤ 255 — ít nhất một (M_660). SHA-256 tính phía server.
- Lọc: khoảng sự cố chồng khoảng ngày; from > to → M_13; > 366 ngày → M_05.
- Thông báo duyệt cho `transport_manager` qua outbox, không SMS.

**5. Giờ lái 2024: Có.**
- BR-DRV-24: sự cố `approved` chỉ cắt khi tính **BR-DRV-04/05, BR-DRV-09, BR-DRV-11** cho báo cáo lịch thường; vi phạm 3 nhóm này trong khoảng sự cố chuyển sang báo cáo sự cố; **BR-DRV-01/02/03, 06, 07/08, 10 tính đủ**; `submitted/rejected` không cắt (063#logic-6, INFERRED, Q&A-B06).
- BR-DRV-23: duyệt sự cố không chạy lại / không sửa / không xóa kết quả kiểm (063#logic-5-3).
- Báo cáo tuân thủ tính trên giờ **thực tế** (`driver_duty_records` thực tế + segment tuyến đã chạy) (063#logic-6 mục 2).

**6. Sub-task.**
1. [BE] Migration `unforeseeable_events` cột bổ sung + CHECK (`approved_by <> reported_by`, `end_at > start_at`, có file hoặc ref) + trigger bất biến (1 lần chuyển, M_667) — M
2. [Infra] Bucket riêng `event-evidence` + policy + job dọn file mồ côi hằng ngày — S
3. [BE] RPC `create_unforeseeable_event` (kiểm chồng ca, chồng sự cố với khóa `drivers`, outbox, audit) — M
4. [BE] API POST create multipart (upload trước, SHA-256 server, zod refine, Idempotency-Key) — M
5. [BE] RPC `decide_unforeseeable_event` + API approve/reject (FOR UPDATE, M_665, M_22) — S
6. [BE] API list + detail (view, signed URL 5 phút, related checks của bản đã công bố) — M
7. [BE][DRV] Hàm `compliance_report_summary(p_month)`: chạy engine trên dữ liệu thực tế, cắt khoảng sự cố `approved` chỉ cho BR-DRV-04/05, 09, 11; tách vi phạm sang báo cáo sự cố — L
8. [BE][DRV] Export CSV `events.csv` (UTF-8 BOM, sự cố duyệt + vi phạm trong khoảng) — S
9. [FE] Trang danh sách: bộ lọc (mặc định theo vai trò), bảng, panel chi tiết + bằng chứng + kết quả kiểm liên quan — M
10. [FE] Dialog đăng ký: chọn tuyến (prefill `?route_id`), tài xế tự lấy, loại, datetime, upload, validate client, banner bất biến, M_31 — M
11. [FE] Nút duyệt/từ chối + nhận xét + M_664 — S
12. [FE] Khối tổng hợp báo cáo tuân thủ (chọn tháng, 6.1, 6.2, link CSV) — S
13. [QA][DRV] Test case: bất biến (UPDATE trực tiếp bị chặn), 2 người, chồng ca/chồng sự cố, file sai định dạng/quá 10MB, phạm vi loại sự cố theo từng rule (04/05, 09, 11 cắt; 01/02/03/06/07/08/10 không cắt) — M
14. [QA] Chạy test SCR-063 (gồm CSV, signed URL hết hạn) — M
15. [BrSE][DRV] Làm rõ gap #1–#5 — S

**7. Gap / mâu thuẫn.**
| # | Trích | Mô tả | Đề xuất |
|---|---|---|---|
| 1 | 063#logic-6 (6-2, 6-3), BR#br-drv BR-DRV-24 | Phạm vi cắt sự cố + cách tính báo cáo INFERRED (Q&A-B06) | Issue làm rõ (chung với SCR-061 gap #4) |
| 2 | 063#logic-6 (6-2) vs database-design `driver_duty_records` | Báo cáo "trên giờ thực tế" nhưng BR-DRV-11 (lái liên tục) cần segment; duty record thực tế chỉ có `drive_h`, `break_h` → không tính được lái liên tục thực tế, spec dùng segment **kế hoạch** của tuyến đã chạy | Issue làm rõ / sửa thiết kế: định nghĩa nguồn segment thực tế (F06) hoặc ghi rõ dùng kế hoạch |
| 3 | BR#sm-unforeseeable ("sai → tạo bản mới tham chiếu bản cũ") vs 063#9, database-design | Không có cột tham chiếu bản cũ trong bảng/API/dialog | Sửa thiết kế: thêm `supersedes_event_id` hoặc bỏ câu trong BR |
| 4 | database-design ERD `unforeseeable_events.evidence_ref` vs §3.2 `evidence_ref_no` | Hai cột cùng nghĩa | Sửa thiết kế DB: giữ 1 cột |
| 5 | 063#7, role-permission-matrix dòng 52 | Chỉ `transport_manager` duyệt và không duyệt sự cố mình ghi → nếu chỉ có 1 `transport_manager` và người đó ghi thì không ai duyệt được | Issue làm rõ (BrSE/PM) |
| 6 | 063#logic-7-1, 063#logic-7-5, 063#logic-2-3 | 30 ngày, ≤ 24h, mặc định 承認待ち — INFERRED | Giả định |
| 7 | 063#logic-7-1 vs 062#3 | Chọn tuyến `in_progress/completed` nhưng 2 trạng thái này do F06 chuyển (ngoài phạm vi) → trước F06 chỉ còn `published` | Ghi phụ thuộc |

---

## Tổng kết

| Màn | Sub-task | Trong đó [DRV] |
|---|---|---|
| SCR-044 | 17 | 0 |
| SCR-053 | 19 | 0 |
| SCR-060 | 23 | 2 |
| SCR-061 | 29 | 23 |
| SCR-062 | 17 | 2 |
| SCR-063 | 15 | 4 |
| **Tổng** | **120** | **31** |

Gap ưu tiên cao (chặn hoặc lệch dữ liệu):
1. Đổi tuyến sau công bố làm kho không xuất được (053 gap #3 / 062 gap #1).
2. Không có màn nhập giờ làm thực tế (`actual_manual`) mà engine cần (061 gap #1).
3. Hash đầu vào cài đặt 2 nơi TS + SQL (061 gap #10); thuật toán chuỗi lái 2 nơi (060 gap #2).
4. Giờ xuất phát SCR-053 lệch định nghĩa SCR-060 (053 gap #2).
5. BR-DRV-11 trên dữ liệu thực tế không có segment (063 gap #2); Q&A-B06/B07 chưa chốt (công thức tăng ca, phạm vi loại sự cố, 労使協定).
6. Job hết hạn 日付逆転 thiếu `PREVIOUS_CHANGED` so với BR-DATE-02 (044 gap #2); hủy tuyến có đơn đã xuất (062 gap #2).

Câu hỏi mở: 1 tài xế 1 tuyến/ngày (060 gap #1) — nếu sai, engine SCR-061 phải gộp ca nhiều tuyến; cần chốt trước khi làm SCR-061 #2.
