# Task Breakdown: Product B — Yuki Cold Logistics (LAB-5)

**Date**: 2026-11-10 | **Source**: pre-estimate | **Level**: L3

---

## E1: Nền tảng & sửa prototype trái RFP
Sửa các chỗ prototype LAB-2 làm trái RFP (G-01/02/03 ngưỡng nhiệt, G-15/16 vai trò, G-21 giao diện JP) và dựng nền dùng chung: migration audit/sổ di chuyển/trạng thái lô/master, hạ tầng Tokyo, CI, phân trang 50. Mọi epic tính năng phụ thuộc epic này.
Stories: 5 | Roles: Backend, Frontend, Infra

### S1.1: Tạo migration dữ liệu dùng chung cho mọi feature
- Backend: Tạo audit_log append-only có correlation_id và trigger audit chung
- Backend: Tạo inventory_movements, lot_status_events và enum trạng thái lô, đơn
- Backend: Tạo master locations, suppliers và bảng deviations, idempotency_keys

### S1.2: Chuyển message sang mã M_xx và giao diện tiếng Nhật
- Backend: Thay raise exception tiếng Việt bằng P0001 kèm hint mã M_xx
- Frontend: Dựng catalog message tiếng Nhật và chuyển UI prototype sang tiếng Nhật

### S1.3: Mở rộng 9 vai trò, RBAC và tách người lập / người duyệt
- Backend: Mở rộng profiles 9 vai trò và viết current_app_role, has_role
- Backend: Viết lại RLS bảng prototype theo ma trận quyền 9 vai trò
- Frontend: Cập nhật role-permissions.ts, decideRouteAccess và menu theo 9 vai trò

### S1.4: Sửa ngưỡng nhiệt đúng RFP và lưu theo phiên bản
- Backend: Tạo temp_zone_policy_versions, seed RFP và hàm effective_temp_policy
- Backend: Chuyển nơi đọc ngưỡng sang effective_temp_policy và lưu policy_version_id

### S1.5: Dựng hạ tầng Tokyo, CI và phân trang 50 dòng
- Infra: Dựng Supabase Tokyo dev/stg, Storage bucket private và bật pg_cron
- Infra: Thiết lập CI GitHub Actions: lint, typecheck, test và kiểm migration
- Backend: Viết helper phân trang 50 dòng dùng chung cho API danh sách
- Frontend: Tạo component List_Paging dùng chung đồng bộ query string

## E2: F12 Xác thực & phân quyền
Đăng nhập SSO OIDC + MFA vai trò đặc quyền thay email/mật khẩu (G-20), trang chủ theo vai trò và quản lý người dùng/vai trò (SCR-001, SCR-002, SCR-018). Thẻ giờ lái 4.8/4.10/4.11 của SCR-002 nằm ở E9.
Stories: 3 | Roles: Backend, Frontend, QA (Manual), Infra, BrSE

### S2.1: Đăng nhập SSO, MFA và quản lý phiên (SCR-001)
- Infra: Cấu hình OIDC provider IdP công ty cho dev/stg/prod và cờ đăng nhập mật khẩu
- Backend: Viết /auth/sso/start và /auth/callback có PKCE, kiểm MFA và JIT profile
- Backend: Viết middleware chặn phiên sai và mở rộng GET /api/me
- Backend: Làm app_sessions, heartbeat idle 15 phút, thiết bị dùng chung và logout
- Frontend: Làm màn đăng nhập tiếng Nhật và panel thông báo chưa có vai trò
- Frontend: Làm bộ đếm idle, dialog cảnh báo 60 giây và đồng bộ đa tab
- QA (Manual): Viết test case + chạy test SCR-001

### S2.2: Trang chủ theo vai trò (SCR-002, trừ thẻ giờ lái)
- Backend: Viết lại get_home_summary khung và route GET /api/home-summary
- Backend: Viết truy vấn thẻ kho, chất lượng, đơn và hợp đồng của trang chủ
- Backend: Viết truy vấn thẻ tuyến chưa gán, chưa công bố và kiểm hiệu năng
- Frontend: Làm trang chủ, component thẻ chung và tự làm mới 5 phút
- QA (Manual): Viết test case + chạy test SCR-002

### S2.3: Quản lý người dùng và vai trò (SCR-018)
- Backend: Viết RPC đổi vai trò, vô hiệu hóa user và route PATCH tương ứng
- Backend: Mở rộng GET /api/users có lọc, phân trang 50 và RLS profiles
- Frontend: Làm trang danh sách user có bộ lọc đồng bộ URL và chế độ chỉ đọc
- Frontend: Làm dialog đổi vai trò, vô hiệu hóa và hộp kết quả của SCR-018
- QA (Manual): Viết test case + chạy test SCR-018
- BrSE: Xác nhận với khách các điểm INFERRED của xác thực và trang chủ

## E3: F01 Master & chính sách nhiệt
Master SKU (khóa trường khi đã dùng), khách hàng + hợp đồng khách–SKU có phiên bản (window_rule NULL = 未確定, không mặc định) và quản lý phiên bản ngưỡng nhiệt (SCR-010, SCR-011, SCR-015). Bảng temp_zone_policy_versions và effective_temp_policy dựng ở E1.
Stories: 4 | Roles: Backend, Frontend, QA (Manual), BrSE

### S3.1: Quản lý master SKU (SCR-010)
- Backend: Mở rộng bảng skus, seed 12 SKU và trigger khóa trường đã dùng
- Backend: Viết sku_list_view và API GET/POST/PATCH /api/skus
- Frontend: Làm layout /master và trang danh sách SKU có bộ lọc, phân trang
- Frontend: Làm dialog thêm/sửa SKU khóa trường theo inUse và xác nhận ngưng dùng
- QA (Manual): Viết test case + chạy test SCR-010

### S3.2: Quản lý khách hàng (SCR-011 tab 顧客)
- Backend: Mở rộng customers, seed CUS-001–005 và API GET/POST/PATCH khách hàng
- Frontend: Làm khung màn SCR-011 và tab 顧客 có dialog khách hàng

### S3.3: Quản lý hợp đồng khách–SKU có phiên bản (SCR-011 tab 契約)
- Backend: Tạo migration customer_sku_agreements, trigger khóa và dữ liệu R-04
- Backend: Viết view phiên bản hợp đồng, API danh sách/lịch sử và hủy phiên bản
- Backend: Viết RPC create_customer_sku_agreement_version và route POST
- Backend: Cập nhật order_lines khi phiên bản áp dụng và lập job 00:05 JST
- Frontend: Làm tab 契約: bộ lọc, bảng hợp đồng 12 cột và panel lịch sử
- Frontend: Làm dialog đăng ký phiên bản hợp đồng và hủy phiên bản
- QA (Manual): Viết test case + chạy test SCR-011

### S3.4: Quản lý phiên bản ngưỡng nhiệt (SCR-015)
- Backend: Viết trigger khóa phiên bản ngưỡng, view lịch sử và GET /api/temp-policies
- Backend: Viết RPC tạo, sửa, hủy phiên bản ngưỡng và các route ghi
- Backend: Viết diffAcceptRanges và API xem trước ảnh hưởng ngưỡng mới
- Frontend: Làm trang chính sách nhiệt: thẻ hiện hành, bảng tương lai và lịch sử
- Frontend: Làm dialog tạo/sửa phiên bản ngưỡng có xem trước ảnh hưởng
- QA (Manual): Viết test case + chạy test SCR-015
- BrSE: Xác nhận với khách các điểm INFERRED của master SKU, hợp đồng, ngưỡng

## E4: F02 Nhập hàng
Kiểm hàng nhập theo dòng và xác nhận phiếu (SCR-022): field P0 + ảnh (G-19), kiểm nhiệt 2 lớp ADR-008 (A cảnh báo + cách ly, B chặn), xác nhận idempotent sinh lô, sổ di chuyển, sự kiện trạng thái và deviation. Bảng dùng chung (locations, suppliers, deviations, idempotency_keys, lot_status_events, inventory_movements) dựng ở E1.
Stories: 2 | Roles: Backend, Frontend, QA (Manual), BrSE

### S4.1: Tạo phiếu nhập và ghi kết quả kiểm từng dòng (SCR-022)
- Backend: Mở rộng inbound_receipts, inbound_lines và lots cho kiểm hàng nhập
- Backend: Viết API danh sách, tạo phiếu nhập và API master cho ô chọn
- Backend: Viết API thêm/sửa/xóa dòng nhập và upload ảnh kiểm hàng
- Frontend: Làm trang danh sách phiếu nhập và dialog tạo phiếu
- Frontend: Làm trang chi tiết phiếu nhập với bảng dòng 14 cột
- Frontend: Làm form dòng kiểm hàng tối ưu cửa kho và chụp/tải ảnh

### S4.2: Kiểm nhiệt 2 lớp và xác nhận phiếu idempotent (SCR-022)
- Backend: Viết hàm inbound_receipt_check và GET chi tiết phiếu kèm kết quả kiểm
- Backend: Viết RPC confirm_inbound_receipt idempotent và route POST confirm
- Frontend: Làm panel kiểm trước xác nhận, dialog xác nhận và dialog kết quả
- QA (Manual): Viết test case + chạy test SCR-022
- BrSE: Xác nhận với khách 7 điểm INFERRED của kiểm hàng nhập

## E5: F03 Tồn kho & lô
Tra cứu tồn kho theo lô (SCR-030), chi tiết lô + dòng thời gian sự kiện + cách ly thủ công (SCR-031), và máy trạng thái lô quarantine/on_hold/release/dispose có duyệt 2 người (SCR-037).
Stories: 3 | Roles: Backend, Frontend, QA (Manual), Infra, BrSE

### S5.1: Tra cứu tồn kho theo lô (SCR-030)
- Backend: Mở rộng lot_stock_view và thêm bảng tham số hệ thống app_parameters
- Backend: Xây RPC search_lot_stock và GET /api/lots với 10 bộ lọc, đạt ≤ 2s
- Frontend: Dựng màn tra cứu tồn kho: vùng lọc 10 điều kiện, tóm tắt và bảng lô
- QA (Manual): Viết test case + chạy test SCR-030

### S5.2: Chi tiết lô, lịch sử sự kiện và cách ly thủ công (SCR-031)
- Backend: Tạo view lot_event_timeline và API chi tiết lô, lịch sử sự kiện
- Backend: Viết RPC quarantine_lot và API cách ly, API tải bằng chứng dùng chung
- Infra: Tạo bucket quality-evidence riêng tư và job dọn file bằng chứng mồ côi
- Frontend: Dựng phần đầu, thông tin lô 12 trường và dialog cách ly SCR-031
- Frontend: Dựng timeline sự kiện lô: 10 loại, lọc, さらに表示, copy correlation ID
- QA (Manual): Viết test case + chạy test SCR-031

### S5.3: Máy trạng thái lô: cách ly, 保留, giải phóng, hủy có duyệt 2 người (SCR-037)
- Backend: Tạo migration máy trạng thái lô, lot_status_events và lot_disposal_requests
- Backend: Tạo quarantine_lot_view, GET /api/lots/quarantine và phân quyền lot:*
- Backend: Viết RPC hold_lot, release_lot và API 保留/giải phóng lô
- Backend: Viết RPC dispose_lot, decide_lot_disposal và API hủy lô duyệt 2 người
- Frontend: Dựng khung màn SCR-037: tab vùng, bộ lọc, bảng lô cách ly, cột thao tác
- Frontend: Dựng dialog 保留, giải phóng và hủy lô trên SCR-037
- Frontend: Dựng bảng hủy chờ duyệt và dialog duyệt/từ chối hủy lô
- QA (Manual): Viết test case + chạy test SCR-037
- BrSE: Làm rõ với khách các điểm mở của tồn kho và máy trạng thái lô

## E6: F04 Đơn hàng & phân bổ
Pipeline loại lô evaluate_lot_for_line (ADR-004, 5 lớp loại + FEFO) làm nền, rồi danh sách/đăng ký/hủy đơn (SCR-040/041), phân bổ lô (SCR-042), lịch sử giao theo khách (SCR-043) và duyệt ngoại lệ 日付逆転 (SCR-044).
Stories: 6 | Roles: Backend, Frontend, QA (Manual), Infra, BrSE

### S6.1: Pipeline evaluate_lot_for_line — nguồn duy nhất của BR-ALLOC-ORDER (làm trước)
- Backend: Tạo migration orders, order_lines, allocations cho luồng đơn và phân bổ
- Backend: Viết evaluate_lot_for_line lớp 1–3: 消費期限, vùng nhiệt, cách ly
- Backend: Viết evaluate_lot_for_line lớp 4 cửa sổ giao và lớp 5 日付逆転
- Backend: Refactor get_allocation_candidates và API ứng viên dùng pipeline
- Backend: Viết lại allocate_lot trên pipeline: khóa, đánh giá lại, bằng chứng
- QA (Manual): Viết test case + chạy test ma trận thứ tự lớp loại của pipeline
- BrSE: Làm rõ với khách các điểm mở của đơn hàng, phân bổ và ngoại lệ

### S6.2: Danh sách đơn hàng và hủy đơn (SCR-040)
- Backend: Tạo view order_list_view và GET /api/orders có lọc, phân trang
- Backend: Viết RPC cancel_order đảo ngược phân bổ và POST /api/orders/{id}/cancel
- Frontend: Dựng màn danh sách đơn: thanh lọc, bảng đơn và dialog hủy đơn
- QA (Manual): Viết test case + chạy test SCR-040

### S6.3: Đăng ký đơn hàng nhập tay (SCR-041)
- Backend: Xây API tra hợp đồng hiệu lực và kiểm trùng mã tham chiếu khách
- Backend: Viết lại RPC create_order và POST /api/orders với chuẩn lỗi chung
- Frontend: Dựng form đăng ký đơn: phần đầu và bảng dòng SKU động
- Frontend: Làm gửi form đơn: tóm tắt lỗi, Idempotency-Key, giữ form khi 401
- QA (Manual): Viết test case + chạy test SCR-041

### S6.4: Phân bổ lô cho dòng đơn và gửi ngoại lệ 日付逆転 (SCR-042)
- Backend: Tính lại line_status và orders.status không ghi khi đọc (G-2)
- Backend: Viết RPC unallocate_allocation và mở rộng GET /api/orders/{id}
- Backend: Viết create_date_reversal_request với upload trước, ghi ref sau (G-4)
- Frontend: Dựng khung SCR-042: thông tin đơn, đầu panel dòng, bảng phân bổ đã có
- Frontend: Dựng bảng lô ứng viên 8.1–8.12 có badge lý do loại và lô on_hold
- Frontend: Làm form phân bổ lô và dialog xác nhận lô quá 賞味期限
- Frontend: Dựng bảng yêu cầu ngoại lệ và dialog gửi ngoại lệ 日付逆転
- QA (Manual): Viết test case + chạy test SCR-042 (日付逆転, đồng thời, RBAC)

### S6.5: Lịch sử giao theo khách (SCR-043)
- Backend: Sửa delivery_history_list_view và GET /api/delivery-history, includeInactive
- Frontend: Dựng màn lịch sử giao: thanh lọc combobox và bảng có badge mốc
- QA (Manual): Viết test case + chạy test SCR-043

### S6.6: Duyệt ngoại lệ 日付逆転 (SCR-044)
- Backend: Tạo migration date_reversal_exception_requests, chuyển dữ liệu cũ, RBAC
- Infra: Tạo bucket consent-evidence riêng tư và policy, dọn file tạm mồ côi
- Backend: Viết RPC approve/reject_date_reversal_request có kiểm lại và tự phân bổ
- Backend: Viết job expire_date_reversal_requests 00:05 JST gồm PREVIOUS_CHANGED
- Backend: Xây API danh sách, chi tiết + kiểm lại, bằng chứng, duyệt/từ chối SCR-044
- Frontend: Dựng trang danh sách duyệt 日付逆転: tab, bộ lọc, menu và deep-link
- Frontend: Dựng panel chi tiết yêu cầu, khối kiểm lại và dialog duyệt/từ chối
- QA (Manual): Viết test case + chạy test SCR-044

