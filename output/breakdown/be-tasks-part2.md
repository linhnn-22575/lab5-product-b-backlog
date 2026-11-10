# Backend Tasks: Product B — Yuki Cold Logistics (LAB-5)

**Date**: 2026-11-10 | **Total**: TBD

---

## E2: F12 Xác thực & phân quyền

### S2.1: Đăng nhập SSO, MFA và quản lý phiên (SCR-001)

#### BE-2.1.2: Viết /auth/sso/start và /auth/callback có PKCE, kiểm MFA và JIT profile
sso/start tạo state/nonce/code_verifier cookie HttpOnly 10 phút, lọc next; callback exchangeCodeForSession, kiểm amr MFA (M_105), is_active (M_106), JIT profile role NULL, cập nhật mfa_verified_at/last_sign_in_at, map ?error= whitelist, audit login.

- [ ] PKCE + state/nonce, prompt=login cho thiết bị dùng chung
- [ ] Kiểm amr theo danh sách cấu hình được
- [ ] Cập nhật mfa_verified_at, last_sign_in_at
- [ ] Audit auth.login_success/failure, không log token

**AC:**
- Vai trò đặc quyền đăng nhập thiếu MFA bị chuyển /login?error=mfa_required
- next ngoài domain hoặc > 512 ký tự bị bỏ qua

#### BE-2.1.3: Viết middleware chặn phiên sai và mở rộng GET /api/me
Middleware decideRouteAccess + chặn amr=password khi cờ tắt + so mfa_required với amr khi đổi vai trò + hủy phiên user vô hiệu (/login?error=deactivated); /api/me thêm mfaRequired, isActive, 403 M_20 khi không vai trò.

- [ ] Chặn amr=password ở prod (M_103)
- [ ] Đổi sang vai trò đặc quyền giữa phiên → bắt đăng nhập lại
- [ ] is_active=false → hủy phiên, M_106
- [ ] /api/me + 403 no-role

**AC:**
- User bị vô hiệu bị đẩy ra ở request kế tiếp
- User không vai trò gọi API nghiệp vụ nhận 403 M_20

#### BE-2.1.4: Làm app_sessions, heartbeat idle 15 phút, thiết bị dùng chung và logout
Bảng app_sessions (theo DB design), POST /api/session/heartbeat kiểm idle server-side (idle_timeout), cookie ký ycl_shared_device, logout local + RP-initiated ở thiết bị dùng chung, audit logout/idle/expired.

- [ ] app_sessions theo cột DB design (device_id, expires_at)
- [ ] Heartbeat: polling không tính là thao tác
- [ ] Thời gian idle là tham số cấu hình
- [ ] RP-initiated logout qua end_session_endpoint

**AC:**
- Quá thời gian idle, request kế tiếp trả 401 + redirect idle_timeout
- Logout ở thiết bị dùng chung đăng xuất cả phiên IdP

### S2.2: Trang chủ theo vai trò (SCR-002, trừ thẻ giờ lái)

#### BE-2.2.1: Viết lại get_home_summary khung và route GET /api/home-summary
RPC get_home_summary() stable/security invoker/search_path='' đọc current_app_role(), ma trận thẻ cấu hình server, chỉ tính key của vai trò; route trả cards[] qua zod, no-store, 401/403/500.

- [ ] Cấu hình ma trận 9 vai trò × thẻ (chừa slot 4.8/4.10/4.11)
- [ ] Thẻ chỉ có link khi vai trò xem được màn đích
- [ ] Zod response, sai shape → 500
- [ ] Cache-Control: no-store

**AC:**
- Mỗi vai trò chỉ nhận đúng các thẻ của mình
- Vai trò no-role nhận 403

#### BE-2.2.2: Viết truy vấn thẻ kho, chất lượng, đơn và hợp đồng của trang chủ
Truy vấn thẻ 4.1, 4.2 (số ngày từ lot_status_events), 4.3, 4.12, 4.13, 4.4, 4.5, 4.6 (loại yêu cầu tự tạo), 4.14–4.17 theo app_today() JST; bảng chưa có dữ liệu trả 0.

- [ ] Thẻ kho/chất lượng + dòng phụ
- [ ] Thẻ đơn/hợp đồng/ngoại lệ, 4.17 loại legacy
- [ ] 4.6 loại yêu cầu do chính mình tạo
- [ ] Đếm biên theo ngày JST

**AC:**
- Dữ liệu seed cho số đếm đúng từng thẻ
- Bảng rỗng trả 0, không lỗi

#### BE-2.2.3: Viết truy vấn thẻ tuyến chưa gán, chưa công bố và kiểm hiệu năng
Truy vấn thẻ 4.7 (tuyến chưa gán) và 4.9 (chưa công bố) từ routes/route_versions; đo p95 ≤ 1s mỗi vai trò, thêm index cần thiết.

- [ ] Thẻ 4.7, 4.9 (bảng F07 rỗng → 0)
- [ ] EXPLAIN các truy vấn thẻ
- [ ] Index thiếu
- [ ] Đo p95 từng vai trò trên dữ liệu seed

**AC:**
- p95 get_home_summary ≤ 1s cho cả 9 vai trò
- Thẻ 4.7/4.9 trả 0 khi chưa có tuyến

### S2.3: Quản lý người dùng và vai trò (SCR-018)

#### BE-2.3.1: Viết RPC đổi vai trò, vô hiệu hóa user và route PATCH tương ứng
RPC admin_set_user_role / admin_set_user_active (security definer, for update, expected* khóa lạc quan, P0001 hint M_120/M_122/M_127/M_22, audit) + PATCH /api/users/:id/role, /status; thu hồi phiên khi vô hiệu.

- [ ] Spike: xóa auth.refresh_tokens trong RPC vs Admin API signOut
- [ ] Chặn tự đổi vai trò / tự vô hiệu
- [ ] Lý do 10–500 bắt buộc khi vô hiệu
- [ ] Map lỗi 403/404/409/400

**AC:**
- User bị vô hiệu không gọi được API ở request kế tiếp
- Hai admin sửa cùng lúc: người sau nhận 409 M_22

#### BE-2.3.2: Mở rộng GET /api/users có lọc, phân trang 50 và RLS profiles
GET /api/users: q (escape %/_), role/none, status, mfa=unverified, phân trang 50; RLS profiles_select_admin_or_auditor, quyền users:read.

- [ ] Zod query params
- [ ] Escape ký tự LIKE
- [ ] Phân trang qua helper chung
- [ ] RLS chỉ admin/auditor đọc

**AC:**
- Vai trò khác gọi API nhận 403
- ?role=none trả đúng user chưa có vai trò

