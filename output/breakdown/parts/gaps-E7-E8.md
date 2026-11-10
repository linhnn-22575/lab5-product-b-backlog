# Gap fragment — E7 (F05 Kiểm trước xuất), E8 (F07 Lập tuyến & công bố, phần không thuộc giờ lái)

| Spec (file#section) | Chỗ hở/mâu thuẫn | Loại | Xử lý | Task id |
|---|---|---|---|---|
| SCR-053#logic-10-4 vs SCR-060#logic-6-5 | SCR-053 lấy giờ xuất phát = `planned_arrival` depot đầu, nhưng SCR-060 định nghĩa đó là 始業; 出庫 = `planned_arrival + service_min` | mâu thuẫn | sửa thiết kế (hàm dùng chung `route_departure_time`) | BE-7.2.1 |
| SCR-053#9 bước 4 vs SCR-062#logic-12 | Đổi sau công bố đưa `routes.status='created'`, `current_version` = nháp → kho không xuất được dù tài xế chạy bản cũ | mâu thuẫn | sửa thiết kế (quyết định 1): routes giữ `published`, RPC kiểm bản `published` hiện hành | BE-7.1.3, BE-8.5.2 |
| SCR-060#4 (published → chỉ đọc M_607) vs quyết định 1 | Tuyến giữ `published` khi có nháp → điều kiện sửa ở SCR-060 phải dựa vào `route_versions.status` của bản đang sửa, không dựa `routes.status` | mâu thuẫn (phát sinh từ quyết định 1) | sửa thiết kế: RPC ghi của SCR-060 kiểm status version draft/created/checked | BE-8.2.2, BE-8.2.4, FE-8.5.2 |
| SCR-062#logic-7 (7-3) | Hủy tuyến published: "mọi đơn routed → allocated", không nói đơn đã `shipped` | hở | sửa thiết kế: chặn hủy khi có đơn shipped (đã chốt trong brief) + Q&A xác nhận | BE-8.5.3, BRSE-8.5.1 |
| SCR-060#logic-11 bước 4 vs ADR-006 §3 | Chèn nghỉ đặt trong SQL `build_route_segments`, ADR đặt trong engine TS → 2 bản cài chuỗi lái | mâu thuẫn | sửa thiết kế (quyết định 3): `build_route_segments` chỉ ghi nghỉ do module TS của E9 trả về | BE-8.2.3 |
| database-design §ERD `route_segments.segment_type` | Có cả `break` và `rest`; spec chỉ dùng `break` | mâu thuẫn | sửa thiết kế DB: bỏ `rest` khỏi `segment_type` | BE-8.1.1 |
| SCR-053#logic-11-6 | Định dạng mã vạch `{sku_code}|{lot_code}` INFERRED | hở | tạo issue làm rõ; parser FE tách riêng để thay | BRSE-7.3.1, FE-7.3.3 |
| SCR-053#3 (h), #9 bước 6h | Kiểm lại đảo ngày lúc xuất INFERRED; ngoại lệ `approved` luôn qua dù mốc giao đổi sau duyệt | hở | giả định theo spec + tạo issue làm rõ | BE-7.1.4, BRSE-7.3.1 |
| SCR-060#logic-6-4 | 1 tài xế 1 tuyến/ngày INFERRED — ảnh hưởng engine gộp ca E9 | hở | giả định (unique partial index) + issue làm rõ ưu tiên cao | BE-8.1.1, BRSE-8.5.1 |
| SCR-060#logic-3, #13; SCR-062#logic-4-4 | Timeout 10s, cách hiểu "> 24h", refresh đưa checked → created buộc kiểm lại khi công bố hôm sau | hở | giả định + issue làm rõ; ghi rủi ro vận hành | BE-8.3.1, BE-8.3.2, BRSE-8.5.1 |
| SCR-062#logic-11 | Công thức KPI + ngưỡng 15 phút INFERRED | hở | giả định, ngưỡng là tham số + issue làm rõ | BE-8.5.4, BRSE-8.5.1 |
| SCR-062#3 | `in_progress/completed` do F06 chuyển (ngoài phạm vi) → tuyến kẹt ở `published` | hở | để mở; PM quyết định nút chuyển tay tạm | BRSE-8.5.1 |

## Phần spec chưa thành task + vì sao

- SCR-060 sub-task 8 (BR-DRV-21 tự chèn nghỉ) và 20 (QA BR-DRV-21) → E9 (dính giờ lái 2024, issue riêng).
- SCR-062 sub-task 1 phần cổng (6 kiểm tra M_642/M_631/M_632/M_633/M_634/M_622, hash, `driver_duty_records` route_plan) và 14 (QA cổng) → E9; E8 chỉ giữ `apply_route_publish` (BE-8.5.1).
- SCR-062 gap #7 (lọc duty records theo `route_versions.status='published'`) → E9, nơi đọc/ghi `driver_duty_records`.
- SCR-053 gap #8 (màu `Status_Badge` 053 vàng vs 060 xanh) → thuộc component common, không tạo task trong E7/E8.
- SCR-053 gap #9 (link sang màn deviation F08) → giai đoạn sau, chỉ ghi phụ thuộc.
- SCR-062 gap #8 (câu "database-design chưa liệt kê" lỗi thời) → sửa chữ trong spec, không đáng thành task.
- SCR-060 gap #8 (rule version theo hôm nay thay vì service_date) → rủi ro thuộc engine E9.
- SCR-060 gap #4, #6 và SCR-062 gap #6 (mặc định ngày mai, service 20 phút, lịch retry) → giữ giả định, đã nhúng vào task (BE-8.1.2, INFRA-8.3.2), không tạo task riêng.
