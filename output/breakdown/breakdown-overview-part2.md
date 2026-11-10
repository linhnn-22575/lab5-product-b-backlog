# Task Breakdown: Product B — Yuki Cold Logistics (LAB-5)

**Date**: 2026-11-10 | **Source**: pre-estimate | **Level**: L3

---

## E7: F05 Kiểm trước xuất
SCR-053 出荷前チェック: kiểm từng dòng phân bổ bằng quét/nhập tay, quét xe, niêm phong, nhiệt độ xe + hàng rồi 出荷確定 qua RPC confirm_shipment (7 tham số) có idempotency. Áp 2 sửa thiết kế: giờ xuất phát = planned_arrival + service_min của depot; confirm_shipment kiểm theo route_version published hiện hành. Phụ thuộc bảng tuyến của E8.
Stories: 3 | Roles: Backend, Frontend, QA (Manual), BrSE

### S7.1: Xác nhận xuất hàng an toàn qua RPC confirm_shipment
- Backend: Tạo migration xuất hàng và hàm effective_temp_policy
- Backend: Tạo view outbound_check_lines_view tính hạn, đảo ngày, ngoại lệ
- Backend: Viết confirm_shipment phần 1: quyền, idempotency, kiểm bản tuyến published
- Backend: Viết confirm_shipment phần 2: gom lỗi kiểm a–j không raise
- Backend: Viết confirm_shipment phần 3: ghi xuất kho và trạng thái đơn

### S7.2: API kiểm trước xuất
- Backend: Sửa giờ xuất phát thành planned_arrival + service_min của depot đầu
- Backend: Viết API GET pending-and-done và GET outbound-check
- Backend: Viết API POST /api/shipments với Idempotency-Key bắt buộc

### S7.3: Màn hình quét, kiểm và xác nhận xuất
- Frontend: Dựng trang /outbound: tab, bộ lọc, bảng chờ xuất và đã xuất
- Frontend: Dựng trang kiểm: header, khung tuyến, khung 積込確認
- Frontend: Làm bảng kiểm dòng hỗ trợ máy quét và nhập tay có lý do
- Frontend: Làm luồng xác nhận xuất với dialog, idempotency và xử lý lỗi
- QA (Manual): Viết test case SCR-053: kiểm a–j, idempotency, xung đột bản tuyến
- QA (Manual): Chạy test SCR-053 trên máy quét giả lập và 2 nhóm vai trò
- BrSE: Làm rõ giả định SCR-053: mã vạch, đảo ngày, lý do nhập tay

## E8: F07 Lập tuyến & công bố (phần không thuộc luật giờ lái)
Nền dữ liệu F07, phân quyền dispatcher/transport_manager, SCR-060 gán đơn/điểm dừng/segment, adapter IF-MAP-01, SCR-062 vòng đời phiên bản (giữ tuyến published khi có nháp), outbox + IF-MAIL-01. Phần dính giờ lái 2024 (BR-DRV-21 tự chèn nghỉ, cổng publish BR-DRV-20/22/23, driver_duty_records) nằm ở E9 và phụ thuộc các task ở đây.
Stories: 5 | Roles: Backend, Frontend, QA (Manual), Infra, BrSE

### S8.1: Dựng nền dữ liệu và phân quyền F07
- Backend: Tạo migration bảng tuyến lõi: xe, tài xế, routes, versions, stops, segments
- Backend: Tạo migration rejections, travel_time_cache và cột khách hàng/đơn
- Backend: Thêm vai trò dispatcher, transport_manager, auditor và RLS tuyến

### S8.2: Gán đơn, sắp điểm dừng và dựng segment tuyến
- Backend: Viết get_route_plan và create_route kèm API GET plan, POST routes
- Backend: Viết assign_orders_to_route kiểm 6 lý do và lưu rejections
- Backend: Viết build_route_segments dựng drive/wait/service và giờ đến
- Backend: Viết save_route_stops có khóa lạc quan, kiểm BR-TIME-02

### S8.3: Tích hợp bản đồ IF-MAP-01 và thông báo IF-MAIL-01
- Backend: Viết adapter IF-MAP-01 batch, timeout 10s, cache 7 ngày
- Backend: Viết API POST travel-times/refresh không ghi đè đoạn nhập tay
- Infra: Cấu hình secret, env và egress cho IF-MAP-01
- Infra: Dựng notification_outbox và worker gửi mail IF-MAIL-01

### S8.4: Màn hình lập tuyến SCR-060
- Frontend: Dựng khung trang lập tuyến và bảng đơn chưa gán
- Frontend: Làm bảng tuyến, dialog 新規ルート và các nút lưu/kiểm
- Frontend: Làm bảng điểm dừng dạng nháp với sắp xếp và service time
- Frontend: Làm dialog thêm điểm nghỉ và nhập tay thời gian di chuyển
- QA (Manual): Viết test case + chạy test SCR-060 (gán đơn, bản đồ, nháp)

### S8.5: Quản lý phiên bản tuyến, công bố và hủy (SCR-062)
- Backend: Viết bước ghi công bố (supersede, outbox) và API GET versions
- Backend: Viết create_route_version giữ tuyến published khi có bản nháp
- Backend: Viết discard_route_draft và cancel_route chặn khi có đơn đã xuất
- Backend: Viết route_version_diff và view KPI đổi tuyến sau công bố
- Frontend: Làm header, dải trạng thái, checklist và nút 公開 SCR-062
- Frontend: Làm bảng phiên bản, diff và dialog đổi/hủy/bỏ nháp
- QA (Manual): Viết test case + chạy test SCR-062 vòng đời phiên bản
- BrSE: Làm rõ giả định F07: 1 tài xế/ngày, IF-MAP-01, KPI, hủy tuyến

## E9: ★ Ràng buộc giờ lái xe tải 2024 (改善基準告示)
Epic ràng buộc đặc biệt: quản lý phiên bản quy tắc giờ làm tài xế, engine TS kiểm BR-DRV-01..14 (mỗi rule 1 task), chặn công bố tuyến vi phạm, kết quả bất biến, sự cố bất khả kháng, nhập giờ làm thực tế (SCR-064 mới) và thẻ cảnh báo trang chủ. Mọi giới hạn đọc từ driver_rule_versions, không viết cứng (ADR-006).
Stories: 13 | Roles: Backend, Frontend, QA (Manual), Infra, PM, BrSE

### S9.1: Quản lý phiên bản quy tắc giờ làm tài xế (SCR-016)
- Backend: [DRV] Tạo migration driver_rule_versions to-be, seed 2024-04 và hàm hiệu lực
- Backend: [DRV] Xây catalog tham số, hàm diff và API đọc/so sánh quy tắc
- Backend: [DRV] Làm RPC/API tạo nháp, sửa nháp, xóa nháp quy tắc
- Backend: [DRV] Làm kích hoạt, hủy, ảnh hưởng tuyến và job retire quy tắc
- Frontend: [DRV] Dựng trang danh sách và form chi tiết tham số quy tắc giờ làm
- Frontend: [DRV] Làm nút thao tác, dialog kích hoạt và màn so sánh quy tắc
- QA (Manual): [DRV] Viết test case + chạy test SCR-016

### S9.2: Khung engine kiểm giờ làm và lắp dữ liệu đầu vào
- Backend: [DRV] Dựng khung engine src/lib/compliance và model finding
- Backend: [DRV] Viết hàm SQL lắp dữ liệu đầu vào kiểm giờ làm theo ngày
- Backend: [DRV] Cài đặt hàm input_hash dùng chung cho kiểm và công bố

### S9.3: Kiểm thời gian ràng buộc theo ngày và số ngày dài trong tuần
- Backend: [DRV] Cài rule BR-DRV-04/05 ràng buộc/ngày 13h cảnh báo, 15h vi phạm
- Backend: [DRV] Cài rule BR-DRV-06 số ngày ràng buộc > 14h trong tuần

### S9.4: Kiểm thời gian nghỉ giữa 2 ca (休息期間)
- Backend: [DRV] Cài rule BR-DRV-07/08 nghỉ giữa ca 11h cảnh báo, 9h vi phạm

### S9.5: Kiểm giờ lái trung bình 2 ngày và 2 tuần
- Backend: [DRV] Cài rule BR-DRV-09 giờ lái trung bình 2 ngày 9h
- Backend: [DRV] Cài rule BR-DRV-10 giờ lái trung bình 2 tuần 44h

### S9.6: Lái liên tục 4h và tự chèn nghỉ khi lập tuyến
- Backend: [DRV] Cài module chuỗi lái và rule BR-DRV-11 lái liên tục 4h
- Backend: [DRV] Cài BR-DRV-21 tự chèn nghỉ 30 phút khi lưu tuyến SCR-060
- QA (Manual): [DRV] Viết test case + chạy test biên lái liên tục và tự chèn nghỉ

### S9.7: Kiểm giới hạn tháng, năm, tăng ca và gia hạn 労使協定
- Backend: [DRV] Cài rule BR-DRV-01 tăng ca tối đa 960h/năm tài chính
- Backend: [DRV] Cài rule BR-DRV-02 thời gian ràng buộc 3.300h/năm
- Backend: [DRV] Cài rule BR-DRV-03 thời gian ràng buộc 284h/tháng
- Backend: [DRV] Cài rule BR-DRV-14 công tắc gia hạn 労使協定 cho hạn năm/tháng

### S9.8: Lưu kết quả kiểm bất biến, xác nhận cảnh báo và cổng công bố
- Backend: [DRV] Tạo bảng kết quả kiểm, RPC save_compliance_check và trigger bất biến
- Backend: [DRV] Tạo bảng và RPC/API xác nhận cảnh báo giờ làm
- Backend: [DRV] Làm RPC publish_route: cổng tuân thủ, gắn rule version, ghi duty record
- Backend: [DRV] Làm API POST compliance-checks chạy engine và lưu kết quả

### S9.9: Màn timeline tài xế và vi phạm giờ làm (SCR-061)
- Backend: [DRV] Làm RPC get_route_timeline và API GET timeline tuyến
- Frontend: [DRV] Dựng component Gantt timeline tài xế với dải vi phạm
- Frontend: [DRV] Làm bảng phát hiện và dialog xác nhận cảnh báo SCR-061
- Frontend: [DRV] Làm header, bảng phán định theo rule và cổng 公開へ進む
- QA (Manual): [DRV] Viết test case theo từng rule giờ làm SCR-061
- QA (Manual): [DRV] Chạy test luồng kiểm–sửa–xác nhận–công bố với seed R-06

### S9.10: Sự cố bất khả kháng và báo cáo tuân thủ (SCR-063)
- Backend: [DRV] Tạo migration unforeseeable_events và trigger bất biến
- Infra: [DRV] Cấu hình bucket event-evidence và job dọn file mồ côi
- Backend: [DRV] Làm RPC và API đăng ký sự cố bất khả kháng
- Backend: [DRV] Làm RPC duyệt/từ chối và API danh sách, chi tiết sự cố
- Backend: [DRV] Làm báo cáo tuân thủ tháng tách lịch thường và sự cố (BR-DRV-24)
- Backend: [DRV] Làm xuất CSV sự cố và báo cáo vượt kế hoạch (BR-DRV-25)
- Frontend: [DRV] Dựng trang danh sách, chi tiết và duyệt sự cố SCR-063
- Frontend: [DRV] Làm dialog đăng ký sự cố và khối báo cáo tuân thủ
- QA (Manual): [DRV] Viết test case + chạy test SCR-063

### S9.11: Nhập giờ làm thực tế của tài xế (SCR-064 乗務実績入力 — mới)
- BrSE: [DRV] Viết spec màn SCR-064 乗務実績入力
- Backend: [DRV] Làm RPC/API upsert giờ làm thực tế actual_manual
- Frontend: [DRV] Dựng màn nhập giờ làm thực tế theo ngày × tài xế
- QA (Manual): [DRV] Viết test case + chạy test SCR-064

### S9.12: Thẻ cảnh báo giờ lái trên trang chủ (SCR-002 4.8/4.10/4.11)
- Backend: [DRV] Làm get_driver_month_restraint và truy vấn thẻ 4.8/4.10/4.11
- Frontend: [DRV] Làm thẻ 4.11 với bảng tài xế gần chạm hạn 拘束時間
- QA (Manual): [DRV] Viết test case + chạy test thẻ giờ lái SCR-002

### S9.13: Xác nhận pháp lý và làm rõ Q&A giờ lái
- PM: [DRV] Lấy xác nhận pháp lý OPS-LAW-01/Q&A-B06 từ phụ trách vận tải
- BrSE: [DRV] Làm rõ Q&A-B07 労使協定, anchor date, 1 tuyến/ngày, ngày trống

## E10: Làm rõ spec & Q&A khách (BrSE)
Gom câu hỏi mở của LAB-4 gửi khách, theo dõi trả lời và phản ánh vào spec; đồng bộ các chỗ spec lệch DB phát hiện khi break task. Q&A-B06/B07 (giờ lái) nằm ở E9.
Stories: 2 | Roles: Backend, BrSE

### S10.1: Gửi và chốt Q&A khách cho luồng hàng hóa
- BrSE: Soạn bộ Q&A tiếng Nhật cho Q&A-B01…B05, B08…B17
- BrSE: Hỏi khách vòng duyệt SKU master (RFP S3-01) có bắt buộc Phase 1
- BrSE: Phản ánh câu trả lời Q&A vào spec và issue liên quan

### S10.2: Đồng bộ spec với database design
- BrSE: Sửa ghi chú lỗi thời 'chưa có trong DB' ở các spec màn hình
- Backend: Thống nhất enum lệch giữa spec và DB trước khi viết migration

## E11: Kiểm thử tích hợp, UAT & quản lý dự án
Kiểm thử xuyên màn hình theo đường đi của hàng hóa, UAT với fixture RFP R-06, vận hành sprint và phát hành Phase 1.
Stories: 3 | Roles: QA (Manual), Infra, PM, BrSE

### S11.1: Kiểm thử tích hợp luồng hàng hóa end-to-end
- QA (Manual): Viết kịch bản tích hợp xuyên màn hình SCR-022→042→060→061→062→053
- QA (Manual): Chạy kiểm thử tích hợp trên môi trường staging và ghi lỗi

### S11.2: UAT với fixture RFP R-06
- QA (Manual): Nạp fixture R-06 và đối chiếu kết quả mong đợi
- BrSE: Điều phối buổi UAT với khách và tổng hợp phản hồi

### S11.3: Quản lý sprint, báo cáo tiến độ và phát hành Phase 1
- PM: Lập kế hoạch sprint và vận hành board GitHub Project
- PM: Viết báo cáo tiến độ sprint gửi khách (trạng thái, burndown, rủi ro)
- Infra: Chuẩn bị runbook phát hành và khôi phục cho production

