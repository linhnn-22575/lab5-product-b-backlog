# Backend Tasks: Product B — Yuki Cold Logistics (LAB-5)

**Date**: 2026-11-10 | **Total**: TBD

---

## E3: F01 Master & chính sách nhiệt

### S3.1: Quản lý master SKU (SCR-010)

#### BE-3.1.1: Mở rộng bảng skus, seed 12 SKU và trigger khóa trường đã dùng
Migration skus thêm unit, trace_lane, updated_at, unique upper(code), backfill SKU prototype + seed 12 SKU R-02; trigger skus_guard_used_fields thay 0800 trả P0001 hint M_130, detail = danh sách cột.

- [ ] Cột mới + unique index upper(code)
- [ ] Backfill + seed R-02
- [ ] Trigger kiểm inUse qua lots/inbound_lines/order_lines
- [ ] RLS skus_insert_admin/skus_update_admin, không DELETE

**AC:**
- UPDATE temp_zone của SKU đã có lô trả P0001 M_130
- Tạo mã trùng khác hoa thường bị 23505

#### BE-3.1.2: Viết sku_list_view và API GET/POST/PATCH /api/skus
View sku_list_view (inUse, ngưỡng hiệu lực); GET /api/skus lọc q/tempZone/expiryType/status + phân trang 50; POST/PATCH zod chung, expectedUpdatedAt, map 23505/P0001/PGRST116 → M_14/M_130/M_23/M_22, audit.

- [ ] View + GET lọc/phân trang
- [ ] Zod chung client/server, mã ^[A-Z0-9_-]+$
- [ ] Optimistic lock expectedUpdatedAt
- [ ] Trigger audit_log

**AC:**
- PATCH với updatedAt cũ trả 409 M_22
- GET trả inUse và ngưỡng đúng phiên bản hiện hành

### S3.2: Quản lý khách hàng (SCR-011 tab 顧客)

#### BE-3.2.1: Mở rộng customers, seed CUS-001–005 và API GET/POST/PATCH khách hàng
Migration customers.updated_at + regex mã thống nhất Format_Code (A–Z, tự upper), seed CUS-001–005; GET/POST/PATCH /api/customers: tìm/lọc/phân trang, đếm hợp đồng active/pending, khóa mã (M_155), optimistic lock, audit.

- [ ] Migration + seed
- [ ] GET đếm hợp đồng + badge 未確定
- [ ] PATCH chặn đổi mã (M_155), expectedUpdatedAt
- [ ] Audit before/after

**AC:**
- PATCH đổi mã khách trả lỗi M_155
- Mã chữ thường được chuẩn hóa thành chữ hoa

### S3.3: Quản lý hợp đồng khách–SKU có phiên bản (SCR-011 tab 契約)

#### BE-3.3.1: Tạo migration customer_sku_agreements, trigger khóa và dữ liệu R-04
Migration customer_sku_agreements (change_reason, created_by, UNIQUE (agreement_code, effective_from), CHECK, không DEFAULT window_rule, ràng buộc mã ↔ cặp), trigger chặn UPDATE/DELETE khi effective_from ≤ app_today(), RLS ghi chỉ qua RPC, nạp 15 hợp đồng R-04.

- [ ] Cột + UNIQUE + CHECK, không DEFAULT
- [ ] Ràng buộc 1 mã ↔ 1 cặp khách–SKU
- [ ] Trigger khóa phiên bản đã hiệu lực
- [ ] Nạp R-04 + test count(window_rule is null)=2

**AC:**
- UPDATE phiên bản đã hiệu lực bị trigger chặn
- Sau nạp R-04 có đúng 2 hợp đồng window_rule NULL (AGR-008/014)

#### BE-3.3.2: Viết view phiên bản hợp đồng, API danh sách/lịch sử và hủy phiên bản
View customer_sku_agreement_versions_view (trạng thái 適用中/適用予定/適用終了, effective_to tính); GET /api/customer-sku-agreements (lọc, scope, pendingCount, heldOrderLines) + /history; RPC cancel_customer_sku_agreement_version + DELETE (chỉ tương lai, 409 M_145).

- [ ] View + trạng thái tính lúc đọc
- [ ] GET lọc khách/SKU/rule/pending/scope
- [ ] RPC hủy chỉ phiên bản tương lai
- [ ] Audit before khi hủy

**AC:**
- Hủy phiên bản đang áp dụng trả 409 M_145
- pendingCount khớp số hợp đồng window_rule NULL đang áp dụng

#### BE-3.3.3: Viết RPC create_customer_sku_agreement_version và route POST
RPC advisory lock, kiểm khách/SKU active (M_148/M_149), effective_from (M_143/M_144), mã ↔ cặp (M_142/M_152), giống phiên bản trước (M_153), insert + audit; route POST zod bắt buộc key window_rule (thiếu → 400 M_141).

- [ ] Advisory lock theo cặp khách–SKU
- [ ] Đủ kiểm tra M_141–M_153
- [ ] null chỉ hợp lệ khi gửi tường minh
- [ ] Lý do bắt buộc (M_06)

**AC:**
- POST thiếu key window_rule trả 400 M_141
- Hai request đồng thời cùng ngày: một thành công, một M_144

#### BE-3.3.4: Cập nhật order_lines khi phiên bản áp dụng và lập job 00:05 JST
Logic chuyển order_lines business_review ↔ open + trỏ agreement_id khi phiên bản áp dụng hôm nay (trong RPC) hoặc tương lai (hàm job), đăng ký pg_cron 00:05 JST, idempotent, ghi log chạy.

- [ ] Hàm apply_agreement_versions_for_date() idempotent
- [ ] Gọi trong RPC khi effective_from = hôm nay
- [ ] cron.schedule 00:05 JST + log kết quả
- [ ] Bỏ qua dòng đã allocated (theo giả định)

**AC:**
- Chạy job 2 lần cùng ngày không đổi kết quả
- Dòng business_review chuyển open khi phiên bản có window_rule áp dụng

### S3.4: Quản lý phiên bản ngưỡng nhiệt (SCR-015)

#### BE-3.4.1: Viết trigger khóa phiên bản ngưỡng, view lịch sử và GET /api/temp-policies
Trigger temp_policy_versions_lock_effective + trigger BEFORE INSERT/UPDATE effective_from ≥ ngày mai, RLS SELECT mọi vai trò / ghi qua RPC; view temp_zone_policy_versions_view (effective_to, state, usage_count) + GET.

- [ ] Trigger khóa + ≥ ngày mai (bypass chỉ role migration)
- [ ] RLS SELECT mở cho mọi vai trò kể cả admin
- [ ] View usage_count từ inbound_lines/shipments/deviations
- [ ] GET + lọc dải + phân trang

**AC:**
- UPDATE phiên bản đã hiệu lực trả 409 M_164
- GET trả 3 bản hiện hành + tương lai + lịch sử

#### BE-3.4.2: Viết RPC tạo, sửa, hủy phiên bản ngưỡng và các route ghi
RPC create_temp_policy_version, update_scheduled_temp_policy_version (for update, kiểm sau khóa), DELETE phiên bản tương lai; validate M_161–M_171, optimistic lock M_22/M_23, audit; POST/PATCH/DELETE /api/temp-policies.

- [ ] min ≤ max, −50..50 1 số lẻ, 下限なし chỉ 冷凍
- [ ] Lý do 10–500, giống bản gốc → M_167
- [ ] Kiểm lại sau khi khóa dòng (qua 0:00 JST → M_164)
- [ ] Audit before/after

**AC:**
- quality tạo được bản ngày mai; admin gọi API nhận 403
- Sửa bản đã qua 0:00 JST trả 409 M_164

#### BE-3.4.3: Viết diffAcceptRanges và API xem trước ảnh hưởng ngưỡng mới
Hàm thuần TS diffAcceptRanges (newlyOut/newlyIn, đoạn đóng, NULL = −∞) + unit test các ca item 8-10; POST /api/temp-policies/preview + SQL đếm nhập/xuất 30 ngày.

- [ ] Hàm thuần + unit test đủ ca biên
- [ ] SQL đếm 30 ngày (shipment có ≥1 SKU thuộc dải)
- [ ] Route preview zod
- [ ] Preview lỗi không chặn lưu

**AC:**
- Unit test các ca item 8-10 đều pass
- Biên đúng bằng ngưỡng tính là đạt

