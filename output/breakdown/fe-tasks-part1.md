# Frontend Tasks: Product B — Yuki Cold Logistics (LAB-5)

**Date**: 2026-11-10 | **Total**: TBD

---

## E1: Nền tảng & sửa prototype trái RFP

### S1.2: Chuyển message sang mã M_xx và giao diện tiếng Nhật

#### FE-1.2.2: Dựng catalog message tiếng Nhật và chuyển UI prototype sang tiếng Nhật
Sinh module TS từ message-list (M_xx → text JP có tham số), hàm t(messageId, params), chuyển nhãn/thông báo các màn prototype sang tiếng Nhật theo common-format.

- [ ] Module messages.ts + kiểm thiếu mã lúc build
- [ ] Toast/vùng lỗi dùng messageId từ API
- [ ] Đổi nhãn menu, bảng, nút sang JP
- [ ] Định dạng ngày/số theo common-format

**AC:**
- Không còn chuỗi tiếng Việt hiển thị trên UI
- Lỗi API hiển thị đúng text JP theo messageId

### S1.3: Mở rộng 9 vai trò, RBAC và tách người lập / người duyệt

#### FE-1.3.3: Cập nhật role-permissions.ts, decideRouteAccess và menu theo 9 vai trò
Viết lại role-permissions.ts theo role-permission-matrix (quyền màn + thao tác), decideRouteAccess dùng bảng mới, menu trái ẩn mục không có quyền.

- [ ] Bảng quyền 9 vai trò × màn
- [ ] decideRouteAccess + unit test
- [ ] Menu trái lọc theo quyền
- [ ] Nút ghi ẩn khi chỉ có quyền đọc

**AC:**
- Unit test 9 vai trò × màn khớp ma trận
- URL màn không có quyền chuyển về trang báo M_20

### S1.5: Dựng hạ tầng Tokyo, CI và phân trang 50 dòng

#### FE-1.5.4: Tạo component List_Paging dùng chung đồng bộ query string
Component phân trang theo common-format List_Paging (tổng, trang, đồng bộ ?page=), dùng chung cho mọi bảng danh sách.

- [ ] Hiển thị tổng + số trang
- [ ] Đồng bộ ?page= với URL
- [ ] Reset về trang 1 khi đổi bộ lọc
- [ ] aria-label tiếng Nhật

**AC:**
- Đổi trang giữ nguyên bộ lọc trên URL
- Bảng prototype hiện có dùng component này

## E2: F12 Xác thực & phân quyền

### S2.1: Đăng nhập SSO, MFA và quản lý phiên (SCR-001)

#### FE-2.1.5: Làm màn đăng nhập tiếng Nhật và panel thông báo chưa có vai trò
Màn login: nút SSO, banner + form demo khi cờ bật, validate, map lỗi Supabase/?error= sang M_100–M_106, M_40/M_41; panel no-role trong layout (app) ẩn sidebar, nút tải lại/đăng xuất.

- [ ] Layout production vs demo theo cờ
- [ ] Vùng lỗi chỉ map giá trị whitelist
- [ ] Ghi chú thiết bị dùng chung, cấp tài khoản
- [ ] Panel no-role thay nội dung + sidebar

**AC:**
- Prod không render form mật khẩu
- ?error=<giá trị lạ> không hiển thị gì

#### FE-2.1.6: Làm bộ đếm idle, dialog cảnh báo 60 giây và đồng bộ đa tab
Idle timer client theo tham số server, dialog cảnh báo + đếm ngược 60s, BroadcastChannel('ycl-activity') đồng bộ đa tab, gửi heartbeat khi có thao tác.

- [ ] Cảnh báo trước hết hạn 60s
- [ ] Thao tác ở tab khác reset bộ đếm
- [ ] Hết giờ → full page load về /login?error=idle_timeout
- [ ] Polling nền không reset bộ đếm

**AC:**
- Hai tab mở: thao tác ở tab A không làm tab B hiện cảnh báo
- Hết đếm ngược tự đăng xuất

### S2.2: Trang chủ theo vai trò (SCR-002, trừ thẻ giờ lái)

#### FE-2.2.4: Làm trang chủ, component thẻ chung và tự làm mới 5 phút
Header + thời điểm tổng hợp + nút làm mới, auto-refresh theo visibilitychange, component thẻ (tone, xám 対応不要 khi 0, link/không link, aria), lưới 3/2/1 cột, banner M_110, giữ số cũ khi lỗi.

- [ ] Skeleton loading, 更新失敗 giữ số cũ
- [ ] Component thẻ + màu kèm chữ (WCAG 2.2 AA)
- [ ] Lưới responsive + banner M_110
- [ ] Chừa slot render thẻ 4.8/4.11 cho E9

**AC:**
- Tab ẩn không gọi refresh
- Lỗi 500 vẫn giữ số cũ và hiện 更新失敗

### S2.3: Quản lý người dùng và vai trò (SCR-018)

#### FE-2.3.3: Làm trang danh sách user có bộ lọc đồng bộ URL và chế độ chỉ đọc
Bộ lọc (debounce 300ms, vai trò gồm 未割当, trạng thái, chưa MFA) đồng bộ URL + preset từ SCR-002, bảng user (badge MFA, trạng thái, dòng 自分), phân trang, auditor chỉ đọc.

- [ ] Bộ lọc + URL sync + preset ?role=none, ?mfa=unverified
- [ ] Bảng + badge + lần đăng nhập cuối
- [ ] Skeleton 5 dòng, rỗng M_32, lỗi tải
- [ ] auditor không thấy control ghi

**AC:**
- Mở link từ SCR-002 lọc sẵn đúng
- auditor không có select vai trò/nút vô hiệu

#### FE-2.3.4: Làm dialog đổi vai trò, vô hiệu hóa và hộp kết quả của SCR-018
Select vai trò trong ô mở dialog (M_125 / M_31, cảnh báo bỏ vai trò), dialog vô hiệu hóa (lý do 10–500, bộ đếm), xác nhận kích hoạt lại (M_124), hộp kết quả map lỗi.

- [ ] Hủy/lỗi trả select về giá trị cũ
- [ ] Đang lưu khóa mọi dòng
- [ ] 409 tự tải lại dòng
- [ ] Hộp kết quả role=status/alert

**AC:**
- Hủy dialog không gọi API và select về giá trị cũ
- Không thể chọn vô hiệu hóa chính mình

