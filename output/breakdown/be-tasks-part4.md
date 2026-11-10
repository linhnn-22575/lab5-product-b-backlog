# Backend Tasks: Product B — Yuki Cold Logistics (LAB-5)

**Date**: 2026-11-10 | **Total**: TBD

---

## E4: F02 Nhập hàng

### S4.1: Tạo phiếu nhập và ghi kết quả kiểm từng dòng (SCR-022)

#### BE-4.1.1: Mở rộng inbound_receipts, inbound_lines và lots cho kiểm hàng nhập
Migration inbound_receipts.supplier_id, cột mới inbound_lines (NSX, bao bì, ghi chú, location_id, mã truy xuất, photo_ref, photo_sha256, policy_version_id, temp_out_of_range, lot_id), lots (location_id, manufactured_date); CHECK beef 10 chữ số.

- [ ] Cột + FK tới suppliers/locations/policy versions
- [ ] CHECK beef 10 chữ số, SL 1..99 999, nhiệt −50..50
- [ ] Trigger 0800 B cập nhật theo cột mới
- [ ] Grant cột theo vai trò inbound:write

**AC:**
- Dòng thiếu P0 (chỉ có SKU) vẫn insert được
- Mã beef sai độ dài bị DB từ chối

#### BE-4.1.2: Viết API danh sách, tạo phiếu nhập và API master cho ô chọn
View inbound_receipt_list_view + GET /api/inbound-receipts (lọc, escape LIKE, ngày M_225, phân trang 50, đếm thiếu P0/ngoài ngưỡng); POST theo supplier_id (422 M_218); GET /api/suppliers, /api/locations, /api/skus thêm traceLane.

- [ ] View + GET lọc/phân trang
- [ ] POST phiếu + validate supplier active
- [ ] GET suppliers/locations (zone, active, quarantine)
- [ ] GET skus trả traceLane

**AC:**
- Khoảng ngày đảo ngược trả 400 M_225
- Supplier ngưng dùng trả 422 M_218

#### BE-4.1.3: Viết API thêm/sửa/xóa dòng nhập và upload ảnh kiểm hàng
POST/PATCH/DELETE lines: zod cho phép thiếu P0, refine M_203/M_221/M_222, map 409 M_211 / 422 M_210; POST …/photo: upload bucket private, SHA-256 server-side ghi photo_sha256 + audit_log, thay ảnh giữ ảnh cũ, signed URL 5 phút.

- [ ] Zod dòng + refine ngày/bao bì
- [ ] Chặn sửa khi phiếu đã confirmed (409 M_211)
- [ ] Upload ≤10MB JPG/PNG/HEIC (M_223)
- [ ] SHA-256 vào cột + audit_log

**AC:**
- Sửa dòng của phiếu confirmed trả 409 M_211
- Ảnh upload có photo_sha256 khớp file gốc

### S4.2: Kiểm nhiệt 2 lớp và xác nhận phiếu idempotent (SCR-022)

#### BE-4.2.1: Viết hàm inbound_receipt_check và GET chi tiết phiếu kèm kết quả kiểm
Hàm inbound_receipt_check(p_receipt_id) trả blocking + warnings (lineNo, messageId, params): P0 M_202, lớp B M_204, -Q M_212/M_213, ngưng M_210/M_215, trùng lô M_224/M_206, thiếu policy M_214, cảnh báo M_205/M_216/M_219/M_220; mở rộng view + GET /{id}.

- [ ] Ngưỡng theo ngày JST của arrived_at
- [ ] Đủ nhánh chặn + cảnh báo, sắp theo dòng
- [ ] Mở rộng inbound_lines_with_temp_check
- [ ] Test SQL từng nhánh

**AC:**
- Phiếu nhiều lỗi trả toàn bộ lỗi, không dừng ở lỗi đầu
- Dòng ngoài ngưỡng chỉ là cảnh báo, không chặn

#### BE-4.2.2: Viết RPC confirm_inbound_receipt idempotent và route POST confirm
RPC 8 bước: role, idempotency_keys (cùng key → kết quả cũ, key khác sau confirm → 409 M_208), for update, NO_LINES, check (422 CHECK_FAILED), sinh lots + lot_status_events + inventory_movements + deviations, snapshot dòng, audit chung correlation_id; route bắt buộc header Idempotency-Key.

- [ ] Idempotency theo key + ref_id phiếu
- [ ] Sinh lô + sự kiện create/quarantine + movement + deviation
- [ ] Cách ly lô ngoài ngưỡng / thiếu trace vào vị trí -Q
- [ ] Route map 409/422/403/404/5xx

**AC:**
- Gửi lại cùng key trả 200 với cùng kết quả, không sinh lô trùng
- Lô ngoài ngưỡng có status quarantine và 1 deviation temp_out_of_range

## E5: F03 Tồn kho & lô

### S5.1: Tra cứu tồn kho theo lô (SCR-030)

#### BE-5.1.1: Mở rộng lot_stock_view và thêm bảng tham số hệ thống app_parameters
Mở rộng view lot_stock_view (security_invoker) với temp_zone, NSX, vị trí, supplier, expiry_flag, pending_disposal và công thức qty_available mới; tạo bảng app_parameters (có audit) chứa consumption_warning_days = 3.

- [ ] Migration app_parameters (key, value, updated_by/at) + audit, seed consumption_warning_days=3
- [ ] View: left join chuỗi inbound_lines → inbound_receipts → suppliers, cờ pending_disposal
- [ ] expiry_flag CASE theo app_today() JST; qty_available = 0 khi status ≠ available hoặc 消費期限到達
- [ ] Hàm dùng chung needs_relocation (要移動) cho quarantine và on_hold, dùng lại ở SCR-031/037

**AC:**
- days_left −1/0/1/3/4 cho ra đúng nhãn 消費期限到達/間近/賞味期限切れ
- Đổi consumption_warning_days trong app_parameters thì view đổi theo, không cần sửa code
- Lô on_hold ở khu thường hiện cờ 要移動 giống lô quarantine

#### BE-5.1.2: Xây RPC search_lot_stock và GET /api/lots với 10 bộ lọc, đạt ≤ 2s
RPC search_lot_stock(p_filter jsonb, p_page, p_page_size) security invoker trả rows + total + summary; GET /api/lots validate zod 10 filter; thêm index và kiểm hiệu năng trên dữ liệu 3 năm.

- [ ] zod 10 filter, status csv mặc định 3 trạng thái, escape LIKE, hạn từ ≤ hạn đến (M_303)
- [ ] Sắp FEFO cố định (hạn → ngày nhập → id), phân trang 50, summary trên toàn bộ kết quả
- [ ] Index lots(location_id), lots(lower(lot_code) text_pattern_ops)
- [ ] Sinh dữ liệu 3 năm, EXPLAIN ANALYZE, ghi kết quả

**AC:**
- Tổng số lô/tồn/khả dụng khớp toàn bộ kết quả, không chỉ trang hiện tại
- Truy vấn 50 dòng trên dữ liệu 3 năm ≤ 2s
- Vai trò chưa gán gọi API nhận 403

### S5.2: Chi tiết lô, lịch sử sự kiện và cách ly thủ công (SCR-031)

#### BE-5.2.1: Tạo view lot_event_timeline và API chi tiết lô, lịch sử sự kiện
View lot_event_timeline union inventory_movements + lot_status_events gộp theo correlation_id, map 10 loại; GET /api/lots/{id}/events (keyset occurred_at,id) và GET /api/lots/{id} to-be có allowedActions.

- [ ] View map 10 loại sự kiện theo enum dùng chung đã chốt (G31-1), index (lot_id, occurred_at)
- [ ] GET events: tham số before, kinds, limit 50
- [ ] GET lot: thông tin nhập chụp lại + phiên bản ngưỡng nhiệt, deviations, pendingDisposal
- [ ] allowedActions theo vai trò × state machine (admin không có quarantine)

**AC:**
- Phân trang keyset không trùng/không sót thẻ khi có sự kiện cùng occurred_at
- Các sự kiện cùng correlation_id trả về như 1 nhóm
- allowedActions chứa quarantine chỉ khi vai trò quality/warehouse_lead và lô available

#### BE-5.2.2: Viết RPC quarantine_lot và API cách ly, API tải bằng chứng dùng chung
RPC quarantine_lot (role, idempotency, FOR UPDATE, kiểm trạng thái + phân bổ, status event, gắn deviation, audit) + POST /api/lots/{id}/quarantine; POST /api/evidence multipart dùng chung SCR-031/037.

- [ ] M_301 INVALID_TRANSITION, M_302 LOT_ALLOCATED khi qty_allocated > 0, 422 deviation không hợp lệ
- [ ] Lý do 10–500 lưu tiền tố MANUAL:, Idempotency-Key gửi lại không cách ly 2 lần
- [ ] POST /api/evidence: PDF/JPG/PNG ≤ 10MB (M_316), trả evidence_ref ≤ 200, signed URL 5 phút khi xem
- [ ] Ghi audit_log + correlation_id

**AC:**
- Cách ly đồng thời với allocate_lot: lô vừa cách ly không phân bổ được
- Gửi lại cùng Idempotency-Key trả kết quả cũ, chỉ 1 lot_status_events

### S5.3: Máy trạng thái lô: cách ly, 保留, giải phóng, hủy có duyệt 2 người (SCR-037)

#### BE-5.3.1: Tạo migration máy trạng thái lô, lot_status_events và lot_disposal_requests
lots.status 5 giá trị, bảng lot_status_events append-only (trigger chặn UPDATE/DELETE, cột evidence_note, reevaluation_*), locations.is_quarantine + seed C-Q/F-Q, bảng lot_disposal_requests, tham số lot_disposal_dual_approval_qty=100.

- [ ] Chốt 1 enum event_type/movement_type dùng chung SCR-022/031/037 (gồm allocate/unallocate/dispose)
- [ ] lot_disposal_requests: request_no DSP-####, CHECK decided_by ≠ requested_by, unique partial pending, trigger khóa sau quyết định
- [ ] Seed lot_disposal_dual_approval_qty vào app_parameters (chỉ admin sửa, có audit)
- [ ] Bước dọn dữ liệu cũ: lô quarantine có qty_allocated > 0 từ prototype

**AC:**
- UPDATE/DELETE trên lot_status_events bị DB từ chối
- Insert yêu cầu hủy với decided_by = requested_by bị CHECK chặn
- Migration chạy được trên dữ liệu prototype, không còn lô quarantine có phân bổ

#### BE-5.3.2: Tạo quarantine_lot_view, GET /api/lots/quarantine và phân quyền lot:*
View quarantine_lot_view + GET /api/lots/quarantine (zoneCounts, ambientHasQuarantineLocation, allowedActions); permission lot:release/lot:dispose cho quality, RLS, has_role trong RPC.

- [ ] View gồm lý do/thời điểm cách ly, deviation, yêu cầu hủy pending, reevaluation_due
- [ ] allowedActions theo state machine; khóa khi có yêu cầu pending (M_321) hoặc qty_allocated > 0
- [ ] role-permissions: quality thao tác, warehouse_lead/auditor chỉ xem, còn lại 403

**AC:**
- zoneCounts khớp số lô từng tab 冷蔵/冷凍/常温
- Vai trò ngoài 3 vai trò gọi API nhận 403

#### BE-5.3.3: Viết RPC hold_lot, release_lot và API 保留/giải phóng lô
RPC hold_lot (kế hoạch, ngày tái đánh giá) và release_lot (kiểm vị trí đích, movement move qty 0, đóng deviation) security definer, 1 transaction, FOR UPDATE, idempotency, audit; POST /api/lots/{id}/hold|release.

- [ ] Chuyển hợp lệ: quarantine → on_hold/available; on_hold → available; sai → M_301
- [ ] hold: kế hoạch 10–500 (M_325), ngày dự kiến ≥ hôm nay JST (M_326)
- [ ] release: vị trí đích bắt buộc khi ở khu -Q, active, không -Q, đúng vùng (M_204/M_313)
- [ ] Lý do 10–500, bằng chứng file hoặc evidence_no lưu cột riêng

**AC:**
- on_hold → quarantine bị chặn M_301
- Release ghi 1 lot_status_events + 1 inventory_movements move và đóng deviation liên quan

#### BE-5.3.4: Viết RPC dispose_lot, decide_lot_disposal và API hủy lô duyệt 2 người
dispose_lot hủy toàn bộ tồn: ≤ ngưỡng hủy ngay (movement dispose), > ngưỡng tạo lot_disposal_requests pending; decide_lot_disposal duyệt/từ chối; POST …/dispose, POST /api/lot-disposal-requests/{id}/decision, GET danh sách/chi tiết (canDecide).

- [ ] Đọc ngưỡng lot_disposal_dual_approval_qty từ app_parameters
- [ ] Duyệt: người duyệt ≠ người gửi (M_311), ALREADY_DECIDED (M_312), qty đổi → INVALID_TRANSITION
- [ ] Từ chối cần comment 10–500 (M_318)
- [ ] FOR UPDATE, idempotency, correlation_id, audit

**AC:**
- qty 100 hủy ngay, qty 101 tạo yêu cầu pending (với ngưỡng 100)
- 2 người duyệt cùng lúc: chỉ 1 thành công, người kia nhận M_312

