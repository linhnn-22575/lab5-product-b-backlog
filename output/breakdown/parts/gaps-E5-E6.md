# Gap — E5 (F03 Tồn kho & lô), E6 (F04 Đơn hàng & phân bổ)

| Spec (file#section) | Chỗ hở/mâu thuẫn | Loại | Xử lý | Task id |
|---|---|---|---|---|
| SCR-030#6, SCR-037#6 vs database-design.md | Không có bảng lưu `consumption_warning_days` và `lot_disposal_dual_approval_qty` | hở | sửa thiết kế: thêm bảng `app_parameters` (audit, chỉ admin sửa) | BE-5.1.1, BE-5.3.1 |
| SCR-030#5-4.8.2 vs SCR-031#5-3.9 | Điều kiện badge 要移動 lệch (chỉ `quarantine` vs `quarantine`/`on_hold`) | mâu thuẫn | sửa thiết kế: 1 hàm dùng chung, gồm `on_hold` | BE-5.1.1 |
| SCR-030#7 (FR-INV-06) | Giả định 1 kho, trong khi Product B là chuỗi kho; DB không có `warehouse_id` | hở | tạo issue làm rõ (rủi ro thiết kế lớn nếu đa kho) | BRSE-5.3.9 |
| SCR-031#9 #2 vs database-design `lot_status_events.event_type` / `movement_type` | Enum 10 loại sự kiện không khớp DB (thiếu allocate/unallocate/dispose, sự kiện tạo lô) | mâu thuẫn | sửa thiết kế: chốt 1 enum dùng chung SCR-022/031/037 trong migration | BE-5.3.1, BE-5.2.1 |
| SCR-037#5 item 6.4 vs #9 #4 | `evidence_no` bị nối `[REF:x]` vào `reason`, không tra cứu được | hở | giả định: thêm cột `evidence_note` (BrSE xác nhận) | BE-5.3.1, BE-5.3.3 |
| SCR-037#5 item 4.6 | Lô quarantine có `qty_allocated > 0` từ prototype khóa mọi nút | hở | sửa thiết kế: bước dọn dữ liệu trong migration | BE-5.3.1 |
| SCR-042#5 item 8-2, 8.7 vs business-rules#sm-lot (G-1) | Lô `on_hold` không vào tập ứng viên/badge | mâu thuẫn | sửa thiết kế (đã chốt): lớp 3 gồm `on_hold`, badge 保留 | BE-6.1.2, BE-6.1.4, FE-6.4.5 |
| SCR-042#5 item 5.5-2 vs 8.11-4 (G-2) | GET tính lại `line_status` = đọc có tác dụng phụ | mâu thuẫn | sửa thiết kế (đã chốt): tính trong RPC ghi + trigger khi hợp đồng đổi | BE-6.4.1 |
| SCR-042#5 item 13.9-4, #9 #5 (G-4) | Upload Storage nằm ngoài transaction, không rollback được | lỗi | sửa thiết kế (đã chốt): upload đường tạm trước, RPC ghi ref, dọn file mồ côi | BE-6.4.3, INFRA-6.6.2 |
| SCR-044#logic-8-6 vs BR-DATE-02 | Job 00:05 chỉ expire theo `requested_date`, thiếu `PREVIOUS_CHANGED` | hở | sửa thiết kế: job so `last_delivered_expiry()` với snapshot | BE-6.6.4 |
| business-rules#BR-DELWIN-01 (SCR-042 G-11, Q&A-B02) | Công thức cửa sổ giao dùng ngày SX hay ngày nhập chưa chốt — chặn lớp 4 | hở | tạo issue làm rõ (ưu tiên), tạm theo ngày SX | BRSE-6.1.7, BE-6.1.3 |
| SCR-040#5 item 13.4-3 | Xung đột hủy đơn trả "M_402 (hoặc M_22)" chưa chốt mã | hở | giả định: 409 `NOT_CANCELLABLE` → M_402 | BE-6.2.2 |

## Phần spec chưa thành task + vì sao
- Màn di chuyển vật lý lô sang khu -Q (SCR-031 G31-4, FR-INV-03): chưa có spec màn → lô treo 要移動; cần PM quyết định thêm vào phase sau.
- Màn chi tiết deviation F08 (SCR-031 G31-5): chưa spec, không link.
- Hủy một phần lô (SCR-037 #2): cần tách lô, chưa thiết kế; phase 1 hủy toàn bộ.
- Nhập đơn CSV ERP FN-0402 (SCR-041 #7): ngoài phạm vi, epic riêng phase sau.
- Thông báo cho người gửi khi có kết quả duyệt 日付逆転 (SCR-044 #3): chưa thiết kế, đưa vào câu hỏi BRSE-6.1.7.
- Thẻ 「承認待ち」 ở SCR-002 (SCR-044 #5): thuộc màn dashboard, không tạo task ở E6.
- Xuất CSV lịch sử giao (SCR-043 #5): không có trong spec, giới hạn 500 dòng chấp nhận cho phase 1.
- Các ghi chú spec lỗi thời (SCR-037 #7, SCR-040 #4, SCR-041 #5, SCR-043 #3): chỉ cập nhật tài liệu, không cần task.
