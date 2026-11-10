# Trích xuất spec màn hình — Nhóm A (SCR-001, 002, 010, 011, 015)

Nguồn: `lab4-product-b-design/specs/05-screens/SCR-<id>_SPEC.md` (v0.1.0, 2026-11-08). Đối chiếu bằng grep: `03-database/database-design.md`, `06-common/role-permission-matrix.md`, `06-common/common-format.md`, `04-business-rules/business-rules.md`, `02-adr/ADR-003`, `ADR-006`.
Quy ước: cỡ S ≤ 4h, M ≤ 8h, L ≤ 16h. "INFERRED" = spec tự ghi là suy luận, cần xác nhận.

Tổng: **69 sub-task** (SCR-001: 15 · SCR-002: 13 · SCR-010: 11 · SCR-011: 17 · SCR-015: 13). Gap: **33**.

---

## SCR-001 — ログイン (F12 auth)

### 1. Tổng quan
- Mục đích: cổng đăng nhập duy nhất — SSO OIDC (production), email/mật khẩu chỉ ở demo; xử lý MFA vai trò đặc quyền, no-role, phiên ngắn thiết bị dùng chung.
- Role: mọi người chưa đăng nhập; 9 vai trò sau đăng nhập (redirect). `driver` dùng app F06, ngoài phạm vi (§3).

### 2. Khu vực / component
- Khung đăng nhập: tên hệ thống (1), nút SSO (2), băng rôn demo (3), form demo email/mật khẩu/nút (4–6), vùng lỗi (7), ghi chú thiết bị dùng chung (8), ghi chú cấp tài khoản (9).
- Panel no-role trong layout `(app)` (10–10.4).
- Dialog cảnh báo tự đăng xuất + đếm ngược (11–11.4).
- Quy tắc URL/phiên/middleware (12).

### 3. Dữ liệu
- Bảng: `profiles` (`role`, `mfa_required`, `is_active`), `app_sessions` (`last_activity_at`), `audit_log`. Trigger `handle_new_auth_user` (JIT profile, role NULL), trigger `prevent_demo_credential_change` (migration 0900).
- API: `GET /auth/sso/start` (mới), `GET /auth/callback` (mới), `POST /api/session/heartbeat` (mới), `GET /api/me` (+`mfaRequired`, `isActive`), Supabase `signInWithPassword` / `signOut({scope:'local'})`.
- Hàm: `current_app_role()` to-be trả NULL khi `is_active=false`; `toSafeNextPath`, `decideRouteAccess` (giữ prototype).
- Tham chiếu: IF-IDP-01, NFR-SEC-01/02, NFR-AUD-01, NFR-LOC-01, RBAC-001 §2.4, BR-INV-03. ADR-007 (audit append-only) gián tiếp qua `audit_log`.
- Message: M_100–M_109, M_01, M_13, M_20, M_21, M_40, M_41.

### 4. Validation / trạng thái / luồng đặc biệt
- OIDC Authorization Code + PKCE; cookie `state/nonce/code_verifier` HttpOnly SameSite=Lax 10 phút; thiết bị dùng chung thêm `prompt=login`, `max_age=0`.
- Callback: lỗi/state sai/quá hạn → `sso_failed` (M_103); vai trò đặc quyền thiếu `amr` MFA → M_105; `is_active=false` → M_106; user mới → JIT profile role NULL.
- Server chặn phiên `amr=password` khi `AUTH_PASSWORD_LOGIN_ENABLED=false` (M_103).
- `?error=` chỉ map whitelist; giá trị lạ bỏ qua (chống reflect). `next` ≤ 512, chỉ path nội bộ.
- Idle 15 phút (INFERRED): cảnh báo ở phút 14, đếm 60s; kiểm cả server (`last_activity_at`), multi-tab qua `BroadcastChannel('ycl-activity')`; polling không tính là thao tác.
- Đổi role sang đặc quyền giữa phiên → middleware so `mfa_required` vs `amr` → hủy phiên.
- Logout: local + RP-initiated logout ở thiết bị dùng chung; full page load.
- Trạng thái: ban đầu / đang chuyển IdP / đang đăng nhập demo / lỗi / no-role / sắp hết phiên / lỗi mạng (§8).
- Audit: `auth.login_success|login_failure|logout|idle_timeout|session_expired`, không log token.

### 5. Ràng buộc giờ lái xe 2024
- **Không.** (Tài xế dùng app F06 — ngoài phạm vi màn này, §3.)

### 6. Sub-task đề xuất
- [Infra] Cấu hình Supabase OIDC provider với IdP công ty (dev/stg/prod), tắt Email provider ở prod, biến `AUTH_PASSWORD_LOGIN_ENABLED` — M
- [BE] `GET /auth/sso/start`: tạo state/nonce/PKCE cookie, lọc `next`, `prompt=login` cho thiết bị dùng chung — M
- [BE] `GET /auth/callback`: exchangeCodeForSession, kiểm `amr`/MFA, `is_active`, JIT profile, map `?error=`, audit login — L
- [BE] Migration `profiles` (`mfa_required` + trigger set theo role, `is_active`, …) + `current_app_role()` trả NULL khi inactive + RLS — M
- [BE] Middleware: `decideRouteAccess` + chặn `amr=password` ở prod + kiểm MFA khi đổi role + `is_active` giữa phiên + session_expired — M
- [BE] `app_sessions` + `POST /api/session/heartbeat` + kiểm idle server-side 15 phút (401 / redirect `idle_timeout`) — M
- [BE] Cơ chế nhận diện thiết bị dùng chung (cookie ký `ycl_shared_device`) — M (chặn bởi BrSE xác nhận)
- [BE] Logout: RP-initiated logout (`end_session_endpoint`) cho thiết bị dùng chung + audit logout/idle/expired — S
- [BE] `GET /api/me` thêm `mfaRequired`, `isActive`; 403 không role → M_20 — S
- [FE] Màn login JP: SSO (production/demo layout), banner demo, form demo + validate, map lỗi Supabase → M_100–M_102/M_40/M_41, vùng lỗi theo `?error=` — M
- [FE] No-role notice trong layout `(app)` (ẩn sidebar + nội dung, reload, logout) — S
- [FE] Idle timer + dialog cảnh báo 60s + BroadcastChannel đa tab + heartbeat — M
- [QA] Thiết kế test case: SSO happy/lỗi, MFA thiếu, deactivated, no-role, open-redirect `next`, reflect `?error=`, idle đa tab, demo env flag — M
- [QA] Thực thi test + bằng chứng (gồm kiểm prod không render form mật khẩu, không có token trong audit) — M
- [BrSE] Làm rõ với khách: giá trị idle 15 phút, cảnh báo 60s, claim `amr` của IdP Yuki, cơ chế đăng ký thiết bị dùng chung — S

### 7. Gap / mâu thuẫn
| # | Vị trí | Mô tả | Đề xuất |
|---|---|---|---|
| 1 | SCR-001 §3, §5 item 8-1, item 11-2 | 15 phút idle, cảnh báo 60s, cookie thiết bị dùng chung đều INFERRED (RFP chỉ ghi「短時間セッション」) | Issue làm rõ (BrSE); code dùng tham số cấu hình |
| 2 | SCR-001 item 2-4, item 12-3 | Giá trị claim `amr` (`mfa`/`otp`/`hwk`) phụ thuộc sản phẩm IdP — chưa xác định | Issue làm rõ; giả định cấu hình được danh sách giá trị |
| 3 | SCR-001 item 7-2 vs item 2-6 | M_104 `mfa_failed` được map ở vùng lỗi nhưng callback không có nhánh nào sinh ra `mfa_failed` | Sửa thiết kế: định nghĩa nguồn (IdP `error=access_denied`?) hoặc bỏ M_104 |
| 4 | SCR-001 §9 "Dữ liệu" vs database-design §3.3 | Spec ghi `is_active` và `app_sessions` "chưa có trong database-design" nhưng DB design đã có. Cột lệch: spec `app_sessions(session_id, profile_id, is_shared_device, last_activity_at)` vs DB `id, profile_id, device_id, last_activity_at, expires_at` | Sửa spec theo DB design; chốt cột trong task BE |
| 5 | SCR-001 item 2-6 / item 12 vs SCR-002 item 4-16 | SCR-002 thẻ 4.16 dựa vào `profiles.mfa_verified_at`, nhưng SCR-001 không quy định cập nhật `mfa_verified_at` / `last_sign_in_at` ở callback | Sửa thiết kế: thêm bước cập nhật vào callback (BE task trên) |

---

## SCR-002 — ホーム（役割別） (F12)

### 1. Tổng quan
- Mục đích: trang chủ chỉ đọc, hiển thị bộ thẻ "việc chờ" cố định theo vai trò để không bỏ sót việc nguy hiểm đầu ca.
- Role: 9 vai trò (bộ thẻ khác nhau); no-role không vào được.

### 2. Khu vực / component
- Tiêu đề (1), dòng hướng dẫn (2), thời điểm tổng hợp + nút làm mới (3, 3.1).
- Lưới thẻ (4) với 17 loại thẻ 4.1–4.17 theo ma trận vai trò; thẻ 4.11 có bảng tài xế con (4.11.1).
- Banner "không còn việc chờ" (5, M_110).

### 3. Dữ liệu
- Đọc: `inbound_receipts`, `lots`, `lot_status_events`, `deviations`, `orders`, `order_lines`, `customer_sku_agreements`, `date_reversal_exception_requests`, `routes`, `route_versions`, `compliance_check_results`, `unforeseeable_events`, `drivers`, `driver_duty_records`, `driver_rule_versions`, `skus`, `profiles`. Không ghi.
- API: `GET /api/home-summary` (to-be trả `cards[]` chỉ của vai trò gọi). RPC `get_home_summary()` viết lại (`stable`, `security invoker`, `search_path=''`), `get_driver_month_restraint(p_month)` (INFERRED, dùng chung SCR-061), `app_today()`.
- BR: BR-TIME-01, BR-EXP-01/02, BR-DELWIN-01, BR-DATE-02, BR-DRV-03/14/20/24, BR-OUT-04, FR-INV-05. ADR-005 (date reversal), ADR-006 (driver hours), ADR-003 (rule version).

### 4. Validation / trạng thái / luồng đặc biệt
- Ma trận thẻ là cấu hình server; client không tự lọc. Thẻ chỉ có link khi vai trò được xem màn đích.
- Tone: danger/warning/info; số = 0 → xám「対応不要」. aria-label + màu kèm chữ (WCAG 2.2 AA).
- 4.6 / 4.10: loại yêu cầu do chính mình tạo (tách người lập/duyệt).
- Tự làm mới 5 phút khi tab hiển thị (INFERRED); không realtime. Làm mới giữ số cũ.
- Trạng thái: loading skeleton, có dữ liệu, tất cả 0, đang làm mới, 500 (giữ số cũ + 「更新失敗」), lỗi mạng, 401→login, bảng F07 rỗng → 0.
- Zod response; sai shape → 500. `Cache-Control: no-store`. p95 ≤ 1s (INFERRED).

### 5. Ràng buộc giờ lái xe 2024
- **Có.**
  - Thẻ 4.8 (tuyến còn vi phạm, BR-DRV-20 — dựa `compliance_check_results.violation_count` của `route_version` hiện tại).
  - Thẻ 4.11 (tài xế ≥ 90% 拘束時間 tháng, BR-DRV-03; giới hạn từ `driver_rule_versions.restraint_month_max_h` / `ext_restraint_month_max_h` BR-DRV-14, không hard-code 284).
  - Thẻ 4.10 (sự cố bất khả kháng chờ duyệt, BR-DRV-24), 4.7/4.9 (tuyến chưa gán/chưa công bố).
  - Phải dùng chung cách tính với ADR-006 engine / SCR-061.

### 6. Sub-task đề xuất
- [BE] Viết lại `get_home_summary()` khung: đọc `current_app_role()`, cấu hình ma trận thẻ, chỉ tính key của vai trò — M
- [BE] Truy vấn thẻ kho/chất lượng: 4.1, 4.2 (số ngày từ `lot_status_events`), 4.3, 4.12, 4.13 + dòng phụ — M
- [BE] Truy vấn thẻ đơn/hợp đồng/ngoại lệ: 4.4, 4.5, 4.6, 4.14, 4.17 (loại legacy) + 4.15, 4.16 — M
- [BE] Truy vấn thẻ tuyến: 4.7, 4.8 (latest check theo route_version), 4.9, 4.10 — M
- [BE] `get_driver_month_restraint(p_month)` dùng chung ADR-006/SCR-061 + thẻ 4.11 (rule version hiệu lực, ext limit, ngưỡng 90%, top 5) — L
- [BE] Route `GET /api/home-summary` to-be + zod response + 401/403/500 + `no-store` — S
- [BE] Kiểm hiệu năng p95 ≤ 1s/vai trò, index cần thiết — S
- [FE] Trang chủ: header, as-of time, refresh, auto-refresh 5' theo `visibilitychange`, trạng thái loading/lỗi/giữ số cũ — M
- [FE] Component thẻ chung (tone, badge, xám khi 0, link/không link, aria) + lưới responsive 3/2/1 cột + banner M_110 — M
- [FE] Thẻ 4.11 với bảng tài xế con (badge 残り, 超過, 「ほか n名」, chú thích 拘束時間 ≠ 運転時間) — S
- [QA] Test case ma trận 9 vai trò × 17 thẻ (đúng thẻ, đúng thứ tự, đúng link) + điều kiện đếm biên (ngày JST, 消費期限, legacy) — M
- [QA] Test case thẻ giờ lái 4.8/4.11 (284h vs 310h ext, ngưỡng 90%, actual vs plan published) + thực thi — M
- [BrSE] Làm rõ: auto-refresh 5', ngưỡng 90% + màu badge 20h, admin chỉ thấy thẻ quản trị, có tính sự cố bất khả kháng vào 拘束時間 thẻ 4.11 không — S

### 7. Gap / mâu thuẫn
| # | Vị trí | Mô tả | Đề xuất |
|---|---|---|---|
| 6 | SCR-002 item 4-3 + §7 vs role-permission-matrix dòng `deviation:read` | RBAC cho `admin` ○ và `warehouse_lead` ● đọc deviation trên SCR-002, nhưng ma trận thẻ SCR-002 chỉ cho `quality`, `auditor` thấy 4.3 | Issue làm rõ; sửa một trong hai tài liệu |
| 7 | SCR-002 item 4.11-2 | Khoảng sự cố bất khả kháng đã duyệt **vẫn tính** vào 拘束時間 thẻ (INFERRED) — có thể lệch số với SCR-061/báo cáo tuân thủ (BR-DRV-24) → người dùng thấy 2 con số | Issue làm rõ; giả định tạm theo spec, hiển thị chú thích |
| 8 | SCR-002 item 4.11-2 vs ADR-006 §36 | ADR-006 cộng "thực tế + kế hoạch đến hết ngày phục vụ"; thẻ cộng kế hoạch `published` cả tháng — phạm vi khác | Sửa thiết kế: thống nhất trong `get_driver_month_restraint` |
| 9 | SCR-002 item 4.11 | Chỉ cảnh báo giới hạn tháng (284h); không có cảnh báo năm 3.300h / tăng ca 960h (ADR-006 §13) | Issue làm rõ (có cần thẻ năm không) |
| 10 | SCR-002 item 4.11-4 | Tham số `home_alert_ratio` = 0.9 lưu ở đâu không được định nghĩa (không có trong `driver_rule_versions`) | Giả định: hằng số cấu hình app; issue làm rõ |
| 11 | SCR-002 item 4.5-3 vs SCR-011 item 16-9 | Query param lệch: `/orders?lineStatus=business_review` vs `?line_status=business_review` cho cùng SCR-040 | Sửa thiết kế: chốt 1 tên param (đối chiếu SCR-040) |
| 12 | SCR-002 item 4.3-3 | Thẻ deviation không link vì màn F08 "giai đoạn sau" — cần ghi nhận scope | Giả định: không link ở release này |
| 13 | SCR-002 item 3-3, §9 hiệu năng, §7 admin | Auto-refresh 5', p95 1s, admin chỉ thấy thẻ quản trị đều INFERRED | Issue làm rõ (gộp BrSE task) |

---

## SCR-010 — SKUマスター (F01 master)

### 1. Tổng quan
- Mục đích: quản lý master SKU (mã, tên, đơn vị, dải nhiệt, loại hạn, loại truy xuất), khóa trường khi SKU đã dùng, không xóa.
- Role: `admin` ghi (`master:write`); 8 vai trò còn lại chỉ xem.

### 2. Khu vực / component
- Tiêu đề + tab master (1, 2) — 4 tab, hiện theo quyền xem.
- Thanh tìm kiếm/lọc: từ khóa, dải nhiệt, loại hạn, trạng thái (3–6); nút thêm (7).
- Bảng SKU 9 cột + phân trang (8, 9).
- Dialog thêm/sửa (10–10.12) với ghi chú khóa M_130; dialog xác nhận ngưng dùng (11, M_131).

### 3. Dữ liệu
- Bảng: `skus` (+`unit`, `trace_lane`, `updated_at`, unique `upper(code)`), `temp_zone_policy_versions` (ngưỡng hiển thị), `lots`, `inbound_lines`, `order_lines` (tính `inUse`), `audit_log`.
- API: `GET /api/skus` (to-be: q/tempZone/expiryType/status/page, trả `inUse`, ngưỡng hiệu lực), `GET /api/temp-zones` (đổi nguồn sang phiên bản), `POST /api/skus`, `PATCH /api/skus/:id` (+`expectedUpdatedAt`). View `sku_list_view`. Trigger `skus_guard_used_fields` (thay trigger 0800, errcode P0001 hint M_130), RLS `skus_insert_admin`/`skus_update_admin`, không DELETE.
- BR: BR-TEMP-01/02, BR-EXP-01/02, BR-ORD-01, BR-INV-03. ADR-003 (ngưỡng theo phiên bản), ADR-007 (audit).
- Message: M_130–M_132 + M_01/04/13/14/20/22/23/30/31/32/40/41.

### 4. Validation / trạng thái / luồng đặc biệt
- Mã: `Format_Code`, regex `^[A-Z0-9_-]+$`, 1–50, tự viết hoa (INFERRED), trùng không phân biệt hoa thường → M_14.
- Tên 1–200; đơn vị enum 6 giá trị; loại hạn radio không chọn sẵn; trace_lane mặc định `internal_lot`.
- `inUse=true` → khóa code/unit/temp_zone/expiry_type/trace_lane (client không gửi; DB trigger chặn).
- Optimistic lock `expectedUpdatedAt` → M_22 + nút「再読み込み」; không đổi gì → không gọi API.
- ON→OFF active → xác nhận M_131; SKU inactive không chọn được ở dòng nhập/đơn mới.
- Bảng trạng thái active × inUse (§8). Loading/empty M_32/lỗi + 再試行.

### 5. Ràng buộc giờ lái xe 2024
- **Không.** (Chỉ hiển thị tab「ドライバー規則」điều hướng sang SCR-016 cho dispatcher/transport_manager/auditor — item 2-2.)

### 6. Sub-task đề xuất
- [BE] Migration `skus`: `unit`, `trace_lane`, `updated_at` + trigger, unique `upper(code)`, backfill SKU prototype + seed 12 SKU R-02 — M
- [BE] Trigger `skus_guard_used_fields` (thay 0800) trả P0001/M_130 + danh sách cột — M
- [BE] View `sku_list_view` (`inUse`, ngưỡng hiệu lực) + `GET /api/skus` có lọc/phân trang + `GET /api/temp-zones` đổi nguồn — M
- [BE] `POST`/`PATCH /api/skus`: zod chung, optimistic lock, map lỗi 23505/P0001/PGRST116 → M_14/M_130/M_23/M_22, trigger audit_log — M
- [FE] Layout `/master/*`: tiêu đề + tab master theo quyền xem — S
- [FE] Trang danh sách SKU: tìm (debounce, escape), 3 bộ lọc trên query string, bảng + badge/tooltip ngưỡng, phân trang, trạng thái — M
- [FE] Dialog thêm/sửa SKU: zod chung, khóa trường theo `inUse`, chỉ gửi trường đổi, M_31 khi hủy có thay đổi, M_22 reload — M
- [FE] Dialog xác nhận ngưng dùng M_131 — S
- [QA] Test case: validation từng trường, khóa khi inUse (UI + gọi API thẳng), ngưng dùng, optimistic lock, phân quyền 9 vai trò — M
- [QA] Thực thi test + kiểm audit_log, kiểm SKU inactive bị chặn ở SCR-022/SCR-041 — M
- [BrSE] Làm rõ: danh sách đơn vị (có `case`?), khóa code/unit/trace_lane khi đã dùng, quy trình duyệt master và chủ sở hữu 営業オペレーション (RFP S3-01) — S

### 7. Gap / mâu thuẫn
| # | Vị trí | Mô tả | Đề xuất |
|---|---|---|---|
| 14 | SCR-010 §7 ghi chú + §10 #9 | RFP S3-01: chủ sở hữu SKU là 営業オペレーション, vòng created→review→active→retired, người đề xuất không tự duyệt; thiết kế chỉ cho `admin` ghi, không vòng duyệt | Issue làm rõ (Q&A) — ảnh hưởng lớn tới scope; giả định giữ RBAC hiện tại |
| 15 | SCR-010 §9 ghi chú cột vs database-design §3.3 dòng `skus` | Spec ghi `unit`, `trace_lane`, `updated_at` "chưa có trong database-design" nhưng DB design đã có. Unique `upper(code)` thì DB design chưa ghi | Sửa spec; bổ sung unique index vào DB design |
| 16 | SCR-010 item 10.2-1/4, 10.4-1/3, 10.7-4 | Tự viết hoa mã, danh sách đơn vị, khóa code/unit/trace_lane đều INFERRED | Issue làm rõ (BrSE task) |
| 17 | SCR-010 item 2 vs SCR-011 item 1-2 | SCR-010 thiết kế 4 tab master trong layout chung; SCR-011 nói "bỏ tab master, điều hướng qua menu trái" — mâu thuẫn điều hướng | Sửa thiết kế: chốt 1 cách cho cả nhóm `/master/*` |
| 18 | SCR-010 §9 PATCH | Trigger 0800 cũ trả lỗi tiếng Việt; spec đổi sang hint M_130 nhưng không nói cách API parse `detail` khi nhiều cột | Giả định: `detail` = CSV tên cột; ghi vào task BE |

---

## SCR-011 — 顧客・顧客SKU契約 (F01 master)

### 1. Tổng quan
- Mục đích: quản lý khách hàng và hợp đồng khách–SKU có phiên bản (`delivery_term`, `window_rule` có thể NULL = 未確定), đầu vào loại trừ khi phân bổ.
- Role: `admin` (sửa khách + hợp đồng), `sales_manager` (sửa hợp đồng), các vai trò khác chỉ xem; `auditor` xem 全履歴.

### 2. Khu vực / component
- Tiêu đề + 2 tab (顧客 / 顧客SKU契約) đồng bộ query `?tab=`.
- Tab 顧客: từ khóa, gồm ngưng dùng, nút thêm, bảng khách (số hợp đồng + badge 未確定), dialog khách hàng (3–7).
- Tab 契約: ghi chú thông lệ M_140 (8), thanh đếm chưa chốt M_151 (9), bộ lọc khách/SKU/rule/pending/phạm vi phiên bản (10–14), nút đăng ký (15), bảng hợp đồng 12 cột (16), panel lịch sử phiên bản (17), dialog đăng ký phiên bản (18–18.13).

### 3. Dữ liệu
- Bảng: `customers` (+`updated_at`), `customer_sku_agreements` (+`change_reason`, `created_by`, `created_at`; UNIQUE (`agreement_code`,`effective_from`); 1 mã ↔ 1 cặp), `skus`, `order_lines` (`line_status`, `agreement_id`), `audit_log`.
- API: `GET/POST /api/customers`, `PATCH /api/customers/{id}`, `GET /api/customer-sku-agreements`, `GET /api/customer-sku-agreements/history`, `POST /api/customer-sku-agreements` → RPC `create_customer_sku_agreement_version()` (advisory lock, kiểm active, kiểm ngày, insert, cập nhật `order_lines`, audit), `DELETE /api/customer-sku-agreements/versions/{id}`. View `customer_sku_agreement_versions_view`. Trigger chặn UPDATE/DELETE khi `effective_from ≤ app_today()`. Job 00:05 JST.
- BR: BR-DELWIN-01, BR-ALLOC-ORDER, BR-TIME-01, BR-INV-03, BR-POD-01. ADR-003 (bảng phiên bản), ADR-004 (allocation exclusion pipeline — `AGREEMENT_PENDING`), ADR-002 (RPC đa bước), ADR-007 (audit).
- Message: M_140–M_155 + chung.

### 4. Validation / trạng thái / luồng đặc biệt
- `window_rule`: 4 radio không chọn sẵn; thiếu key → 400 M_141; `null` chỉ hợp lệ khi gửi tường minh; chọn 未確定 → xác nhận M_146. Không DEFAULT ở DB/API. Không bao giờ hiện giá trị "đề xuất" cho NULL.
- Phiên bản mới: 18.6 bắt chọn lại; trùng phiên bản trước → M_153; lý do bắt buộc (M_06).
- `effective_from ≥ app_today()` (cho phép hôm nay, INFERRED) → M_143; trùng ngày → M_144.
- Mã `^AGR-\d{3,}$` (INFERRED); mã dùng cho cặp khác → M_152; cặp đã có hợp đồng → M_142; khách/SKU inactive → M_149/M_148.
- Mã khách readonly sau tạo (M_155, INFERRED); optimistic lock khách (M_22); ngưng dùng khách xác nhận M_31.
- Trạng thái phiên bản tính lúc đọc: 適用中 / 適用予定 / 適用終了; hủy chỉ phiên bản tương lai (M_154, API → 409 M_145).
- Side-effect lên `order_lines` khi phiên bản bắt đầu áp dụng (business_review ↔ open) — trong RPC (hôm nay) hoặc job 00:05 (tương lai).
- Ghi bắt MFA (admin, sales_manager đặc quyền).

### 5. Ràng buộc giờ lái xe 2024
- **Không.** (`delivery_term` ảnh hưởng checkpoint POD BR-POD-01, không phải giờ lái.)

### 6. Sub-task đề xuất
- [BE] Migration `customers.updated_at` + regex code + seed CUS-001–005 — S
- [BE] `GET/POST/PATCH /api/customers`: tìm/lọc/phân trang, đếm hợp đồng active/pending, khóa code (M_155), optimistic lock, audit — M
- [BE] Migration `customer_sku_agreements` (cột mới, unique, CHECK, không DEFAULT, ràng buộc mã ↔ cặp) + trigger khóa phiên bản đã hiệu lực + RLS (SELECT all, ghi chỉ qua RPC) — M
- [BE] Migration dữ liệu 15 hợp đồng R-04 (AGR-008/014 NULL) + test `count(window_rule is null)=2` — S
- [BE] View `customer_sku_agreement_versions_view` + `GET /api/customer-sku-agreements` (lọc, scope, pendingCount, heldOrderLines) + `/history` — M
- [BE] RPC `create_customer_sku_agreement_version()` (advisory lock, mọi kiểm tra M_142–M_153, insert, audit) + route POST zod (key `window_rule` bắt buộc) — L
- [BE] Logic chuyển `order_lines` business_review ↔ open khi phiên bản áp dụng hôm nay (trong RPC) — M
- [Infra] Job 00:05 JST hằng ngày (Vercel Cron/pg_cron) áp phiên bản đến ngày + idempotent + giám sát — M
- [BE] `DELETE …/versions/{id}` (chỉ tương lai, 409 M_145, audit before) — S
- [FE] Khung màn + tab đồng bộ query, giữ bộ lọc riêng từng tab — S
- [FE] Tab 顧客: tìm/lọc, bảng + badge 未確定, dialog khách hàng (readonly code khi sửa, M_31 ngưng dùng) — M
- [FE] Tab 契約: ghi chú M_140, thanh M_151, 5 bộ lọc, bảng 12 cột (badge 業務確認待ち, nền vàng, version state), link SCR-040 — L
- [FE] Panel lịch sử phiên bản (v1, v2…, effective_to tính) — S
- [FE] Dialog đăng ký phiên bản: 2 chế độ, radio không chọn sẵn, 18.7 giải thích + ví dụ, M_146 xác nhận, M_141, hủy phiên bản M_154 — L
- [QA] Test case: invariants window_rule NULL (không default ở UI/API/DB), phiên bản (hôm nay/tương lai/trùng/giống trước), hủy, phân quyền admin vs sales_manager, migration R-04 — M
- [QA] Test tích hợp side-effect `order_lines` + job 00:05 + liên thông SCR-042 `AGREEMENT_PENDING` — M
- [BrSE] Làm rõ: cho phép `effective_from = hôm nay`, mẫu mã AGR, mặc định ẩn khách ngưng dùng, khóa mã khách, hành vi side-effect `order_lines`, công thức 1/3·1/2 (Q&A-B02) — S

### 7. Gap / mâu thuẫn
| # | Vị trí | Mô tả | Đề xuất |
|---|---|---|---|
| 19 | SCR-011 item 18-9 vs SCR-015 item 8-7 | Hợp đồng cho `effective_from = hôm nay` (INFERRED), ngưỡng nhiệt bắt ≥ ngày mai — hai bảng phiên bản ADR-003 xử lý khác nhau; bản tạo hôm nay khóa ngay lập tức (trigger `≤ app_today()`), không sửa/hủy được nếu nhập sai | Issue làm rõ; nếu giữ "hôm nay" thì thêm xác nhận rõ ràng |
| 20 | SCR-011 item 18-14 | Toàn bộ side-effect lên `order_lines` (đổi trạng thái, trỏ `agreement_id` sang bản mới, job 00:05) là INFERRED và chạm SCR-042; chưa rõ xử lý dòng `allocated` một phần | Issue làm rõ + sửa thiết kế (đối chiếu ADR-004, state machine đơn) |
| 21 | SCR-011 item 18-14 | Job 00:05 JST không có trong ADR nào cho hợp đồng (business-rules chỉ nhắc job 00:05 cho date-reversal expiry); ADR-001 nhắc giới hạn Cron | Sửa thiết kế: thêm vào ADR/infra spec; task Infra |
| 22 | SCR-011 §9 Dữ liệu vs database-design §3.4 | Spec ghi `change_reason`, `created_by`, `created_at`, `customers.updated_at` "chưa có" nhưng DB design đã có (cột kiểm soát chung + `change_reason`). Ràng buộc "1 mã chỉ thuộc 1 cặp" / bảng `customer_sku_agreement_heads` chưa có trong DB design | Sửa spec; chốt cách ràng buộc mã↔cặp (RPC vs bảng heads) |
| 23 | SCR-011 §9 POST `/api/customers` vs `common-format.md` Format_Code và SCR-010 §9 | Regex mã khách `^[A-Za-z0-9_-]{1,50}$` cho chữ thường, trong khi Format_Code là A–Z và SKU dùng `^[A-Z0-9_-]+$` | Sửa thiết kế: thống nhất regex (chỉ A–Z, tự upper) |
| 24 | SCR-011 item 7-5 | Ngưng dùng khách: không nói gì về phiên bản hợp đồng tương lai của khách đó | Issue làm rõ |
| 25 | SCR-011 item 16-8 | Màu 適用予定 không có trong `Status_Badge` — đề xuất bổ sung | Sửa thiết kế common-format (nhỏ) |
| 26 | SCR-011 §9 RLS | "INSERT/DELETE chỉ qua RPC security definer" nhưng DELETE endpoint không nêu RPC nào | Giả định: thêm RPC `cancel_customer_sku_agreement_version()` |

---

## SCR-015 — 温度帯ポリシー版管理 (F01 master)

### 1. Tổng quan
- Mục đích: quản lý phiên bản ngưỡng nhiệt 3 dải (常温/冷蔵/冷凍) theo `effective_from`, chỉ tạo phiên bản tương lai, preview ảnh hưởng.
- Role: `quality` ghi (`temp_policy:write`); warehouse, warehouse_lead, sales_planner, sales_manager, dispatcher, transport_manager, auditor chỉ xem; `admin` không thấy màn.

### 2. Khu vực / component
- Tiêu đề, ghi chú chính sách M_160 (1, 2), nút tạo (3).
- 3 thẻ ngưỡng đang hiệu lực (4).
- Bảng phiên bản tương lai + chênh với bản trước + sửa/hủy (5).
- Lọc dải + bảng lịch sử (usage count, badge state) (6, 7).
- Dialog tạo/sửa phiên bản + preview ảnh hưởng (number line) + số tham khảo 30 ngày (8–8.11).

### 3. Dữ liệu
- Bảng: `temp_zones` (chỉ code+name), `temp_zone_policy_versions` (+`updated_at`), `inbound_lines`, `shipments`, `deviations` (`policy_version_id`, usage count), `audit_log`.
- API: `GET /api/temp-policies`, `POST /api/temp-policies/preview` (hàm thuần TS `diffAcceptRanges` + SQL đếm 30 ngày), `POST /api/temp-policies` → RPC `create_temp_policy_version()`, `PATCH /api/temp-policies/{id}` → RPC `update_scheduled_temp_policy_version()` (`for update`, kiểm sau khi khóa), `DELETE /api/temp-policies/{id}`. View `temp_zone_policy_versions_view`. Hàm `effective_temp_policy(zone, at)`. Trigger `temp_policy_versions_lock_effective` + trigger BEFORE INSERT/UPDATE ≥ ngày mai.
- Nơi phải đổi sang hàm: `inbound_lines_with_temp_check`, `confirm_inbound_receipt()`, `confirm_shipment()`, `/api/temp-zones`, `formatTempZone()`.
- BR: BR-TEMP-01/02, BR-TIME-01, BR-INV-03. ADR-003 (versioned policy), ADR-008 (2-layer temp check at inbound — người tiêu thụ ngưỡng), ADR-007 (audit).
- Message: M_160–M_173 + chung.

### 4. Validation / trạng thái / luồng đặc biệt
- `effective_from ≥ app_today()+1` (M_161), trùng (zone, ngày) → M_163; `min_c ≤ max_c` (M_162); −50.0..50.0, 1 số lẻ (M_05); 下限なし chỉ 冷凍 (M_171, INFERRED); giống bản gốc → M_167; lý do 10–500 (M_06).
- Phiên bản đã hiệu lực khóa (trigger, 409 M_164); qua 0:00 JST khi đang mở dialog → 409 M_164 + reload; đua sửa → M_22 / M_23.
- Preview: newlyOut/newlyIn theo đoạn đóng, biên = đạt, NULL = −∞; preview lỗi không chặn lưu.
- Xác nhận M_169 trước khi lưu; toast M_170.
- State 適用予定 → 適用中 → 適用終了 tính lúc đọc, không cần job.
- Thiếu bản hiệu lực cho 1 dải → thẻ đỏ, không tự điền mặc định.

### 5. Ràng buộc giờ lái xe 2024
- **Không.** (Ngưỡng nhiệt; `shipments` truck temp chỉ dùng cho preview/usage.)

### 6. Sub-task đề xuất
- [BE] Migration `temp_zone_policy_versions` (+`updated_at`), bỏ `min_c/max_c` khỏi `temp_zones`, seed bản 2026-04-01 đúng RFP — M
- [BE] Hàm `effective_temp_policy()` + trigger khóa bản đã hiệu lực + trigger ≥ ngày mai + RLS SELECT mọi vai trò, ghi chỉ qua RPC — M
- [BE] Refactor nơi dùng ngưỡng sang `effective_temp_policy` + lưu `policy_version_id` (`confirm_inbound_receipt`, `confirm_shipment`, view inbound, `/api/temp-zones`, `formatTempZone`) — L
- [BE] View `temp_zone_policy_versions_view` (effective_to, state, usage_count) + `GET /api/temp-policies` — M
- [BE] RPC `create_temp_policy_version()` + `update_scheduled_temp_policy_version()` + DELETE (lock-after-check, optimistic lock, audit) + routes — L
- [BE] `diffAcceptRanges` (hàm thuần + unit test các ca item 8-10) + `POST /api/temp-policies/preview` + SQL đếm 30 ngày — M
- [FE] Trang: ghi chú M_160, 3 thẻ ngưỡng hiện hành (công thức, 下限なし, U+2212), bảng tương lai (diff đỏ/xanh), lịch sử + lọc + phân trang — M
- [FE] Dialog tạo/sửa: chọn dải → nạp bản gốc, 下限なし chỉ 冷凍, date picker chặn ≤ hôm nay, đếm ký tự, M_172, M_169 — M
- [FE] Preview ảnh hưởng: debounce 500ms, câu M_165/M_166, number line có chữ (WCAG), M_168, trạng thái 計算中/lỗi — M
- [QA] Test case: biên ngưỡng, NULL cận dưới, tương lai/hiệu lực/0:00 JST, đua sửa, quyền (quality vs admin 403), preview đúng các ca — M
- [QA] Test hồi quy: giao dịch cũ giữ `policy_version_id`, SCR-022/SCR-053/SCR-010 đọc ngưỡng đúng phiên bản theo ngày — M
- [BrSE] Làm rõ: admin xem được hay không (ký hiệu「—」), 下限なし chỉ 冷凍, ngày seed 2026-04-01, cửa sổ 30 ngày của preview — S
- [Infra] Cơ chế role service bỏ qua trigger ≥ ngày mai cho seed/migration (không lộ cho app) — S

### 7. Gap / mâu thuẫn
| # | Vị trí | Mô tả | Đề xuất |
|---|---|---|---|
| 27 | SCR-015 §7 ghi chú cuối vs role-permission-matrix chú thích ¹ | `admin` không thấy màn (ký hiệu「—」, INFERRED) nhưng RLS SELECT phải mở cho admin để SCR-010/022 đọc ngưỡng (§9) | Issue làm rõ; giả định theo matrix (ẩn màn, RLS mở) |
| 28 | SCR-015 item 8-5 | Chỉ 冷凍 được `min_c = NULL` là INFERRED; DB cho NULL mọi dải | Issue làm rõ; giả định chặn ở API |
| 29 | SCR-015 §9 Dữ liệu vs database-design §3.4 | Spec ghi `updated_at` "chưa có" nhưng DB design có "cột kiểm soát chung" `updated_at` cho bảng phiên bản; seed 2026-04-01 INFERRED ở cả hai | Sửa spec; BrSE xác nhận ngày seed |
| 30 | SCR-015 §9 trigger | "trừ migration seed chạy bằng role service" — cơ chế bypass trigger không được định nghĩa (rủi ro bảo mật) | Sửa thiết kế: định nghĩa rõ (session var / role check) |
| 31 | SCR-015 item 8-11, M_168 | Đếm `shipments` "đơn có SKU thuộc dải" — một shipment có nhiều SKU nhiều dải thì đếm thế nào chưa rõ; cửa sổ 30 ngày INFERRED | Giả định: đếm shipment nếu có ≥ 1 SKU thuộc dải; issue làm rõ |
| 32 | SCR-015 item 7-5 | Usage count link tới màn danh sách "giai đoạn sau" — chỉ hiện số | Giả định: không link ở release này |
| 33 | SCR-015 §9 DELETE | Xóa vật lý phiên bản tương lai (FK chặn nếu đã dùng) — cần xác nhận phù hợp nguyên tắc append-only ADR-007 (audit giữ `before`) | Giả định chấp nhận (audit đủ); ghi rõ trong ADR |

---

## Ghi chú cho backlog
- Chỉ **SCR-002** chạm ràng buộc giờ lái 2024 (thẻ 4.8, 4.10, 4.11; phụ 4.7, 4.9) → gắn label `driver-hours-2024` và dependency vào epic ADR-006 / SCR-061 (`get_driver_month_restraint` dùng chung).
- Phụ thuộc chéo: SCR-001 → mọi màn (middleware, `current_app_role`); SCR-015 → SCR-010/022/053 (`effective_temp_policy`); SCR-011 → SCR-040/042 (`order_lines.line_status`, `AGREEMENT_PENDING`); SCR-002 phụ thuộc dữ liệu của gần như mọi feature → nên làm sau cùng trong F12 hoặc làm khung trước, thẻ bổ sung dần.
- Nhiều spec ghi "chưa có trong database-design" đã lỗi thời (DB design đã cập nhật) → 1 task BrSE/PM rà đồng bộ spec ↔ DB design trước sprint.
