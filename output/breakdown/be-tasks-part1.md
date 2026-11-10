# Backend Tasks: Product B — Yuki Cold Logistics (LAB-5)

**Date**: 2026-11-10 | **Total**: TBD

---

## E1: Nền tảng & sửa prototype trái RFP

### S1.1: Tạo migration dữ liệu dùng chung cho mọi feature

#### BE-1.1.1: Tạo audit_log append-only có correlation_id và trigger audit chung
Migration bảng audit_log (actor, action, entity, before/after jsonb, correlation_id) chặn UPDATE/DELETE, hàm audit_write() và trigger audit chung để các RPC gọi (G-17, NFR-AUD-01, ADR-007).

- [ ] Bảng audit_log + index (entity, created_at), (correlation_id)
- [ ] Trigger chặn UPDATE/DELETE kể cả role authenticated
- [ ] Hàm audit_write() nhận correlation_id từ RPC
- [ ] RLS: SELECT cho admin/auditor, không INSERT trực tiếp

**AC:**
- UPDATE/DELETE audit_log trả lỗi ở mọi role ứng dụng
- Một RPC ghi nhiều bản ghi audit dùng chung 1 correlation_id

#### BE-1.1.2: Tạo inventory_movements, lot_status_events và enum trạng thái lô, đơn
Migration inventory_movements append-only thay cập nhật trực tiếp qty_on_hand, lot_status_events (event_type gồm create), enum lots 5 trạng thái và orders thêm partially_allocated/routed/cancelled (G-09/10/24).

- [ ] inventory_movements append-only + view số dư theo lô
- [ ] lot_status_events với event_type create/quarantine/hold/release/dispose
- [ ] Enum lots: available, quarantine, on_hold, disposed, depleted
- [ ] Enum orders mở rộng + migrate dữ liệu prototype
- [ ] Chặn DELETE cứng trên lots, inventory_movements, lot_status_events; sửa sai = bút toán đảo / sự kiện mới tham chiếu bản gốc (BR-INV-03)

**AC:**
- Số dư lô tính từ inventory_movements khớp qty_on_hand của seed sau migrate
- Không UPDATE/DELETE được inventory_movements và lot_status_events
- DELETE trên lots/inventory_movements/lot_status_events bị từ chối ở mọi role ứng dụng; sửa sai tạo bút toán đảo có tham chiếu bản gốc

#### BE-1.1.3: Tạo master locations, suppliers và bảng deviations, idempotency_keys
Migration locations (zone, is_quarantine, mã -Q), suppliers + migrate inbound_receipts.supplier_name, deviations (enum temp_out_of_range/trace_missing/zone_mismatch), idempotency_keys có ref_id + request_hash (G-07/08/18/22).

- [ ] locations + seed vị trí thường và -Q theo vùng
- [ ] suppliers + migrate supplier_name (hậu tố 未登録)
- [ ] deviations chốt enum theo DB design
- [ ] idempotency_keys thêm ref_id, request_hash

**AC:**
- Phiếu nhập prototype đều có supplier_id sau migrate
- Cùng key với ref_id khác bị phát hiện được bằng truy vấn

### S1.2: Chuyển message sang mã M_xx và giao diện tiếng Nhật

#### BE-1.2.1: Thay raise exception tiếng Việt bằng P0001 kèm hint mã M_xx
Sửa mọi RPC/trigger prototype (0500–0800) raise lỗi errcode P0001 + hint M_xx, viết helper API mapDbError() đổi 23505/P0001/PGRST116 sang mã message.

- [ ] Liệt kê toàn bộ raise exception trong migration prototype
- [ ] Đổi sang P0001 + hint M_xx, detail chứa tham số
- [ ] Helper mapDbError() dùng chung cho route handler
- [ ] Unit test mapping

**AC:**
- grep không còn chuỗi tiếng Việt trong SQL
- API trả { messageId, params } cho mọi lỗi nghiệp vụ

### S1.3: Mở rộng 9 vai trò, RBAC và tách người lập / người duyệt

#### BE-1.3.1: Mở rộng profiles 9 vai trò và viết current_app_role, has_role
Migration profiles: CHECK role 9 giá trị, is_active, deactivated_at/by/reason, mfa_verified_at, last_sign_in_at, trigger mfa_required theo vai trò; current_app_role() trả NULL khi inactive, has_role(), thu hồi grant update(role).

- [ ] Cột mới + CHECK reason 10–500
- [ ] Trigger đặt mfa_required theo vai trò đặc quyền
- [ ] current_app_role() lọc is_active + has_role(variadic)
- [ ] Map 4 vai trò prototype sang 9 vai trò

**AC:**
- User is_active=false có current_app_role() = NULL
- authenticated không UPDATE được cột role trực tiếp

#### BE-1.3.2: Viết lại RLS bảng prototype theo ma trận quyền 9 vai trò
Thay policy RLS 0300 bằng policy theo role-permission-matrix dùng has_role(); thêm CHECK decided_by <> requested_by mẫu cho bảng duyệt và bỏ quyền admin ghi nghiệp vụ.

- [ ] Bảng đối chiếu quyền × bảng × thao tác
- [ ] Policy SELECT/INSERT/UPDATE theo has_role()
- [ ] CHECK tách lập/duyệt cho bảng có decided_by
- [ ] Test SQL mỗi vai trò cho bảng chính

**AC:**
- admin không ghi được lots/inbound qua nghiệp vụ ngoài quyền ma trận
- Bản ghi duyệt có decided_by = requested_by bị DB từ chối

### S1.4: Sửa ngưỡng nhiệt đúng RFP và lưu theo phiên bản

#### BE-1.4.1: Tạo temp_zone_policy_versions, seed RFP và hàm effective_temp_policy
Migration temp_zone_policy_versions (min_c nullable, effective_from, updated_at), bỏ min_c/max_c khỏi temp_zones, seed bản 2026-04-01 đúng RFP, hàm effective_temp_policy(zone, at) theo ngày JST.

- [ ] Bảng + UNIQUE (zone, effective_from)
- [ ] Seed 冷蔵 0–5, 常温 15–25, 冷凍 NULL..−18
- [ ] effective_temp_policy() stable, theo app_today/JST
- [ ] Cơ chế seed bỏ qua trigger ≥ ngày mai chỉ cho role migration

**AC:**
- effective_temp_policy('frozen', now()) trả min_c NULL, max_c −18
- temp_zones không còn cột min_c/max_c

#### BE-1.4.2: Chuyển nơi đọc ngưỡng sang effective_temp_policy và lưu policy_version_id
Sửa view inbound_lines_with_temp_check, GET /api/temp-zones, formatTempZone() đọc ngưỡng qua effective_temp_policy; thêm policy_version_id vào inbound_lines/shipments.

- [ ] View tính phán định theo ngày đến
- [ ] /api/temp-zones trả bản hiệu lực + version id
- [ ] formatTempZone() hiển thị 下限なし khi min_c NULL
- [ ] Cột policy_version_id + FK

**AC:**
- Đổi ngưỡng bản tương lai không làm đổi phán định dòng nhập cũ
- Không còn chỗ đọc temp_zones.min_c trong code

### S1.5: Dựng hạ tầng Tokyo, CI và phân trang 50 dòng

#### BE-1.5.3: Viết helper phân trang 50 dòng dùng chung cho API danh sách
Helper parsePaging() (page, limit=50) + range() + count exact cho route handler; thay giới hạn 500 dòng ở các GET prototype.

- [ ] parsePaging() zod, mặc định 50
- [ ] Response { items, page, total }
- [ ] Áp vào GET prototype hiện có
- [ ] Unit test biên trang

**AC:**
- Không còn .limit(500) trong code
- GET danh sách trả total đúng

