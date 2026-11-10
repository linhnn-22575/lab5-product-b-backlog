# Gap — E9 Ràng buộc giờ lái xe tải 2024

| Spec (file#section) | Chỗ hở/mâu thuẫn | Loại | Xử lý | Task id |
|---|---|---|---|---|
| ADR-006 §5; SCR-061#logic-5 bước 2.2 | Engine cần `driver_duty_records` thực tế (`actual_manual`) nhưng không có màn nhập | hở | sửa thiết kế: màn mới SCR-064 (đã chốt) | BRSE-9.11.1, BE-9.11.2, FE-9.11.3, QA-9.11.4 |
| SCR-016#5-9.2, #9 PATCH vs database-design §3.2, BR-DRV-06/10 (G16-1) | Màn/API thiếu `long_day_threshold_h`, `drive_2week_anchor_date` | hở | sửa thiết kế (đã chốt): thêm vào migration, catalog, form, compare | BE-9.1.1, BE-9.1.2, FE-9.1.5 |
| SCR-061#9 vs SCR-062#logic-5 bước 3.5 (061 gap #10) | Hash tính ở TS khi kiểm, `publish_route` (SQL) tính lại → 2 cài đặt | mâu thuẫn | sửa thiết kế: 1 hàm SQL `compute_compliance_input_hash` dựa trên `get_compliance_input`; POST compliance-checks và publish_route cùng gọi | BE-9.2.2, BE-9.2.3, BE-9.8.3 |
| SCR-060#logic-11 bước 4 vs ADR-006 §3 bước 2 (060 gap #2) | Thuật toán chuỗi lái BR-DRV-11 có nguy cơ cài 2 nơi (SQL chèn nghỉ + TS kiểm) | mâu thuẫn | sửa thiết kế (đã chốt): 1 module TS `drive-chain`; `build_route_segments` (E8 BE-8.2.3) chỉ lưu break được truyền vào | BE-9.6.1, BE-9.6.2 |
| SCR-062#logic-5 bước 3.8, database-design `driver_duty_records` (062 gap #7) | Duty record `route_plan` của bản `superseded` vẫn còn, spec không nói lọc | hở | sửa thiết kế: mọi chỗ đọc lọc `route_versions.status='published'` và tuyến chưa hủy (gồm thẻ SCR-002) | BE-9.2.2, BE-9.8.3, BE-9.12.1 |
| SCR-063#logic-6 item 7 (`compliance_report_summary` là hàm SQL) vs ADR-006 phương án A | Báo cáo "chạy engine" nhưng engine là TS, SQL không gọi được | mâu thuẫn | sửa thiết kế: báo cáo là service TS sau route handler, giữ tên `compliance_report_summary` | BE-9.10.5 |
| SCR-063#logic-6 (6-2) vs `driver_duty_records` (063 gap #2) | BR-DRV-11 trên thực tế cần segment, duty record chỉ có `drive_h/break_h` | hở | giả định: dùng segment kế hoạch của tuyến đã chạy; ghi trong spec SCR-064/Q&A | BE-9.10.5, BRSE-9.13.2 |
| ADR-006 §3 bước 1/4 vs SCR-061#logic-5 bước 2.2 (061 gap #2/#3) | ADR: "14 ngày trước", nghỉ giữa ca chỉ so thực tế; spec: FY → D+14, thực tế hoặc kế hoạch công bố | lỗi thời | sửa thiết kế: theo spec màn, cập nhật ADR khi viết SCR-064 | BE-9.2.2, BRSE-9.11.1 |
| BR §7 "Định nghĩa dùng chung", BR-DRV-24 (Q&A-B06) | Công thức tăng ca và phạm vi loại sự cố INFERRED | hở | tạo issue làm rõ (PM); công thức tách 1 hàm để đổi | PM-9.13.1, BE-9.7.1 |
| SCR-061#logic-9 BR-DRV-14, SCR-016 G16-7 (Q&A-B07) | Điều kiện phụ 告示 của 労使協定 (số tháng được vượt) chưa thiết kế | hở | giả định: chỉ thay hạn năm/tháng; issue BrSE | BE-9.7.4, BRSE-9.13.2 |
| SCR-061#logic-5 bước 2.2 (061 gap #7), SCR-060 gap #1 | Ngày quá khứ trống = 0h có thể làm lọt vi phạm; 1 tài xế 1 tuyến/ngày INFERRED | hở | tạo issue làm rõ; SCR-064 đánh dấu ngày chưa nhập | BRSE-9.13.2, FE-9.11.3 |
| SCR-002 item 4.11-2/4.11-4 (gap #7, #8, #10) | Phạm vi cộng tháng của thẻ lệch ADR-006; `home_alert_ratio` 0.9 không có chỗ lưu | mâu thuẫn | sửa thiết kế: dùng chung `select_driver_duty_days`; giả định 0.9 là hằng số app | BE-9.12.1 |

## Phần spec chưa thành task + vì sao
- Thẻ năm 3.300h / tăng ca 960h trên SCR-002 (gap #9): spec không có, chờ khách — không tạo scope mới.
- Kiểm điều kiện phụ 労使協定 trong engine: chờ Q&A-B07.
- Segment thực tế từ app tài xế F06 (`actual_app`): ngoài phạm vi; engine đã đọc được `source='actual_app'`.
- `supersedes_event_id` cho sự cố sai (063 gap #3), sự cố khi chỉ có 1 `transport_manager` (063 gap #5): để mở, BrSE hỏi chung ở Q&A — chưa đủ chắc để làm task.
- Phần `publish_route` ngoài cổng tuân thủ (supersede, outbox, audit) thuộc E8 `apply_route_publish` (BE-8.5.1); migration lõi F07 thuộc E8 BE-8.1.1.
