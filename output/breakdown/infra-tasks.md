# Infra Tasks: Product B — Yuki Cold Logistics (LAB-5)

**Date**: 2026-11-10 | **Total**: TBD

---

## E1: Nền tảng & sửa prototype trái RFP

### S1.5: Dựng hạ tầng Tokyo, CI và phân trang 50 dòng

#### INFRA-1.5.1: Dựng Supabase Tokyo dev/stg, Storage bucket private và bật pg_cron
Tạo project Supabase region ap-northeast-1 cho dev/stg, bucket inbound-photos private (≤10MB, JPG/PNG/HEIC), bật pg_cron, biến môi trường Vercel theo môi trường.

- [ ] 2 project Supabase Tokyo + Vercel env
- [ ] Bucket inbound-photos private + policy theo vai trò
- [ ] Bật extension pg_cron, timezone job JST
- [ ] Tài liệu cách chạy migration từng môi trường

**AC:**
- Upload file > 10MB hoặc sai loại bị bucket từ chối
- Job pg_cron thử chạy được trên stg

#### INFRA-1.5.2: Thiết lập CI GitHub Actions: lint, typecheck, test và kiểm migration
Workflow GitHub Actions chạy lint, typecheck, unit test, supabase db reset + test SQL trên PR; deploy stg khi merge.

- [ ] Job lint + typecheck + vitest
- [ ] Job supabase start + db reset + test SQL
- [ ] Deploy stg khi merge nhánh chính
- [ ] Chặn merge khi job đỏ

**AC:**
- PR có migration lỗi bị CI đỏ
- Merge vào nhánh chính tự deploy stg

## E2: F12 Xác thực & phân quyền

### S2.1: Đăng nhập SSO, MFA và quản lý phiên (SCR-001)

#### INFRA-2.1.1: Cấu hình OIDC provider IdP công ty cho dev/stg/prod và cờ đăng nhập mật khẩu
Đăng ký Supabase OIDC provider với IdP công ty từng môi trường, tắt Email provider ở prod, biến AUTH_PASSWORD_LOGIN_ENABLED, redirect URL /auth/callback.

- [ ] Client id/secret IdP lưu ở secret store
- [ ] Tắt Email provider ở prod
- [ ] AUTH_PASSWORD_LOGIN_ENABLED theo môi trường
- [ ] Redirect URL + logout URL đăng ký ở IdP

**AC:**
- Prod không đăng nhập được bằng mật khẩu
- Dev/stg đăng nhập SSO thành công với tài khoản test IdP

## E5: F03 Tồn kho & lô

### S5.2: Chi tiết lô, lịch sử sự kiện và cách ly thủ công (SCR-031)

#### INFRA-5.2.3: Tạo bucket quality-evidence riêng tư và job dọn file bằng chứng mồ côi
Bucket Storage quality-evidence private (đường dẫn {yyyy}/{uuid}) + storage policy; job định kỳ xóa file không được tham chiếu sau 24h (dùng chung SCR-031/037).

- [ ] Bucket private + policy chỉ server (service role) ghi
- [ ] Quy ước đường dẫn {yyyy}/{uuid}
- [ ] Job dọn file > 24h không có tham chiếu trong lot_status_events/deviations

**AC:**
- Người dùng không đọc được file qua URL công khai, chỉ qua signed URL
- File mồ côi quá 24h bị xóa, file đang được tham chiếu giữ nguyên

## E6: F04 Đơn hàng & phân bổ

### S6.6: Duyệt ngoại lệ 日付逆転 (SCR-044)

#### INFRA-6.6.2: Tạo bucket consent-evidence riêng tư và policy, dọn file tạm mồ côi
Bucket Storage consent-evidence private + storage policy (chỉ server ghi), đường tạm cho upload trước RPC (G-4), mở rộng job dọn file mồ côi sang bucket này.

- [ ] Bucket private, đường {yyyy}/{uuid}, thư mục tạm
- [ ] Policy: chỉ service role ghi/đọc, người dùng chỉ xem qua signed URL 5 phút
- [ ] Job dọn file tạm > 24h không có yêu cầu tham chiếu

**AC:**
- File bằng chứng không truy cập được qua URL công khai
- File tạm mồ côi > 24h bị xóa

## E8: F07 Lập tuyến & công bố (phần không thuộc luật giờ lái)

### S8.3: Tích hợp bản đồ IF-MAP-01 và thông báo IF-MAIL-01

#### INFRA-8.3.1: Cấu hình secret, env và egress cho IF-MAP-01
Đặt API key IF-MAP-01 vào secret Supabase/Vercel, biến env theo môi trường, cho phép egress tới endpoint bản đồ.

- [ ] Secret cho dev/stg/prod
- [ ] Biến endpoint + timeout
- [ ] Kiểm egress từ server
- [ ] Ghi tài liệu xoay vòng key

**AC:**
- Server stg gọi được API bản đồ
- Key không xuất hiện trong repo/log

#### INFRA-8.3.2: Dựng notification_outbox và worker gửi mail IF-MAIL-01
Bảng notification_outbox (route_published/route_changed/route_cancelled, 送信待ち/送信済/送信失敗) + worker Supabase cron/edge function gửi qua IF-MAIL-01, retry 1/5/15/60 phút rồi mỗi 60 phút tới 24h, thất bại báo lên SCR-002; tài xế không email không chặn.

- [ ] Khóa hàng khi worker lấy job
- [ ] Lịch retry tham số hóa
- [ ] Secret mail relay
- [ ] Cờ cảnh báo cho SCR-002

**AC:**
- Mail relay lỗi → retry đúng lịch, quá 24h → 送信失敗
- Worker chạy 2 instance không gửi trùng

## E9: ★ Ràng buộc giờ lái xe tải 2024 (改善基準告示)

### S9.10: Sự cố bất khả kháng và báo cáo tuân thủ (SCR-063)

#### INFRA-9.10.2: [DRV] Cấu hình bucket event-evidence và job dọn file mồ côi
Storage bucket riêng event-evidence (private, policy theo vai trò, signed URL 5 phút) + job hằng ngày xóa file không có bản ghi unforeseeable_events.

- [ ] Giới hạn PDF/JPEG/PNG ≤ 10MB ở policy
- [ ] Job lịch hằng ngày + log
- [ ] Không public URL

**AC:**
- Truy cập file không có signed URL → 403
- File upload nhưng tạo bản ghi thất bại bị xóa sau lần chạy job

## E11: Kiểm thử tích hợp, UAT & quản lý dự án

### S11.3: Quản lý sprint, báo cáo tiến độ và phát hành Phase 1

#### INFRA-11.3.3: Chuẩn bị runbook phát hành và khôi phục cho production
Runbook deploy Vercel + migration Supabase (region Tokyo), kiểm PITR (RPO ≤ 15 phút), khôi phục ≤ 4h, cảnh báo uptime 05:00–23:00 JST.

- [ ] Thứ tự migration + rollback
- [ ] Thử khôi phục PITR trên staging
- [ ] Cấu hình cảnh báo uptime

**AC:**
- Runbook đã chạy thử trên staging
- Thời gian khôi phục đo được ≤ 4h
