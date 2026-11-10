# QA (Manual) Tasks: Product B — Yuki Cold Logistics (LAB-5)

**Date**: 2026-11-10 | **Total**: TBD

---

## E2: F12 Xác thực & phân quyền

### S2.1: Đăng nhập SSO, MFA và quản lý phiên (SCR-001)

#### QA-2.1.7: Viết test case + chạy test SCR-001
Test SSO happy/lỗi, thiếu MFA, deactivated, no-role, open-redirect next, reflect ?error=, idle đa tab, cờ demo; kiểm audit_log không chứa token.

- [ ] Bộ test case theo trạng thái §8
- [ ] Ca bảo mật: next, ?error=, amr=password ở prod
- [ ] Idle + thiết bị dùng chung
- [ ] Bằng chứng audit_log

**AC:**
- Mọi ca có kết quả + bằng chứng
- Lỗi tìm thấy được log thành issue

### S2.2: Trang chủ theo vai trò (SCR-002, trừ thẻ giờ lái)

#### QA-2.2.5: Viết test case + chạy test SCR-002
Ma trận 9 vai trò × thẻ (đúng thẻ, thứ tự, link), điều kiện đếm biên (ngày JST, 消費期限, legacy), trạng thái lỗi/giữ số cũ. Thẻ giờ lái test ở E9.

- [ ] Ma trận vai trò × thẻ
- [ ] Ca biên ngày JST, 消費期限
- [ ] Trạng thái loading/lỗi/tất cả 0
- [ ] Kiểm link theo quyền

**AC:**
- Mọi ô ma trận có kết quả
- Lỗi log thành issue

### S2.3: Quản lý người dùng và vai trò (SCR-018)

#### QA-2.3.5: Viết test case + chạy test SCR-018
State machine user, tự bảo vệ, auditor read-only, 409 đồng thời, hiệu lực ngay sau vô hiệu, MFA khi lên vai trò đặc quyền; gọi API thẳng không quyền, UPDATE trực tiếp bị chặn, audit_log.

- [ ] Ca state machine active_no_role ↔ active_with_role ↔ inactive
- [ ] Ca bảo mật API/RLS
- [ ] Ca đồng thời 2 admin
- [ ] Bằng chứng audit_log

**AC:**
- Mọi ca có kết quả + bằng chứng
- Lỗi log thành issue

## E3: F01 Master & chính sách nhiệt

### S3.1: Quản lý master SKU (SCR-010)

#### QA-3.1.5: Viết test case + chạy test SCR-010
Validation từng trường, khóa khi inUse (UI + gọi API thẳng), ngưng dùng, optimistic lock, phân quyền 9 vai trò; kiểm audit_log và SKU inactive bị chặn ở SCR-022/SCR-041.

- [ ] Ca validation + biên
- [ ] Ca khóa trường qua API thẳng
- [ ] Ca phân quyền 9 vai trò
- [ ] Bằng chứng audit_log

**AC:**
- Mọi ca có kết quả + bằng chứng
- Lỗi log thành issue

### S3.3: Quản lý hợp đồng khách–SKU có phiên bản (SCR-011 tab 契約)

#### QA-3.3.7: Viết test case + chạy test SCR-011
Cả 2 tab: invariant window_rule NULL (không default ở UI/API/DB), phiên bản hôm nay/tương lai/trùng/giống trước, hủy, quyền admin vs sales_manager, dữ liệu R-04, side-effect order_lines + job 00:05.

- [ ] Ca tab 顧客
- [ ] Ca phiên bản + hủy
- [ ] Ca phân quyền
- [ ] Ca side-effect order_lines + job

**AC:**
- Mọi ca có kết quả + bằng chứng
- Lỗi log thành issue

### S3.4: Quản lý phiên bản ngưỡng nhiệt (SCR-015)

#### QA-3.4.6: Viết test case + chạy test SCR-015
Biên ngưỡng, NULL cận dưới, tương lai/hiệu lực/qua 0:00 JST, đua sửa, quyền quality vs admin; hồi quy giao dịch cũ giữ policy_version_id, SCR-010/SCR-022 đọc ngưỡng đúng theo ngày.

- [ ] Ca validation + biên
- [ ] Ca khóa + đồng thời
- [ ] Ca preview
- [ ] Ca hồi quy policy_version_id

**AC:**
- Mọi ca có kết quả + bằng chứng
- Lỗi log thành issue

## E4: F02 Nhập hàng

### S4.2: Kiểm nhiệt 2 lớp và xác nhận phiếu idempotent (SCR-022)

#### QA-4.2.4: Viết test case + chạy test SCR-022
Ma trận P0 từng field, lớp A/B ADR-008, quy tắc -Q, trace beef/rice, phiên bản ngưỡng theo ngày đến, ảnh (định dạng, cỡ, SHA-256), RBAC; xác nhận bấm 2 lần / mạng chập chờn cùng key, 2 tab khác key (M_208), số bản ghi lots/movements/events/deviations.

- [ ] Ca form dòng + ảnh
- [ ] Ca kiểm 2 lớp + -Q + trace
- [ ] Ca idempotency + đồng thời
- [ ] Kiểm DB sau xác nhận

**AC:**
- Mọi ca có kết quả + bằng chứng
- Lỗi log thành issue

## E5: F03 Tồn kho & lô

### S5.1: Tra cứu tồn kho theo lô (SCR-030)

#### QA-5.1.4: Viết test case + chạy test SCR-030
Test tra cứu tồn kho: biên nhãn hạn theo 2 loại hạn, qty_available theo trạng thái, AND 10 filter, FEFO, tổng khớp toàn bộ kết quả.

- [ ] Biên days_left −1/0/1/3/4 × 消費期限/賞味期限
- [ ] qty_available theo 5 trạng thái lô + lô 消費期限到達
- [ ] Kết hợp 10 filter, filter supplier loại lô seed, sắp FEFO
- [ ] Số tổng khớp toàn bộ kết quả qua nhiều trang

**AC:**
- Bộ test case được review và lưu trong repo test
- Mọi case chạy pass hoặc lỗi được tạo issue có bước tái hiện

### S5.2: Chi tiết lô, lịch sử sự kiện và cách ly thủ công (SCR-031)

#### QA-5.2.6: Viết test case + chạy test SCR-031
Test nút theo vai trò × trạng thái lô, chặn cách ly khi có phân bổ, timeline đủ loại + gộp correlation, keyset, bằng chứng, đồng thời và audit_log.

- [ ] Ma trận vai trò (quality, warehouse_lead, admin, auditor…) × trạng thái lô
- [ ] Timeline đủ 10 loại, phân trang keyset, lọc kinds
- [ ] Đồng thời cách ly vs allocate_lot; gửi lại cùng key
- [ ] Kiểm audit_log và file/số tham chiếu bằng chứng

**AC:**
- Bộ test case được review và lưu trong repo test
- Mọi case chạy pass hoặc lỗi được tạo issue có bước tái hiện

### S5.3: Máy trạng thái lô: cách ly, 保留, giải phóng, hủy có duyệt 2 người (SCR-037)

#### QA-5.3.8: Viết test case + chạy test SCR-037
Test máy trạng thái lô, duyệt 2 người (biên 100/101, tự duyệt, đã quyết định, qty đổi, đồng thời), giải phóng theo vị trí đích, bằng chứng, RBAC 3 vai trò.

- [ ] Chuyển hợp lệ/bước nhảy sai M_301, yêu cầu pending chặn thao tác
- [ ] Biên ngưỡng 100/101, tự duyệt, ALREADY_DECIDED, đồng thời
- [ ] Vị trí đích khác vùng/khu -Q/ngưng dùng/ambient không -Q
- [ ] RBAC quality/warehouse_lead/auditor + vai trò khác 403

**AC:**
- Bộ test case được review và lưu trong repo test
- Mọi case chạy pass hoặc lỗi được tạo issue có bước tái hiện

