# Trích xuất màn hình nhóm C — SCR-037, SCR-040, SCR-041, SCR-042, SCR-043

Nguồn: `lab4-product-b-design/specs/05-screens/SCR-<id>_SPEC.md` (đọc hết), đối chiếu `04-business-rules/business-rules.md`,
`03-database/database-design.md`, `06-common/role-permission-matrix.md`, `06-common/message-list.md`, `02-adr/ADR-006`.
Quy ước cỡ: S ≤ 4h · M ≤ 8h · L ≤ 16h. Mọi gap ghi rõ file#section.

## 0. Kết luận về giờ lái xe 2024 (ADR-006)

**Không màn nào trong nhóm C chứa rule giờ lái xe.** Grep `driver|運転|拘束|960|ADR-006` trên 5 spec chỉ thấy dòng phân quyền
(`driver` không thấy màn: SCR-037 §7, SCR-043 §7). ADR-006 front-matter gắn rule BR-DRV-01..25 với **SCR-060..063** (nhóm khác).

Liên quan gián tiếp (không sinh rule mới, chỉ là phụ thuộc trạng thái):
- Trạng thái đơn `routed` do SCR-060 gán tuyến (business-rules.md#sm-order). SCR-040 ẩn nút hủy khi `routed` (SCR-040 §5 item 11.12);
  SCR-042 chuyển chỉ xem khi `routed`/`shipped` (SCR-042 §8). Muốn hủy/sửa phân bổ phải gỡ tuyến trước (`routed → allocated`, chỉ khi tuyến chưa published).
- SCR-043 đọc `delivery_history` ghi bởi `confirm_shipment()` (SCR-043 §3); xác nhận xuất cần tuyến đã công bố (M_465, SCR-053), và
  tuyến chỉ công bố được khi qua kiểm tra giờ làm (ADR-006 §3). → Dữ liệu SCR-043 phụ thuộc gián tiếp vào engine ADR-006.

Để tham chiếu cho nhóm SCR-060..063 (trích nguyên văn ADR-006 §1, **không** thuộc nhóm C): tăng ca 960h/năm; 3.300h/năm; 284h/tháng;
ràng buộc 13h/ngày (max 15h); nghỉ giữa ca 11h (min 9h); lái TB 9h/ngày (2 ngày); 44h/tuần (2 tuần); lái liên tục ≤ 4h
(nghỉ ≥ 10 phút được tính, reset khi tổng nghỉ ≥ 30 phút — ADR-006 §3 bước 2). Đề xuất tách sub-task từng rule ở nhóm đó, không ở đây.

---

## 1. SCR-037 — 隔離・解除・廃棄 (Cách ly / giải phóng / hủy lô)

**1. Mục đích:** QA quyết định số phận lô cách ly: đưa vào 保留, giải phóng (về `available`) hoặc hủy; không tự giải phóng (RFP D1).
Role: `quality` thao tác; `warehouse_lead`, `auditor` chỉ xem; còn lại không thấy (§7).

**2. Component:** tiêu đề; tab vùng nhiệt 冷蔵(C-Q)/冷凍(F-Q)/常温 kèm số lô; bộ lọc (SKU, mã lô, trạng thái); bảng lô cách ly
(4.1–4.12: lô, SKU, hạn, vị trí + badge 要移動, tồn, đã phân bổ, thời điểm/lý do cách ly, deviation, yêu cầu hủy, thao tác, trạng thái);
bảng hủy chờ duyệt [5]; dialog giải phóng [6]; dialog hủy [7]; dialog duyệt/từ chối hủy [8]; ghi chú vùng thường [9]; dialog 保留 [10].

**3. Dữ liệu:**
- Đọc: `lot_stock_view`, `lot_status_events`, `deviations`, `lot_disposal_requests`, `locations`, `skus`, `profiles`. View mới `quarantine_lot_view`.
- Ghi: `lots` (status, location_id, qty_on_hand), `lot_status_events` (hold/release/dispose, `reevaluation_plan`, `reevaluation_due`),
  `inventory_movements` (`move` qty 0, `dispose`), `lot_disposal_requests`, `deviations` (đóng), `audit_log`, Storage `quality-evidence`.
- API/RPC (§9): `GET /api/lots/quarantine`, `GET /api/lot-disposal-requests[?status|/{id}]`, `POST /api/lots/{id}/hold|release|dispose`,
  `POST /api/lot-disposal-requests/{id}/decision`, `POST /api/evidence`; RPC `hold_lot`, `release_lot`, `dispose_lot`, `decide_lot_disposal`
  (security definer, 1 transaction, `FOR UPDATE`, idempotency key, correlation_id, audit).
- BR: BR-TEMP-02, BR-TEMP-03, BR-INV-02, BR-INV-03, sm-lot, BR-ALLOC-ORDER lớp 3; FR-INV-05, RFP FIG-011, NFR-SEC-02, RBAC-001 nguyên tắc 3.
- ADR: ADR-002 (RPC), ADR-007 (append-only/audit), ADR-008.
- Tham số `lot_disposal_dual_approval_qty` = 100 (Q&A-B15), chỉ `admin` đổi + audit (§6).

**4. Validation / trạng thái / luồng:**
- Chuyển hợp lệ (§5 item 4.11): `quarantine` → 保留/解除/廃棄; `on_hold` → 解除/廃棄. Không có hủy lô `available`, không có `on_hold → quarantine`. Sai → M_301.
- Disable mọi nút khi có yêu cầu hủy `pending` (M_321) hoặc `qty_allocated > 0` (dữ liệu cũ).
- Lý do 10–500 (M_06); bằng chứng: file PDF/JPG/PNG ≤ 10MB **hoặc** số tham chiếu 1–100 (M_307, M_316).
- Giải phóng: vị trí đích bắt buộc khi đang ở khu `-Q`; phải active, không `-Q`, đúng vùng (M_204, M_313).
- 保留: kế hoạch 10–500 (M_325), ngày dự kiến ≥ hôm nay JST (M_326); quá hạn chỉ hiện `期限超過`, không tự đổi trạng thái.
- Hủy: luôn toàn bộ tồn; `qty_on_hand > ngưỡng` → tạo yêu cầu `pending` (duyệt 2 người, người duyệt ≠ người gửi: CHECK DB + M_311);
  ≤ ngưỡng → hủy ngay. Duyệt: kiểm `ALREADY_DECIDED` (M_312), qty đổi → INVALID_TRANSITION. Từ chối cần comment 10–500 (M_318).
- Trạng thái màn: loading skeleton, empty M_32, lỗi M_40/M_41 + 再試行, xung đột → reload (§8).

**5. Giờ lái xe 2024:** Không.

**6. Sub-task đề xuất (24):**
- [BE] Migration `lots.status` 5 giá trị + bảng `lot_status_events` append-only (trigger chặn UPDATE/DELETE) — M
- [BE] `locations.is_quarantine` + seed `C-Q-xx`, `F-Q-xx` (tùy chọn `A-Q-xx`) — S
- [BE] Bảng `lot_disposal_requests` (request_no `DSP-####`, CHECK decided_by ≠ requested_by, unique partial pending, trigger khóa sau quyết định) — M
- [BE] Lưu tham số `lot_disposal_dual_approval_qty` (chỉ admin sửa, có audit) — S
- [BE] View `quarantine_lot_view` + `GET /api/lots/quarantine` (zoneCounts, ambientHasQuarantineLocation, allowedActions) — M
- [BE] RPC `hold_lot` + `POST /api/lots/{id}/hold` — M
- [BE] RPC `release_lot` (kiểm vị trí đích, movement `move`, đóng deviation) + `POST …/release` — L
- [BE] RPC `dispose_lot` (nhánh ngưỡng, movement `dispose`) + `POST …/dispose` — M
- [BE] RPC `decide_lot_disposal` + `POST …/decision` + `GET` danh sách/chi tiết yêu cầu (`canDecide`) — M
- [BE] Bucket private `quality-evidence` + `POST /api/evidence` + signed URL 5 phút (dùng chung SCR-031, kiểm đã làm chưa) — M
- [BE] Permission `lot:release`/`lot:dispose` cho `quality` + RLS + `has_role` trong RPC — S
- [Infra] Job dọn file bằng chứng mồ côi trong bucket — S
- [FE] Khung trang, tab vùng (tab mặc định, nhãn động 常温), bộ lọc + đồng bộ query — M
- [FE] Bảng lô cách ly: badge 要移動, cờ hạn, mapping lý do, deviation, badge yêu cầu hủy, tooltip 保留/期限超過 — M
- [FE] Cột thao tác theo state + quy tắc disable — S
- [FE] Dialog 保留 — S
- [FE] Dialog giải phóng (upload bằng chứng, chọn vị trí đích, mapping lỗi) — M
- [FE] Dialog hủy (đổi nhãn nút theo ngưỡng, thông báo M_323) — S
- [FE] Bảng hủy chờ duyệt + dialog duyệt/từ chối (ẩn với người gửi) — M
- [FE] Ghi chú 常温 (M_314) + ẩn/hiện theo vai trò, trang 403 — S
- [QA] Test case + chạy: state machine lô (chuyển hợp lệ, bước nhảy sai M_301, yêu cầu pending chặn thao tác) — M
- [QA] Test duyệt 2 người: biên 100/101, tự duyệt, đã quyết định, qty đổi, đồng thời — M
- [QA] Test giải phóng: vị trí đích (khác vùng, khu -Q, ngưng dùng, ambient không -Q), bằng chứng, RBAC theo 3 vai trò — M
- [BrSE] Làm rõ: đường tắt Q&A-B12, hủy một phần, đóng deviation khi giải phóng, lưu `evidence_no`, 要移動 có chặn không — S

**7. Gap / mâu thuẫn:**
| # | Vị trí | Mô tả | Đề xuất |
|---|---|---|---|
| 1 | SCR-037 §5 item 6.4 vs §9 #4 | API nhận `evidence_no`, nhưng lưu bằng cách nối `[REF:x]` vào `reason`; DB `lot_status_events` không có `evidence_note` | Issue làm rõ; nghiêng về thêm cột riêng để tra cứu được |
| 2 | §5 item 7.1 | Chỉ hủy toàn bộ lô; hủy một phần cần tách lô, chưa thiết kế (INFERRED) | Giả định hủy toàn bộ cho phase 1, ghi issue |
| 3 | §9 `release_lot` bước 7 | Tự đóng deviation khi giải phóng/hủy là INFERRED (có thể F08 muốn đóng riêng) | BrSE hỏi khách |
| 4 | §5 item 4.4 | Badge 要移動 chỉ cảnh báo, không chặn (INFERRED) | Giả định không chặn, xác nhận |
| 5 | §5 item 4.6 | Lô cách ly có `qty_allocated > 0` (dữ liệu prototype) → khóa nút; cách xử lý dữ liệu cũ chưa rõ | Thêm bước dọn dữ liệu trong migration |
| 6 | §6 / database-design | Tham số `lot_disposal_dual_approval_qty` không có bảng lưu trong database-design (grep không thấy) | Sửa thiết kế: thêm bảng tham số hệ thống có phiên bản (ADR-003) |
| 7 | §9 ghi chú bảng vs database-design.md:126,129 | Spec nói `request_no`, `reevaluation_*` "chưa có — cần thêm", nhưng ER to-be đã có | Spec lỗi thời; cập nhật spec |
| 8 | §6 M_317 | Câu "ロットは隔離のままです" sai khi lô đang `on_hold` | Sửa message: giữ nguyên trạng thái hiện tại |
| 9 | §7 ghi chú | Cách hiểu dấu "—" của `lot:quarantine` cho SCR-037 cần chốt lại (role-permission-matrix §3 chú thích ¹ đã xác nhận) | Đóng gap, cập nhật spec |
| 10 | §5 item 6.3 | Định dạng/dung lượng file 10MB là INFERRED | Xác nhận cùng gap #G-3 của SCR-042 |
| 11 | §5 item 6.7 | Job dọn file mồ côi là INFERRED, không có lịch/ngưỡng | Infra đề xuất (vd. > 24h không tham chiếu) |

---

## 2. SCR-040 — 受注一覧 (Danh sách đơn hàng)

**1. Mục đích:** tra cứu đơn, theo dõi tiến độ phân bổ, đi tới tạo/phân bổ, và hủy đơn chưa gán tuyến (BR-ORD-03).
Role: mọi vai trò đã gán xem; `sales_planner`, `sales_manager`, `admin` tạo/hủy/phân bổ (§7).

**2. Component:** tiêu đề; nút 新規受注; bộ lọc (từ khóa, khách, khoảng ngày yêu cầu, 6 checkbox trạng thái, chỉ đơn có dòng chờ nghiệp vụ duyệt);
検索/クリア; số kết quả; bảng (11.1–11.12: số đơn, mã tham chiếu, khách, ngày yêu cầu, số dòng, tiến độ, badge business_review,
badge ngoại lệ chờ duyệt, trạng thái, thời điểm tạo, 引当/表示, 取消); phân trang 50; dialog hủy đơn [13].

**3. Dữ liệu:**
- Đọc: view mới `order_list_view` (security_invoker) gom `orders`, `customers`, `order_lines`, `allocations(active)`, `date_reversal_exception_requests(pending)`.
- Ghi (hủy): `allocations` → cancelled, `inventory_movements` (`unallocate`), `lots.qty_allocated`, `date_reversal_exception_requests` → `expired` (`ORDER_CANCELLED`), `orders` (cancel_*), `audit_log`.
- API: `GET /api/orders` (sửa), `GET /api/orders/{id}`, `POST /api/orders/{id}/cancel` (mới) → RPC `cancel_order(p_order_id, p_reason)`.
- BR: BR-ORD-02, BR-ORD-03, BR-DELWIN-01, BR-DATE-02, BR-INV-02, sm-order. ADR: ADR-002, ADR-005 (gián tiếp), ADR-007.

**4. Validation / trạng thái:**
- Từ khóa ≤ 50 (M_04), escape `%`/`_`; từ ngày > đến ngày → M_13; mặc định từ = hôm nay − 7, trạng thái mặc định 4 trạng thái còn việc.
- Sắp xếp cố định `orders.id desc`; điều kiện ghi lên query string để quay lại từ SCR-042.
- Ngày yêu cầu < hôm nay và đơn `open`/`partially_allocated` → chữ đỏ, tooltip M_444.
- Hủy được khi `open`/`partially_allocated`/`allocated`; khác → M_402. Lý do 10–500 (M_06). Khóa `lots` theo id tăng để tránh deadlock.
- Trạng thái màn: skeleton, M_32 (+ nút tạo), M_40/M_41/M_21, 「取消中…」.

**5. Giờ lái xe 2024:** Không trực tiếp. Gián tiếp: `routed` (SCR-060) → ẩn hủy.

**6. Sub-task đề xuất (11):**
- [BE] Migration cột `orders` (customer_ref + unique lower, created_at, cancel_reason/by/at) + 6 giá trị status (dùng chung SCR-041/042) — S
- [BE] View `order_list_view` + `GET /api/orders` (lọc, phân trang, total) — M
- [BE] RPC `cancel_order` + `POST /api/orders/{id}/cancel` (khóa, unallocate movement, hết hạn yêu cầu ngoại lệ, audit) — M
- [FE] Thanh lọc + đồng bộ query string + clear + validation — M
- [FE] Bảng đơn: badge trạng thái, tiến độ, badge business_review/ngoại lệ, link, phân trang — M
- [FE] Dialog hủy đơn (tải số phân bổ/yêu cầu mới nhất, M_400, lý do) — S
- [FE] Menu hiện cho mọi vai trò, ẩn nút theo quyền — S
- [QA] Test lọc/phân trang/escape ký tự đặc biệt/biên ngày — S
- [QA] Test hủy theo từng trạng thái + kiểm movement/yêu cầu expired + xung đột (đơn vừa routed) — M
- [QA] Test RBAC 9 vai trò + API 403 — S
- [BrSE] Làm rõ mặc định lọc (−7 ngày, 4 trạng thái), lý do hủy bắt buộc — S

**7. Gap / mâu thuẫn:**
| # | Vị trí | Mô tả | Đề xuất |
|---|---|---|---|
| 1 | §5 item 13.3 | Lý do hủy bắt buộc là INFERRED (BR-ORD-03 không nói) | BrSE xác nhận; giả định bắt buộc |
| 2 | §5 item 5.1, 6.2 | Mặc định −7 ngày và 4 trạng thái là INFERRED | Giả định, xác nhận |
| 3 | §5 item 13.4-3 | Xung đột trả "M_402 (hoặc M_22)" — không chốt mã | Chốt: 409 `NOT_CANCELLABLE` → M_402 |
| 4 | §9 ghi chú | Nói DB-001 chưa có cột `customer_ref`, `cancel_*`; database-design.md:132 đã có | Spec lỗi thời, cập nhật |
| 5 | §5 item 11.1 | Không có màn chi tiết đơn riêng; dùng SCR-042 chế độ xem (INFERRED) | Xác nhận với screen list |
| 6 | sm-order (business-rules.md) | Đơn `routed` muốn hủy phải gỡ tuyến trước; spec không nêu hướng dẫn cho người dùng | Thêm tooltip/hướng dẫn, issue nhỏ |

---

## 3. SCR-041 — 受注登録 (Đăng ký đơn hàng)

**1. Mục đích:** nhập tay 1 đơn (khách, ngày yêu cầu, mã tham chiếu, dòng SKU + qty + điều kiện giao theo hợp đồng). Role: `sales_planner` (chính), `sales_manager`, `admin`.

**2. Component:** link quay lại; tiêu đề + ghi chú CSV ERP để phase sau; khách; ngày yêu cầu; mã tham chiếu khách; bảng dòng
(6.1–6.8: STT, SKU, badge vùng/loại hạn, hợp đồng + badge window_rule, điều kiện giao, qty, xóa, thông báo dòng); thêm dòng; đếm dòng; hủy; đăng ký; tóm tắt lỗi.

**3. Dữ liệu:**
- Đọc: `customers`, `skus` (active), `customer_sku_agreements` (hiệu lực theo ngày), `orders` (check trùng ref).
- Ghi: `orders` (`open`, `O-`+sequence), `order_lines` (`agreement_id`, `delivery_term`, `line_status` open/business_review), `idempotency_keys`, `audit_log`.
- API: `GET /api/customers`, `GET /api/skus`, `GET /api/agreements/lookup` (mới), `GET /api/orders/check-ref` (mới), `POST /api/orders` (sửa) → RPC `create_order(...)`.
- BR: BR-ORD-01, BR-ORD-02, BR-DELWIN-01, BR-TIME-01; FR-OUT-01. ADR: ADR-002, ADR-003 (hợp đồng có `effective_from`).

**4. Validation / trạng thái:**
- Khách bắt buộc (M_01); ngày bắt buộc, ≥ `app_today()` JST (M_409, kiểm ở SQL).
- Mã tham chiếu `^[0-9A-Za-z_-]{1,50}$` (M_13/M_01), không trùng trong cùng khách không phân biệt hoa thường (M_408, blur + DB unique); khác khách được trùng.
- 1–50 dòng (M_411); mỗi SKU 1 dòng (M_410); qty 1–99 999 (M_05); master ngưng dùng giữa chừng → M_414.
- Hợp đồng 3 nhánh: có rule → `open`; `window_rule IS NULL` → cảnh báo M_407, vẫn đăng ký, `business_review`; không có hợp đồng → M_405, chặn đăng ký.
- Đổi điều kiện giao khác hợp đồng → cảnh báo M_413 (không chặn). Đổi khách/ngày → tra lại hợp đồng mọi dòng.
- Idempotency-Key UUID khi mở form; thành công → toast M_412 → SCR-042. 401 → giữ form trong sessionStorage.

**5. Giờ lái xe 2024:** Không.

**6. Sub-task đề xuất (11):**
- [BE] `GET /api/agreements/lookup` (chọn phiên bản hợp đồng hiệu lực theo ngày) — M
- [BE] `GET /api/orders/check-ref` + unique index `(customer_id, lower(customer_ref))` — S
- [BE] Viết lại RPC `create_order` (thêm `sales_manager`, validation đầy đủ, hợp đồng từng dòng, `line_status`, idempotency, mã lỗi) + `POST /api/orders` — L
- [BE] Chuẩn hóa error body `{code, messageId, params}` + map M_4xx (dùng chung SCR-042) — S
- [FE] Phần đầu form: khách, ngày (hôm nay từ server), mã tham chiếu check khi blur — M
- [FE] Bảng dòng động: thêm/xóa ≤ 50, chống trùng SKU, tra hợp đồng từng dòng, badge, điều kiện giao, thông báo dòng — L
- [FE] Tóm tắt lỗi, submit + Idempotency-Key, xác nhận rời trang M_31, khôi phục từ sessionStorage — M
- [QA] Test 3 nhánh hợp đồng (AGR-008/AGR-014, có rule, chưa có hợp đồng) — S
- [QA] Test biên: qty 0/1/99999/100000, 50/51 dòng, ref trùng hoa/thường, khác khách, ngày quá khứ JST — M
- [QA] Test gửi lại cùng key, master ngưng dùng giữa chừng, RBAC (vào thẳng URL) — S
- [BrSE] Làm rõ: ref bắt buộc, chặn khi thiếu hợp đồng, cho đổi điều kiện giao, chọn hợp đồng khi nhiều `effective_from` — S

**7. Gap / mâu thuẫn:**
| # | Vị trí | Mô tả | Đề xuất |
|---|---|---|---|
| 1 | §5 item 5-1 | Mã tham chiếu bắt buộc là INFERRED | BrSE hỏi khách |
| 2 | §5 item 6.4-3 | Chặn khi không có hợp đồng là INFERRED; phương án khác: cho đăng ký như `business_review` | BrSE hỏi; giả định chặn |
| 3 | §5 item 6.5-2 | Cho đổi điều kiện giao theo đơn là INFERRED | BrSE hỏi |
| 4 | §5 item 4-3 | Cách chọn hợp đồng khi nhiều `effective_from` là INFERRED | Giả định bản `effective_from ≤ requested_date` lớn nhất (khớp ADR-003) |
| 5 | §9 ghi chú | Nói DB-001 chưa có `customer_ref`, `delivery_term`; database-design.md:132-133 đã có | Spec lỗi thời |
| 6 | §6 | M_406 bị trùng nghĩa (đã gán cho BR-TEMP-02 C, SCR-053) — spec đã tránh | Không cần làm gì, ghi nhận |
| 7 | §3 | Nhập CSV ERP (FN-0402) ngoài phạm vi | Tạo epic/issue riêng phase sau |

---

## 4. SCR-042 — アロケーション (Phân bổ lô cho dòng đơn)

**1. Mục đích:** phân bổ lô cho từng dòng đơn, thực thi BR-ALLOC-ORDER ở SQL (1 消費期限 → 2 vùng nhiệt → 3 cách ly → 4 cửa sổ giao/hợp đồng → 5 日付逆転 → 6 FEFO);
gửi yêu cầu ngoại lệ 日付逆転; cũng là màn xem chi tiết đơn. Role: `sales_planner` (phân bổ + gửi ngoại lệ); `sales_manager`, `admin` phân bổ, không gửi ngoại lệ; còn lại chỉ xem.

**2. Component:** quay lại; tiêu đề + badge đơn; thông tin đơn (基準日 từ server, badge 要求日超過); chú giải ①–⑥; mỗi dòng đơn 1 panel:
đầu panel (SKU, vùng/loại hạn, hợp đồng + điều kiện giao, SL đặt/đã phân bổ/còn, trạng thái dòng), banner business_review,
checkbox hiện lô bị loại, bảng lô ứng viên (8.1–8.12), SL phân bổ, nút 引当, bảng phân bổ đã có (11.1–11.6), bảng yêu cầu ngoại lệ (12.1–12.5);
dialog gửi ngoại lệ [13]; dialog xác nhận lô quá 賞味期限 [14]; dialog hủy phân bổ [15].

**3. Dữ liệu:**
- Đọc: `orders`, `order_lines`, `customer_sku_agreements`, `lots`, `locations`, `skus`, `delivery_history_ranked`/`last_delivered_expiry()`, `allocations`, `date_reversal_exception_requests`.
- Ghi: `allocations` (+ `allocation_evidence` jsonb), `inventory_movements` (`allocate`/`unallocate`), `lots.qty_allocated`, `order_lines.line_status`,
  `orders.status`, `exception_events` (rule 1 chặn), `date_reversal_exception_requests`, Storage `consent-evidence`, `idempotency_keys`, `audit_log`.
- API (§9): `GET /api/orders/{id}`, `GET /api/orders/{id}/allocation-candidates?lineId=`, `POST /api/allocations`, `POST /api/allocations/{id}/cancel`,
  `POST /api/date-reversal-requests` (multipart), `GET /api/date-reversal-requests?orderId=`.
- RPC/hàm: `evaluate_lot_for_line` (nguồn duy nhất của BR-ALLOC-ORDER, dùng chung với duyệt SCR-044), `get_allocation_candidates`, `allocate_lot` (bỏ `p_override_reason`),
  `unallocate_allocation`, `create_date_reversal_request`; dùng `app_today()`, `last_delivered_expiry()`, `is_date_reversal()`.
- BR: BR-ALLOC-ORDER, BR-EXP-01/02, BR-TEMP-02, BR-DELWIN-01, BR-DATE-01/02, BR-FEFO-01, BR-INV-01/02, BR-ORD-03, FR-OUT-02. ADR: ADR-002, ADR-005, ADR-007.

**4. Validation / trạng thái / luồng:**
- Rule (§5 item 8.11 bảng): 1 `EXPIRED_CONSUMPTION` (`consumption` và expiry ≤ hôm nay) — không ngoại lệ, ghi `exception_events` khi lệnh phân bổ bị chặn;
  2 `TEMP_ZONE_MISMATCH`; 3 `QUARANTINED` (`status ≠ available`); 4a `DELIVERY_WINDOW` tỉ lệ (`requested_date > deadline`), 4b thiếu ngày SX, 4c LABEL_DATE_ONLY (`expiry < requested_date`),
  4d `AGREEMENT_PENDING`; 5 `DATE_REVERSAL` (chỉ đường ngoại lệ); 6 FEFO (expiry → received_at → id).
- Công thức rule 4: `total_days = expiry − manufactured`; deadline = manufactured + floor(total/3) hoặc floor(total/2) (business-rules.md BR-DELWIN-01).
- Trả `first_reason` + `other_reasons[]`; nút ngoại lệ chỉ khi `first_reason = DATE_REVERSAL`.
- 賞味期限 quá hạn: cho phép + nhãn + dialog xác nhận; server thiếu cờ → 422 M_424.
- Phân bổ: SL 1..min(残, khả dụng) (M_05/M_426/M_427); khóa `orders → order_lines → lots`; đánh giá lại trên dữ liệu đã khóa; chọn lô không phải FEFO → M_425 + `fefo_skipped`.
- Trạng thái dòng: `open`/`business_review`/`allocated`; đơn `open → partially_allocated → allocated`. Dòng business_review: bảng chỉ xem, ẩn chọn/phân bổ kể cả admin.
- Ngoại lệ: SL ≤ 残 và ≤ khả dụng (M_442), lý do 10–500, bằng chứng file (PDF/JPG/PNG ≤ 10MB) hoặc số biên bản 1–100 (M_434/M_435), trùng pending → M_436; không tạo phân bổ; yêu cầu pending không giữ tồn.
- Hủy phân bổ khi đơn `partially_allocated`/`allocated` (M_441), lý do bắt buộc.
- Trạng thái màn: 404 M_23; `allocated` ẩn bảng ứng viên; `routed`/`shipped`/`cancelled` chỉ xem (M_430); xung đột → M_426/M_428/M_22 + tự tải lại.

**5. Giờ lái xe 2024:** Không trực tiếp. Gián tiếp: đơn `routed` (gán tuyến ở SCR-060) → màn chuyển chỉ xem, ẩn hủy phân bổ.

**6. Sub-task đề xuất (26):**
- [BE] `evaluate_lot_for_line` — rule 1 消費期限 (≤ hôm nay JST) — M
- [BE] `evaluate_lot_for_line` — rule 2 lệch vùng nhiệt (vị trí vs SKU) — S
- [BE] `evaluate_lot_for_line` — rule 3 cách ly (`status ≠ available`, gồm `on_hold`) — S
- [BE] `evaluate_lot_for_line` — rule 4 cửa sổ giao 4 nhánh + `window_evidence` — M
- [BE] `evaluate_lot_for_line` — rule 5 日付逆転 (cùng khách+SKU, không lịch sử → bỏ qua) — S
- [BE] `get_allocation_candidates` (first/other reasons, FEFO rank, sắp xếp, pendingRequest) + `GET …/allocation-candidates` — M
- [BE] Viết lại `allocate_lot`: khóa theo thứ tự, đánh giá lại, movement, evidence, cờ 賞味期限, `exception_events` 1 dòng/cặp, idempotency, bỏ override — L
- [BE] Tính lại `line_status` + `orders.status` (gồm `business_review ↔ open` khi hợp đồng đổi) — M
- [BE] RPC `unallocate_allocation` + `POST /api/allocations/{id}/cancel` — M
- [BE] `create_date_reversal_request` + bucket `consent-evidence` + `POST /api/date-reversal-requests` (multipart, rollback khi upload lỗi) — L
- [BE] `GET /api/date-reversal-requests?orderId=` (dùng chung SCR-044) — S
- [BE] Migration bỏ `date_reversal_overrides` → `date_reversal_exception_requests` (`is_legacy`, approved, decided_by null) — M
- [BE] Mở rộng `GET /api/orders/{id}` (today, agreement, line_status, evidence, yêu cầu ngoại lệ) — S
- [FE] Header, thông tin đơn, chú giải ①–⑥, chế độ chỉ xem theo vai trò/trạng thái — S
- [FE] Đầu panel dòng + banner business_review (link SCR-011 theo quyền) — S
- [FE] Bảng ứng viên cột 8.2–8.10 (hạn/ngày còn, SX/nhập, vị trí, trạng thái, khả dụng, lần giao trước, bằng chứng cửa sổ) — L
- [FE] Badge lý do 8.11 + tooltip `other_reasons` + checkbox hiện lô bị loại (localStorage) — M
- [FE] Form phân bổ: radio tự chọn FEFO, SL, M_425, gửi + Idempotency-Key, tải lại mọi panel — M
- [FE] Dialog xác nhận lô quá 賞味期限 — S
- [FE] Bảng phân bổ đã có + chi tiết bằng chứng + dialog hủy phân bổ — M
- [FE] Bảng yêu cầu ngoại lệ + dialog gửi ngoại lệ (khối so sánh, trục ngày, bằng chứng file/số) — L
- [QA] Ma trận thứ tự rule: mỗi `first_reason`, lô trượt nhiều rule, 4 nhánh rule 4 với biên floor/deadline, 消費期限 = hôm nay — L
- [QA] 日付逆転: chặn, gửi yêu cầu, chưa có lịch sử, hạn bằng nhau, không mượn lịch sử khách khác (ví dụ CUS-003/CUS-004) — M
- [QA] Đồng thời: 2 người phân bổ cùng lô không vượt tồn, không deadlock; idempotency — M
- [QA] RBAC (`sales_manager`/`admin` không gửi ngoại lệ) + trạng thái đơn routed/shipped/cancelled chỉ xem — S
- [BrSE] Làm rõ: Q&A-B01, Q&A-B02, Q&A-B16, chọn lô ngoài FEFO, yêu cầu pending không giữ tồn, thời điểm ghi `exception_events`, phân bổ sau ngày yêu cầu — S

**7. Gap / mâu thuẫn:**
| # | Vị trí | Mô tả | Đề xuất |
|---|---|---|---|
| G-1 | SCR-042 §5 item 8-2, 8.7 vs business-rules.md#sm-lot | Tập ứng viên chỉ `status IN ('available','quarantine')`, badge chỉ 可/隔離; lô `on_hold` (SCR-037) không hiện dù BR nói `on_hold` bị loại ở lớp 3 | Sửa thiết kế: thêm `on_hold` vào tập + badge 「保留」, lý do ③ |
| G-2 | §5 item 5.5-2 vs §5 item 8.11-4 | "Server tính lại `line_status` mỗi lần mở màn" = hàm đọc có tác dụng phụ, trái nguyên tắc 8.11-4; chuyển `business_review → open` là INFERRED | Sửa thiết kế: tính trong view, hoặc trigger khi `customer_sku_agreements` đổi |
| G-3 | §5 item 13.5, 13.6 | Định dạng/dung lượng file và độ dài số biên bản là INFERRED | BrSE xác nhận (dùng chung với SCR-037) |
| G-4 | §5 item 13.9-4, §9 #5 | INSERT trong RPC rồi upload Storage "trong cùng request; lỗi → rollback": Storage nằm ngoài transaction Postgres, rollback sau khi RPC commit không tự xảy ra | Sửa thiết kế: upload trước vào đường tạm rồi RPC ghi ref, hoặc trạng thái nháp; issue BE |
| G-5 | §5 item 8.8-2 | Yêu cầu pending không giữ tồn (INFERRED) → lúc duyệt có thể thiếu (M_452) | Giả định, xác nhận |
| G-6 | §5 item 8.11-4 | Thời điểm ghi `exception_events` là INFERRED | BrSE xác nhận |
| G-7 | §5 item 10-2 | Cho chọn lô khác FEFO là INFERRED | BrSE xác nhận |
| G-8 | §5 item 3-3 | Cho phân bổ khi đã quá ngày yêu cầu là INFERRED | BrSE xác nhận |
| G-9 | §5 item 11.6-2, 15-3 | Hủy phân bổ và hành vi với phân bổ từ ngoại lệ đã duyệt là INFERRED (Q&A-B04) | Xác nhận |
| G-10 | §5 item 14-3; business-rules.md BR-EXP-01 note | "Chính sách hợp đồng" cho 賞味期限 quá hạn chưa có field (Q&A-B16) | Chờ khách; giữ hành vi cho phép + nhãn |
| G-11 | business-rules.md BR-DELWIN-01 | Công thức dùng ngày SX hay ngày nhập — Q&A-B02 mở | Chờ khách |
| G-12 | SCR-043 §3 vs SCR-042 §4 | SCR-043 nói có link 「納品履歴を見る」 ở SCR-042 (mở sẵn khách + SKU) nhưng item list SCR-042 không có item này | Sửa spec SCR-042: thêm link ở item 8.9-3 |
| G-13 | §3 | Màn thay cho trang chi tiết đơn là INFERRED | Xác nhận với screen list (giống SCR-040 #5) |
| G-14 | §5 item 12.1 | Định dạng `DRX-` + id 6 số là INFERRED, không có cột | Giả định |
| G-15 | Phụ thuộc | Hết hạn yêu cầu (job 00:05 JST, BR-DATE-02) và duyệt (SCR-044) nằm ngoài nhóm C nhưng item 12.4 hiển thị kết quả | Ghi dependency sang issue SCR-044 |

---

## 5. SCR-043 — 顧客別納品履歴照会 (Lịch sử giao theo khách)

**1. Mục đích:** tra cứu lịch sử giao đã nhận theo cặp khách–SKU; hiển thị dòng mốc so sánh 日付逆転 (nguồn duy nhất của BR-DATE-01). Chỉ đọc cho mọi vai trò đã gán.

**2. Component:** tiêu đề; mô tả mốc so sánh (tĩnh); bộ lọc (khách, SKU — gồm cả ngưng dùng 「（無効）」, mã lô, ngày giao từ/đến, chỉ dòng mốc); 検索/条件クリア;
số dòng; bảng (12.1–12.8: thời điểm giao, khách, SKU, lô (link SCR-031 / badge 移行データ), hạn + loại hạn, SL, nguồn (link SCR-053), badge 日付逆転比較基準); phân trang.

**3. Dữ liệu:**
- Đọc: view `delivery_history_list_view` (dựng trên `delivery_history_ranked`, window `partition by customer_id, sku_id order by delivered_at desc, id desc`), `customers`, `skus`, `shipments`, `orders`.
- Ghi: không. `delivery_history` chỉ ghi qua `confirm_shipment()` và job chuyển đổi dữ liệu.
- API: `GET /api/delivery-history` (sửa), `GET /api/customers`, `GET /api/skus` (thêm `includeInactive=true`).
- BR: BR-DATE-01, BR-DATE-02, BR-OUT-03, BR-TIME-01, DR-HIST-01. ADR: ADR-005, ADR-007.

**4. Validation / trạng thái:**
- Mã lô `Format_Code` (M_13/M_04), khớp phần đầu không phân biệt hoa thường; từ > đến → M_461 (không gọi API); lọc ngày theo JST.
- Cờ mốc luôn tính trên toàn bộ lịch sử (lọc ngày/lô ở view ngoài) → lọc ngày cũ + chỉ mốc có thể ra 0 dòng (đúng, M_32).
- Sắp xếp cố định `delivered_at desc, id desc`; 50 dòng/trang; tối đa 500 dòng (`500件以上` + M_462).
- Lần đầu tự tìm theo URL; đổi combobox không tự tìm.
- Dòng 移行データ (`lot_id` null): không link, badge + M_463; `shipment_id` null nhưng `lot_id` có → 「—」 + log cảnh báo server.
- Trạng thái: skeleton, rỗng M_32, M_40 (+ correlation_id)/M_41 + 再試行, 401 → SCR-001.

**5. Giờ lái xe 2024:** Không trực tiếp. Gián tiếp: dữ liệu sinh từ xác nhận xuất trên tuyến đã công bố (đã qua kiểm ADR-006).

**6. Sub-task đề xuất (9):**
- [BE] Sửa view `delivery_history_list_view` (lot_id, sku_expiry_type, is_migrated; giữ window không bị đẩy filter) + index `(delivered_at desc, id desc)` — S
- [BE] `GET /api/delivery-history` (lọc, khoảng JST, phân trang, count cắt 501, no-store) — M
- [BE] `includeInactive` cho `/api/customers`, `/api/skus` (đổi hợp đồng API dùng chung) — S
- [FE] Thanh lọc: combobox có tìm, nhận/ghi URL, validation, clear — M
- [FE] Bảng + badge mốc/移行データ + link + phân trang + số dòng/M_462 — M
- [QA] Test cờ mốc: trùng `delivered_at`, 1 lần xuất nhiều lô, lọc ngày + chỉ mốc ra 0 dòng — M
- [QA] Test lọc, biên ngày JST, giới hạn 500, dòng 移行データ — S
- [QA] Test RBAC/chỉ đọc + không có quyền ghi `delivery_history` qua RLS + hồi quy các màn khác dùng `/api/customers`, `/api/skus` — S
- [BrSE] Làm rõ: mã lô khớp phần đầu hay khớp chính xác; quy ước giờ của dữ liệu chuyển đổi — S

**7. Gap / mâu thuẫn:**
| # | Vị trí | Mô tả | Đề xuất |
|---|---|---|---|
| 1 | SCR-043 §5 item 5-2 | Khớp phần đầu là INFERRED | BrSE hỏi |
| 2 | §5 item 12.1-2 | Dữ liệu chuyển đổi chỉ có ngày → 00:00 JST (INFERRED); ảnh hưởng thứ tự "gần nhất" khi cùng ngày | Xác nhận với nhóm migration (DR-MIG-01) |
| 3 | §7 | Nói ma trận chưa có dòng cho SCR-043; role-permission-matrix.md §2 nguyên tắc 7 đã liệt kê SCR-043 là màn chỉ đọc | Spec lỗi thời, cập nhật |
| 4 | §3 vs SCR-042 | Link 「納品履歴を見る」 từ SCR-042 không có trong spec SCR-042 (xem G-12) | Sửa SCR-042 |
| 5 | §5 item 11-2 | Giới hạn 500 dòng với 3 năm lịch sử (S4-01): người dùng buộc phải lọc; không có xuất CSV | Giả định đủ cho phase 1; ghi nhận |
| 6 | §9 | Đổi `/api/customers`, `/api/skus` là thay đổi hợp đồng API dùng chung → thuộc nhóm safety-critical khi test | Test hồi quy các màn gọi 2 API này |

---

## 6. Tổng hợp

| Màn | BE | FE | QA | BrSE | Infra | Tổng |
|---|---|---|---|---|---|---|
| SCR-037 | 11 | 8 | 3 | 1 | 1 | 24 |
| SCR-040 | 3 | 4 | 3 | 1 | 0 | 11 |
| SCR-041 | 4 | 3 | 3 | 1 | 0 | 11 |
| SCR-042 | 13 | 8 | 4 | 1 | 0 | 26 |
| SCR-043 | 3 | 2 | 3 | 1 | 0 | 9 |
| **Tổng** | 34 | 25 | 16 | 5 | 1 | **81** |

Phụ thuộc chéo đáng chú ý:
- Migration `orders`/`order_lines`/`allocations` (SCR-040/041/042) nên làm 1 lần, trước các RPC.
- `evaluate_lot_for_line` dùng chung SCR-042 và SCR-044 (duyệt ngoại lệ) — xong trước SCR-044.
- `lot_status_events` + `lots.status` (SCR-037) cần trước rule 3 của SCR-042 (G-1).
- `POST /api/evidence` dùng chung SCR-031; bucket bằng chứng của SCR-037 và SCR-042 khác nhau (`quality-evidence` / `consent-evidence`).

**Status:** DONE_WITH_CONCERNS
**Summary:** Đã trích 5 màn, 81 sub-task. Không màn nào có rule giờ lái xe; rule ADR-006 thuộc SCR-060..063.
**Concerns:** G-1 (lô `on_hold` không vào tập ứng viên), G-2 (hàm đọc có tác dụng phụ), G-4 (upload Storage không nằm trong transaction) cần sửa thiết kế trước khi làm BE.
