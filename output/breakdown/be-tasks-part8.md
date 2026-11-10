# Backend Tasks: Product B — Yuki Cold Logistics (LAB-5)

**Date**: 2026-11-10 | **Total**: TBD

---

## E8: F07 Lập tuyến & công bố (phần không thuộc luật giờ lái)

### S8.1: Dựng nền dữ liệu và phân quyền F07

#### BE-8.1.1: Tạo migration bảng tuyến lõi: xe, tài xế, routes, versions, stops, segments
Migration vehicles, drivers, routes (+updated_at, current_version), route_versions (status draft/created/checked/published/superseded/discarded, change_category, change_reason, driver_rule_version_id, published_at/by), route_stops (+travel_min/source/fetched_at/manual_reason, place_name), route_segments (auto_inserted) + unique partial (ngày, xe)/(ngày, tài xế). E9 dùng route_versions.driver_rule_version_id và route_segments.auto_inserted.

- [ ] Enum route_versions.status đủ 6 giá trị
- [ ] segment_type bỏ 'rest' (060 gap #7)
- [ ] Unique partial index xe/tài xế theo ngày bỏ qua tuyến cancelled
- [ ] Seed xe/tài xế mẫu cho dev

**AC:**
- Migration up/down chạy sạch
- Tạo 2 tuyến cùng ngày cùng tài xế bị DB chặn
- Type Supabase sinh lại không lỗi build

#### BE-8.1.2: Tạo migration rejections, travel_time_cache và cột khách hàng/đơn
Migration route_assignment_rejections, travel_time_cache (key from, to, slot 1h, fetched_at), customers (+delivery_window_*, default_service_min), enum orders.status thêm routed/partially_allocated/cancelled.

- [ ] Index tra cache theo (from, to, slot)
- [ ] default_service_min mặc định 20
- [ ] Thêm giá trị enum không phá dữ liệu LAB-2
- [ ] Cập nhật type

**AC:**
- Đơn cũ giữ nguyên trạng thái sau migration
- Ghi/đọc cache theo key chạy được

#### BE-8.1.3: Thêm vai trò dispatcher, transport_manager, auditor và RLS tuyến
Thêm vai trò dispatcher, transport_manager, auditor + quyền route:write vào role-permission; RLS chỉ SELECT trên routes/route_versions/route_stops/route_segments, ghi qua RPC security definer có has_role.

- [ ] Cập nhật bảng quyền + middleware Next.js
- [ ] Policy SELECT cho vai trò xem (gồm warehouse cho SCR-053)
- [ ] Chặn INSERT/UPDATE trực tiếp từ client
- [ ] Test quyền từng vai trò

**AC:**
- auditor đọc được tuyến nhưng gọi RPC ghi bị 403
- Client không ghi trực tiếp được bảng tuyến

### S8.2: Gán đơn, sắp điểm dừng và dựng segment tuyến

#### BE-8.2.1: Viết get_route_plan và create_route kèm API GET plan, POST routes
RPC get_route_plan(p_date) trả đơn chưa gán (lý do 1–3 tính, 4–6 đọc route_assignment_rejections, mapStatus) + GET /api/routes/plan; RPC create_route + POST /api/routes (Idempotency-Key, 2 depot stop, segment 出庫前/帰庫後).

- [ ] Ngày < hôm nay → M_618
- [ ] Xe/tài xế trùng → M_603/M_605
- [ ] Tạo version đầu status created
- [ ] Idempotency-Key cho POST

**AC:**
- Đơn nhiều vùng nhiệt hiện lý do MIXED_TEMP_ZONE
- Tạo tuyến sinh đủ 2 depot stop và segment pre/post

#### BE-8.2.2: Viết assign_orders_to_route kiểm 6 lý do và lưu rejections
RPC assign_orders_to_route + POST /api/routes/{id}/assign: kiểm từng đơn theo thứ tự NOT_ALLOCATED → MIXED_TEMP_ZONE → NO_VEHICLE_ZONE → TEMP_ZONE_MISMATCH → CAPACITY_EXCEEDED → SERVICE_HOURS, M_602 đơn đã ở tuyến khác, lưu rejections 4–6, đơn → routed, checked → created qua M_606.

- [ ] Khóa đơn chống gán đồng thời
- [ ] Lưu bền lý do 4–6
- [ ] Tuyến checked sửa cần confirm → về created
- [ ] Chỉ sửa được version draft/created/checked

**AC:**
- Hai dispatcher gán cùng đơn đồng thời → 1 thành công, 1 M_602
- Tải 100% vượt → CAPACITY_EXCEEDED, đơn còn ở bảng chưa gán

#### BE-8.2.3: Viết build_route_segments dựng drive/wait/service và giờ đến
Hàm build_route_segments(route_version_id) dựng segment drive/wait/service/break thủ công, depot pre/post, planned_arrival từng điểm; KHÔNG tự chèn nghỉ — module chuỗi lái BR-DRV-11/21 của E9 trả danh sách nghỉ để hàm này ghi với auto_inserted=true.

- [ ] Thứ tự segment theo seq
- [ ] Chờ khi đến sớm hơn khung khách
- [ ] Nhận input danh sách nghỉ chèn từ ngoài (mặc định rỗng)
- [ ] Unit test 3 điểm dừng

**AC:**
- Giờ đến từng điểm = giờ trước + travel_min + service
- Gọi lại 2 lần cho cùng version ra kết quả giống nhau

#### BE-8.2.4: Viết save_route_stops có khóa lạc quan, kiểm BR-TIME-02
RPC save_route_stops + PUT /api/routes/{id}/stops: khóa lạc quan updated_at (M_22), ghi stops, lấy thời gian di chuyển cho đoạn thiếu, gọi build_route_segments, rollback nếu ngoài 05:00–23:00 (M_614), cảnh báo khung khách M_615, checked → created, audit. E9 gắn bước chèn nghỉ vào đây.

- [ ] Validate pre/post 0–120, service 5–180, nghỉ 10–180
- [ ] Rollback toàn bộ khi vi phạm BR-TIME-02
- [ ] Từ chối khi version không phải draft/created/checked (M_607)
- [ ] audit_log giá trị cũ/mới

**AC:**
- Dời giờ làm điểm giao 23:05 → rollback, M_614
- Lưu đè với updated_at cũ → M_22

### S8.3: Tích hợp bản đồ IF-MAP-01 và thông báo IF-MAIL-01

#### BE-8.3.1: Viết adapter IF-MAP-01 batch, timeout 10s, cache 7 ngày
Adapter IF-MAP-01: gọi batch, timeout 10s, cache travel_time_cache key (from, to, slot 1h) 7 ngày, fallback cache → lỗi (正常/キャッシュ使用中 M_621/障害 M_620), đếm M_623, ghi travel_source/fetched_at vào route_stops.

- [ ] Interface tách để mock khi test
- [ ] Fallback cache khi timeout
- [ ] Trả trạng thái dịch vụ cho badge
- [ ] Không log API key

**AC:**
- Timeout có cache → dùng cache, trạng thái キャッシュ使用中
- Không cache + lỗi → 障害, cho nhập tay

#### BE-8.3.2: Viết API POST travel-times/refresh không ghi đè đoạn nhập tay
POST /api/routes/{id}/travel-times/refresh: lấy lại thời gian di chuyển qua adapter, không ghi đè đoạn manual khi chưa confirm (M_31), audit giá trị cũ, dựng lại segment, checked → created.

- [ ] Cờ confirm ghi đè manual
- [ ] Audit từng đoạn đổi
- [ ] Gọi build_route_segments sau khi cập nhật
- [ ] Trả số đoạn dùng cache/manual

**AC:**
- Không confirm → đoạn manual giữ nguyên
- Tuyến checked sau refresh về created

### S8.5: Quản lý phiên bản tuyến, công bố và hủy (SCR-062)

#### BE-8.5.1: Viết bước ghi công bố (supersede, outbox) và API GET versions
Hàm nội bộ apply_route_publish(version_id): version → published, bản published trước → superseded, routes.status='published', current_version, enqueue outbox route_published/route_changed, audit; E9 publish_route gọi hàm này sau khi qua cổng BR-DRV-20/22/23. Kèm GET versions (prePublish, notification, kpi).

- [ ] Không expose trực tiếp cho client
- [ ] Lần đầu → route_published, lần sau → route_changed
- [ ] Khóa route chống công bố đồng thời
- [ ] GET versions trả trạng thái outbox

**AC:**
- Sau công bố bản 2, bản 1 là superseded và chỉ 1 bản published
- Có đúng 1 dòng outbox mỗi lần công bố

#### BE-8.5.2: Viết create_route_version giữ tuyến published khi có bản nháp
RPC create_route_version + POST versions: lý do 10–500 + 区分 7 giá trị, copy stops/segments sang bản draft, Idempotency-Key; SỬA THIẾT KẾ (quyết định 1): routes.status giữ 'published', bản published không đổi, SCR-060 sửa trên bản draft.

- [ ] Chặn khi đã có draft mở
- [ ] Copy đủ stops/segments
- [ ] Không đổi routes.status
- [ ] in_progress/completed/cancelled → M_646

**AC:**
- Sau tạo nháp, kho vẫn xuất theo bản published (E7)
- Bản published không bị sửa nội dung

#### BE-8.5.3: Viết discard_route_draft và cancel_route chặn khi có đơn đã xuất
RPC discard_route_draft (draft → discarded, khôi phục trạng thái đơn theo bản published, không thông báo) và cancel_route (lý do bắt buộc, đơn routed → allocated, outbox nếu đã công bố; CHẶN nếu có đơn shipped trên tuyến) + 2 API POST.

- [ ] Khôi phục đơn được gán/gỡ trong nháp
- [ ] Kiểm orders.status='shipped' trước khi hủy
- [ ] Outbox route_cancelled chỉ khi từng published
- [ ] Audit cả 2 thao tác

**AC:**
- Tuyến có 1 đơn đã xuất → hủy bị từ chối
- Bỏ nháp đưa đơn về đúng trạng thái theo bản published

#### BE-8.5.4: Viết route_version_diff và view KPI đổi tuyến sau công bố
Hàm route_version_diff ghép theo order_id / place_name+vị trí / depot + GET diff; view route_post_publish_change_kpi (ngưỡng 15 phút giả định) + GET KPI.

- [ ] Diff đúng 2 bản, khác → M_649
- [ ] Phân loại thêm/bớt/đổi giờ/đổi thứ tự
- [ ] Ngưỡng KPI là tham số
- [ ] Liệt kê đơn ảnh hưởng

**AC:**
- Đổi thứ tự 2 điểm hiện đúng 2 dòng thay đổi
- KPI tính đúng trên dữ liệu mẫu 3 tuyến

