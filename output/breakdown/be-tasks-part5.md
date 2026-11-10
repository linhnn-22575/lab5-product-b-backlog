# Backend Tasks: Product B — Yuki Cold Logistics (LAB-5)

**Date**: 2026-11-10 | **Total**: TBD

---

## E6: F04 Đơn hàng & phân bổ

### S6.1: Pipeline evaluate_lot_for_line — nguồn duy nhất của BR-ALLOC-ORDER (làm trước)

#### BE-6.1.1: Tạo migration orders, order_lines, allocations cho luồng đơn và phân bổ
orders: customer_ref + unique (customer_id, lower(customer_ref)), created_at, cancel_reason/by/at, 6 giá trị status; order_lines: agreement_id, delivery_term, line_status; allocations: allocation_evidence jsonb, exception_request_id, status cancelled.

- [ ] Migration 1 lần dùng chung SCR-040/041/042, chạy trước mọi RPC
- [ ] CHECK enum status đơn (open/partially_allocated/allocated/routed/shipped/cancelled)
- [ ] line_status open/business_review/allocated
- [ ] Chuyển dữ liệu prototype sang cột mới

**AC:**
- Migration chạy được trên dữ liệu prototype, không mất đơn
- Insert 2 đơn cùng khách với customer_ref khác hoa/thường bị unique chặn

#### BE-6.1.2: Viết evaluate_lot_for_line lớp 1–3: 消費期限, vùng nhiệt, cách ly
Khung hàm evaluate_lot_for_line(line, lot) trả first_reason + other_reasons[]; lớp 1 EXPIRED_CONSUMPTION (expiry ≤ app_today() JST), lớp 2 TEMP_ZONE_MISMATCH (vị trí vs SKU), lớp 3 QUARANTINED (status ≠ available, gồm on_hold).

- [ ] Hợp đồng trả về: first_reason, other_reasons[], evidence jsonb
- [ ] Đánh giá đủ mọi lớp để có other_reasons, không dừng ở lớp đầu
- [ ] Lớp 3 bao gồm on_hold (sửa thiết kế G-1)
- [ ] Unit test SQL cho từng lớp

**AC:**
- Lô 消費期限 = hôm nay JST trả EXPIRED_CONSUMPTION
- Lô on_hold trả QUARANTINED; lô trượt lớp 1 và 3 có first_reason = lớp 1, other_reasons chứa lớp 3

#### BE-6.1.3: Viết evaluate_lot_for_line lớp 4 cửa sổ giao và lớp 5 日付逆転
Lớp 4 DELIVERY_WINDOW 4 nhánh (tỉ lệ 1/3–1/2 theo BR-DELWIN-01, thiếu ngày SX, LABEL_DATE_ONLY, AGREEMENT_PENDING) + window_evidence; lớp 5 DATE_REVERSAL dùng last_delivered_expiry()/is_date_reversal() cùng khách+SKU.

- [ ] deadline = manufactured + floor(total_days/3 hoặc /2), so với requested_date
- [ ] Hợp đồng hiệu lực theo effective_from ≤ requested_date (ADR-003)
- [ ] Lớp 5: không có lịch sử giao → bỏ qua, không mượn lịch sử khách khác
- [ ] Unit test biên floor/deadline và hạn bằng nhau

**AC:**
- requested_date = deadline đạt, deadline + 1 ngày trả DELIVERY_WINDOW
- Lô hạn sớm hơn lần giao trước cho cùng khách+SKU trả DATE_REVERSAL; khách khác không bị ảnh hưởng

#### BE-6.1.4: Refactor get_allocation_candidates và API ứng viên dùng pipeline
get_allocation_candidates gọi evaluate_lot_for_line cho mọi lô của SKU (gồm on_hold), tính FEFO rank (expiry → received_at → id), pendingRequest; GET /api/orders/{id}/allocation-candidates?lineId=.

- [ ] Bỏ logic lọc riêng cũ, chỉ dùng pipeline
- [ ] Trả first_reason/other_reasons/window_evidence/lần giao trước mỗi lô
- [ ] Hàm chỉ đọc, không ghi (không write-on-read)

**AC:**
- Kết quả ứng viên trùng với kết quả evaluate_lot_for_line gọi trực tiếp
- Lô đủ điều kiện sắp đúng FEFO rank

#### BE-6.1.5: Viết lại allocate_lot trên pipeline: khóa, đánh giá lại, bằng chứng
allocate_lot khóa orders → order_lines → lots, gọi lại evaluate_lot_for_line trên dữ liệu đã khóa, ghi allocations + allocation_evidence, inventory_movements allocate, lots.qty_allocated, exception_events (lớp 1), idempotency; bỏ p_override_reason.

- [ ] SL 1..min(残, khả dụng) (M_05/M_426/M_427), chọn lô ngoài FEFO → M_425 + fefo_skipped
- [ ] Lô quá 賞味期限 cần cờ xác nhận, thiếu → 422 M_424
- [ ] exception_events 1 dòng/cặp khi lớp 1 chặn
- [ ] Idempotency-Key, audit_log

**AC:**
- 2 phiên phân bổ cùng lô đồng thời không vượt tồn, không deadlock
- Lô bị loại ở bất kỳ lớp nào không phân bổ được qua RPC dù gọi thẳng

### S6.2: Danh sách đơn hàng và hủy đơn (SCR-040)

#### BE-6.2.1: Tạo view order_list_view và GET /api/orders có lọc, phân trang
View order_list_view (security_invoker) gom orders, customers, order_lines, allocations active, date_reversal_exception_requests pending; GET /api/orders lọc từ khóa/khách/khoảng ngày/6 trạng thái/business_review, total.

- [ ] Từ khóa ≤ 50 (M_04), escape % và _
- [ ] Mặc định từ = hôm nay − 7, 4 trạng thái còn việc
- [ ] Sắp orders.id desc, phân trang 50, tiến độ phân bổ, cờ ngoại lệ chờ duyệt

**AC:**
- Từ khóa chứa % chỉ khớp ký tự % thật
- Số đếm tiến độ khớp số dòng đã phân bổ

#### BE-6.2.2: Viết RPC cancel_order đảo ngược phân bổ và POST /api/orders/{id}/cancel
cancel_order(p_order_id, p_reason): allocations → cancelled, inventory_movements unallocate, giảm lots.qty_allocated, yêu cầu 日付逆転 pending → expired ORDER_CANCELLED, ghi cancel_*, audit (BR-ORD-03).

- [ ] Chỉ open/partially_allocated/allocated; khác → 409 NOT_CANCELLABLE → M_402
- [ ] Lý do 10–500 (M_06)
- [ ] Khóa lots theo id tăng dần để tránh deadlock
- [ ] Toàn bộ trong 1 transaction

**AC:**
- Sau hủy, qty_allocated mỗi lô giảm đúng bằng SL phân bổ, có movement unallocate tương ứng
- Đơn vừa chuyển routed khi đang hủy trả M_402, không thay đổi dữ liệu

### S6.3: Đăng ký đơn hàng nhập tay (SCR-041)

#### BE-6.3.1: Xây API tra hợp đồng hiệu lực và kiểm trùng mã tham chiếu khách
GET /api/agreements/lookup chọn customer_sku_agreements hiệu lực (effective_from ≤ requested_date lớn nhất); GET /api/orders/check-ref kiểm trùng (customer_id, lower(customer_ref)).

- [ ] Trả window_rule, delivery_term, cờ thiếu rule / thiếu hợp đồng
- [ ] check-ref không phân biệt hoa thường, khác khách được trùng
- [ ] zod validate tham số, 403 theo quyền

**AC:**
- Có 2 phiên bản hợp đồng thì trả bản effective_from ≤ ngày yêu cầu lớn nhất
- Ref 'ABC' và 'abc' cùng khách báo trùng

#### BE-6.3.2: Viết lại RPC create_order và POST /api/orders với chuẩn lỗi chung
create_order: thêm sales_manager, validation đầy đủ ở SQL, hợp đồng từng dòng → line_status open/business_review, idempotency_keys, mã O-+sequence, audit; chuẩn hóa error body {code, messageId, params} dùng chung SCR-042.

- [ ] Ngày ≥ app_today() JST (M_409), 1–50 dòng (M_411), SKU không trùng (M_410), qty 1–99 999 (M_05)
- [ ] Không có hợp đồng → M_405 chặn; window_rule null → business_review
- [ ] Master ngưng dùng giữa chừng → M_414; ref trùng → M_408
- [ ] Gửi lại cùng Idempotency-Key trả đơn cũ

**AC:**
- Đơn có 1 dòng thiếu window_rule được tạo, dòng đó line_status = business_review
- Mọi lỗi trả body {code, messageId, params} đúng mã M_4xx

### S6.4: Phân bổ lô cho dòng đơn và gửi ngoại lệ 日付逆転 (SCR-042)

#### BE-6.4.1: Tính lại line_status và orders.status không ghi khi đọc (G-2)
Hàm recompute_order_status gọi trong allocate_lot/unallocate_allocation/cancel_order, và trigger khi customer_sku_agreements đổi để chuyển business_review ↔ open; GET không còn ghi dữ liệu.

- [ ] Đơn open → partially_allocated → allocated theo SL phân bổ
- [ ] Trigger trên customer_sku_agreements cập nhật dòng business_review liên quan
- [ ] Xóa đoạn tính lại trong GET /api/orders/{id}

**AC:**
- Mở SCR-042 nhiều lần không tạo bản ghi audit/UPDATE nào
- Bổ sung window_rule cho hợp đồng thì dòng business_review chuyển open

#### BE-6.4.2: Viết RPC unallocate_allocation và mở rộng GET /api/orders/{id}
unallocate_allocation + POST /api/allocations/{id}/cancel (khóa, movement unallocate, giảm qty_allocated, lý do bắt buộc, audit); GET /api/orders/{id} trả today, agreement, line_status, evidence, yêu cầu ngoại lệ.

- [ ] Chỉ khi đơn partially_allocated/allocated (M_441); routed/shipped → M_430
- [ ] Đảo ngược đúng phân bổ từ ngoại lệ đã duyệt (theo Q&A-B04)
- [ ] Gọi recompute_order_status sau khi hủy

**AC:**
- Hủy phân bổ trả lại đúng SL khả dụng cho lô và có movement unallocate
- Đơn routed gọi hủy phân bổ nhận lỗi, dữ liệu không đổi

#### BE-6.4.3: Viết create_date_reversal_request với upload trước, ghi ref sau (G-4)
POST /api/date-reversal-requests multipart: upload file vào đường tạm consent-evidence trước, rồi RPC create_date_reversal_request kiểm lại DATE_REVERSAL qua evaluate_lot_for_line và ghi ref; GET /api/date-reversal-requests?orderId= dùng chung SCR-044.

- [ ] SL ≤ 残 và ≤ khả dụng (M_442), lý do 10–500, file ≤ 10MB hoặc số biên bản 1–100 (M_434/M_435)
- [ ] Trùng pending → M_436; chỉ khi first_reason = DATE_REVERSAL; không tạo phân bổ
- [ ] RPC lỗi → xóa file tạm; file mồ côi do job dọn
- [ ] Chỉ sales_planner gửi được

**AC:**
- RPC thất bại sau upload không để lại bản ghi yêu cầu, file tạm bị xóa
- Lô không bị loại ở lớp 5 gửi yêu cầu nhận lỗi

### S6.5: Lịch sử giao theo khách (SCR-043)

#### BE-6.5.1: Sửa delivery_history_list_view và GET /api/delivery-history, includeInactive
View delivery_history_list_view trên delivery_history_ranked (lot_id, sku_expiry_type, is_migrated; cờ mốc tính trên toàn lịch sử) + index (delivered_at desc, id desc); GET /api/delivery-history; thêm includeInactive cho /api/customers, /api/skus.

- [ ] Lọc ngày/mã lô ở ngoài window để không đẩy filter vào (cờ mốc không đổi)
- [ ] Khoảng ngày JST, mã lô khớp phần đầu không phân biệt hoa thường, 50/trang, count cắt 501, no-store
- [ ] includeInactive mặc định false, không đổi hành vi màn khác

**AC:**
- Lọc ngày cũ + chỉ dòng mốc có thể trả 0 dòng (cờ mốc vẫn theo toàn lịch sử)
- Các màn đang gọi /api/customers, /api/skus không đổi kết quả khi không truyền includeInactive

