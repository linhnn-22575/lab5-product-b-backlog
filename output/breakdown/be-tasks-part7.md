# Backend Tasks: Product B — Yuki Cold Logistics (LAB-5)

**Date**: 2026-11-10 | **Total**: TBD

---

## E7: F05 Kiểm trước xuất

### S7.1: Xác nhận xuất hàng an toàn qua RPC confirm_shipment

#### BE-7.1.1: Tạo migration xuất hàng và hàm effective_temp_policy
Thêm cột shipments (cargo_temp_c, seal_no, route_version_id, policy_version_id), shipment_checks (input_method, manual_reason, scanned_sku_code), deviations (measure_type, order_id), idempotency_keys nếu chưa có; viết hàm effective_temp_policy(p_zone, p_date) dùng chung SCR-022.

- [ ] Migration up/down cho 4 bảng
- [ ] Hàm effective_temp_policy đọc temp_zone_policy_versions theo ngày
- [ ] Test biên: bằng biên = đạt, 冷凍 không có cận dưới
- [ ] Cập nhật type sinh từ Supabase

**AC:**
- Migration chạy sạch trên DB có dữ liệu LAB-2
- effective_temp_policy trả đúng phiên bản hiệu lực ở ngày đổi chính sách
- Unit test biên nhiệt độ pass

#### BE-7.1.2: Tạo view outbound_check_lines_view tính hạn, đảo ngày, ngoại lệ
View security_invoker outbound_check_lines_view ghép allocations/lots/skus với last_delivered_expiry(), is_date_reversal(), app_today() và date_reversal_exception_requests để trả trạng thái 消費期限/賞味期限/đảo ngày cho từng dòng.

- [ ] security_invoker = true
- [ ] Cột consumption_expired, best_before_expired, date_reversal, exception_status
- [ ] "Hôm nay" lấy từ app_today()
- [ ] Index cho join theo order_id

**AC:**
- Đơn có lô 消費期限 = hôm nay hiện consumption_expired = true
- Vai trò chỉ xem đọc được view, RLS không rò đơn ngoài quyền

#### BE-7.1.3: Viết confirm_shipment phần 1: quyền, idempotency, kiểm bản tuyến published
RPC confirm_shipment bước 1–5: thêm warehouse_lead vào outbound:write + has_role trong RPC, idempotency_keys, khóa đơn, khóa lô theo id; SỬA THIẾT KẾ: kiểm đơn thuộc route_version status='published' hiện hành của tuyến, không dùng routes.status/current_version (quyết định 1).

- [ ] has_role cho warehouse/warehouse_lead/admin
- [ ] Idempotency-Key trùng trả lại kết quả cũ
- [ ] Tìm bản published mới nhất, so với route_version_id client gửi → M_22 nếu lệch
- [ ] Khóa đơn và lô theo thứ tự id tránh deadlock

**AC:**
- Tuyến đang có bản draft (routes vẫn published) vẫn xuất được theo bản published
- Đơn không thuộc bản published → M_465/M_466
- Gọi 2 lần cùng key chỉ tạo 1 shipment

#### BE-7.1.4: Viết confirm_shipment phần 2: gom lỗi kiểm a–j không raise
Gom mọi problem b–j (xe/vùng, lô/SKU, SL, cách ly, 消費期限, 賞味期限 cảnh báo, đảo ngày + ngoại lệ approved, nhiệt xe và hàng, niêm phong); INSERT deviations (mỗi giá trị ngoài ngưỡng 1 dòng) và exception_events rồi trả blocked, transaction vẫn commit.

- [ ] Trả danh sách problem có allocationId/field + mã M_xx
- [ ] Deviation riêng cho nhiệt xe và nhiệt hàng
- [ ] 消費期限 ≤ hôm nay ghi exception_events
- [ ] 賞味期限 quá chỉ là warning, không chặn

**AC:**
- Xe + hàng cùng ngoài ngưỡng → 2 deviation được lưu dù bị chặn
- Bằng biên nhiệt độ = đạt
- Kết quả blocked có đủ mọi lỗi, không dừng ở lỗi đầu

#### BE-7.1.5: Viết confirm_shipment phần 3: ghi xuất kho và trạng thái đơn
Khi không có lỗi chặn: INSERT shipments, shipment_checks, delivery_history (thứ tự expiry, id), inventory_movements 'ship', cập nhật lots depleted + lot_status_events, orders.status='shipped', audit_log.

- [ ] shipments lưu route_version_id published và policy_version_id
- [ ] delivery_history theo thứ tự expiry rồi id
- [ ] Lô về 0 → depleted + lot_status_events
- [ ] audit_log cho shipment

**AC:**
- Sau xuất tồn lô giảm đúng SL, có movement 'ship'
- Đơn chuyển shipped, lần xuất tiếp bị chặn trạng thái
- delivery_history dùng được cho kiểm đảo ngày lần sau

### S7.2: API kiểm trước xuất

#### BE-7.2.1: Sửa giờ xuất phát thành planned_arrival + service_min của depot đầu
SỬA THIẾT KẾ (053 gap #2): giờ xuất phát hiển thị = route_stops.planned_arrival + service_min của depot đầu (始業 + 出庫前作業) thay cho planned_arrival; đặt trong 1 hàm SQL dùng chung cho 2 API GET.

- [ ] Hàm route_departure_time(route_version_id)
- [ ] Đọc bản published hiện hành, không đọc current_version
- [ ] Cập nhật spec SCR-053 logic-10-4
- [ ] Unit test với service_min = 0 và 30

**AC:**
- Depot đầu 06:00 + service 30 phút → hiển thị 06:30
- Giờ trùng với 出庫 hiển thị ở SCR-060

#### BE-7.2.2: Viết API GET pending-and-done và GET outbound-check
GET /api/shipments/pending-and-done (tuyến/xe/tài xế, giờ xuất phát, canStartCheck, blockReason, lọc ngày/tuyến/ルート未割当) và GET /api/orders/[id]/outbound-check (DTO route, policy, dateReversal, shipment.checks) đọc từ outbound_check_lines_view.

- [ ] Lọc ngày xuất + tuyến + unassigned
- [ ] canStartCheck/blockReason theo ma trận 053#8
- [ ] DTO trả route_version_id published để client gửi lại
- [ ] 403 cho vai trò không có quyền xem

**AC:**
- Đơn thuộc tuyến chưa published có canStartCheck=false + blockReason
- DTO outbound-check đủ trường cho bảng kiểm dòng và khung 積込確認

#### BE-7.2.3: Viết API POST /api/shipments với Idempotency-Key bắt buộc
POST /api/shipments: zod validate body 7 tham số, header Idempotency-Key bắt buộc, gọi confirm_shipment, map kết quả 201 / 409 OUTBOUND_BLOCKED (kèm problems) / 409 trạng thái / 400 / 403 → mã M_xx.

- [ ] Schema zod cho checks, xe, niêm phong, 2 nhiệt độ
- [ ] Thiếu header → 400
- [ ] Map problems sang allocationId/field
- [ ] Log lỗi 500 không lộ chi tiết DB

**AC:**
- Bị chặn trả 409 kèm đủ danh sách lỗi
- Gửi lại cùng key trả cùng kết quả 201

