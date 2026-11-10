# Gap — E1–E4

| Spec (file#section) | Chỗ hở/mâu thuẫn | Loại | Xử lý | Task id |
|---|---|---|---|---|
| SCR-022 §9 RPC bước 6 vs database-design ERD `deviations.deviation_type` | Spec ghi `temperature`/`traceability`, DB là `temp_out_of_range`/`trace_missing`/`zone_mismatch` (G22-1) | mâu thuẫn | sửa thiết kế: chốt enum DB, cập nhật spec 022/031 | BE-1.1.3, BE-4.2.2 |
| SCR-022 §9 RPC bước 6 vs ERD `lot_status_events.event_type` | Lô mới nhập không có event_type hợp lệ (G22-2) | mâu thuẫn | sửa thiết kế: thêm `event_type = 'create'` | BE-1.1.2, BE-4.2.2 |
| SCR-022 §9 RPC bước 2 vs database-design §3.3 `idempotency_keys` | Không có cột tham chiếu đối tượng → không phát hiện "key dùng cho phiếu khác" (G22-3) | hở | sửa thiết kế: thêm `ref_id`, `request_hash`; dùng chung cho SCR-031 | BE-1.1.3 |
| SCR-001 §9 vs database-design §3.3 `app_sessions` | Cột spec (`session_id`, `is_shared_device`) lệch DB (`id`, `device_id`, `expires_at`); spec ghi "chưa có" đã lỗi thời (#4, G18-1, #15, #22, #29) | lỗi thời | sửa spec theo DB design; chốt cột trong task | BE-2.1.4 |
| SCR-001 item 2-6 vs SCR-002 item 4-16 | Callback không cập nhật `mfa_verified_at`/`last_sign_in_at` mà thẻ 4.16 cần (#5) | hở | sửa thiết kế: thêm bước vào callback | BE-2.1.2 |
| SCR-001 item 7-2 | M_104 `mfa_failed` không có nhánh nào sinh ra (#3) | mâu thuẫn | tạo issue làm rõ (nguồn IdP `access_denied`?) | BRSE-2.3.6 |
| SCR-001 §3, item 11-2 | Idle 15 phút, cảnh báo 60s, cookie thiết bị dùng chung, claim `amr` đều INFERRED (#1, #2) | hở | giả định: tham số cấu hình; tạo issue làm rõ | BE-2.1.4, BRSE-2.3.6 |
| SCR-018 spec#5-11.5 | Thu hồi phiên bằng xóa `auth.refresh_tokens` đụng schema nội bộ Supabase (G18-2) | hở | spike trong task; fallback Admin API `signOut` | BE-2.3.1 |
| SCR-010 item 2 vs SCR-011 item 1-2 | Điều hướng `/master/*`: tab chung vs menu trái (#17) | mâu thuẫn | sửa thiết kế: chốt 1 cách cho cả nhóm | FE-3.1.3 |
| SCR-011 §9 vs common-format Format_Code | Regex mã khách cho chữ thường, SKU chỉ A–Z (#23) | mâu thuẫn | sửa thiết kế: A–Z, tự upper | BE-3.2.1 |
| SCR-011 item 18-14 | Side-effect `order_lines` + job 00:05 INFERRED, không có trong ADR; dòng allocated một phần chưa rõ (#20, #21) | hở | giả định: bỏ qua dòng đã allocated; tạo issue làm rõ; ghi vào ADR/infra | BE-3.3.4, BRSE-3.4.7 |
| SCR-015 §9 trigger | Cơ chế role service bỏ qua trigger ≥ ngày mai cho seed không định nghĩa (#30) — rủi ro bảo mật | hở | sửa thiết kế: chỉ role migration (session var + kiểm role), không lộ cho app | BE-1.4.1, BE-3.4.1 |

## Phần spec chưa thành task + vì sao
- SCR-002 thẻ 4.8 / 4.10 / 4.11 và `get_driver_month_restraint` — giờ lái 2024, thuộc E9 (E2 chỉ chừa slot trong ma trận thẻ và lưới FE).
- SCR-002 gap #6 (deviation:read của admin/warehouse_lead vs ma trận thẻ), #9 (thẻ năm 3.300h), #11 (tên query param SCR-040) — thuộc E9/E5 hoặc chỉ sửa tài liệu; để mở cho epic liên quan.
- SCR-010 #14 / G-25 vòng duyệt master (SCR-017) — hoãn theo Q&A-B11, đã có ở E10 (BRSE-10.1.2).
- G-04 (日付逆転 override), G-05, G-11, G-12, G-13 — thuộc epic phân bổ/xuất hàng, không nằm trong E1 dù là "sửa prototype".
- `confirm_shipment()` đổi sang `effective_temp_policy` — chỉ thêm cột `policy_version_id` ở BE-1.4.2; viết lại RPC thuộc epic xuất hàng.
- SCR-022 G22-9 kiểm sức chứa vị trí (FR-INV-01) — out-of-scope phase này.
- G18-4 / G22-8 vai trò `driver` — giả định không phải vai trò app (thực thể `drivers`); không task.
- SCR-011 #25 màu badge 適用予定 và SCR-015 #32 link usage count — sửa nhỏ common-format / giai đoạn sau, gộp trong FE task.
- Nhiều spec ghi "chưa có trong database-design" đã lỗi thời — rà đồng bộ thuộc E10.
