# Backend Tasks: Product B — Yuki Cold Logistics (LAB-5)

**Date**: 2026-11-10 | **Total**: TBD

---

## E6: F04 Đơn hàng & phân bổ

### S6.6: Duyệt ngoại lệ 日付逆転 (SCR-044)

#### BE-6.6.1: Tạo migration date_reversal_exception_requests, chuyển dữ liệu cũ, RBAC
Bảng date_reversal_exception_requests (requested_at, decided_at, expire_reason, previous_delivery_history_id, snapshot hạn trước, allocation_id, is_legacy; CHECK decided_by <> requested_by; UNIQUE partial pending), chuyển date_reversal_overrides → legacy approved; vai trò sales_manager + date_reversal:approve/request + RLS 4 vai trò.

- [ ] State machine pending → approved | rejected | expired bằng CHECK
- [ ] Chuyển dữ liệu overrides: is_legacy, approved, decided_by null, rồi bỏ bảng cũ
- [ ] role-permissions.ts thêm sales_manager và 2 permission
- [ ] RLS SELECT cho sales_manager, sales_planner, quality, auditor

**AC:**
- Không tạo được 2 yêu cầu pending cho cùng dòng đơn + lô
- Dữ liệu date_reversal_overrides cũ xuất hiện dưới dạng yêu cầu legacy approved

#### BE-6.6.3: Viết RPC approve/reject_date_reversal_request có kiểm lại và tự phân bổ
approve_date_reversal_request khóa yêu cầu → orders → order_lines → lots, kiểm lại lớp 1–4 qua evaluate_lot_for_line + SL, 6 nhánh expire (commit expired, trả result 'expired'), nếu đạt thì phân bổ như allocate_lot, exception_events, audit; reject_date_reversal_request với nhận xét 10–500.

- [ ] expire_reason: RULE_FAILED:<code>, PREVIOUS_CHANGED, QTY_INSUFFICIENT, ORDER_CANCELLED, REQUESTED_DATE_PASSED, ORDER_NOT_ALLOCATABLE
- [ ] Người duyệt ≠ người gửi (M_448), đã xử lý → M_450
- [ ] Tạo allocations với exception_request_id + allocation_evidence, movement allocate
- [ ] reject: nhận xét bắt buộc 10–500 (M_06)

**AC:**
- Duyệt khi lô vừa bị cách ly trả HTTP 200 result 'expired' với RULE_FAILED:QUARANTINED, không phân bổ
- 2 manager duyệt cùng lúc: chỉ 1 thành công, người kia nhận M_450

#### BE-6.6.4: Viết job expire_date_reversal_requests 00:05 JST gồm PREVIOUS_CHANGED
pg_cron expire_date_reversal_requests() 00:05 JST, lô 500: hết hạn yêu cầu pending khi requested_date đã qua (REQUESTED_DATE_PASSED) hoặc last_delivered_expiry() khác snapshot lúc gửi (PREVIOUS_CHANGED, sửa thiết kế theo BR-DATE-02).

- [ ] Lịch pg_cron theo JST, xử lý theo lô 500, idempotent khi chạy lại
- [ ] So last_delivered_expiry() với snapshot previous_delivery_history_id
- [ ] Ghi audit_log mỗi yêu cầu expired

**AC:**
- Có lần giao mới cho cùng khách+SKU sau khi gửi thì job chuyển yêu cầu sang expired PREVIOUS_CHANGED
- Chạy job 2 lần liên tiếp không tạo thay đổi thừa

#### BE-6.6.5: Xây API danh sách, chi tiết + kiểm lại, bằng chứng, duyệt/từ chối SCR-044
GET list (zod, counts theo 5 tab, sort, paging 50), GET detail + recheck (evaluate_lot_for_line, SL, currentPreviousExpiry) + history từ audit_log, GET evidence (302 signed URL 5 phút, audit evidence_viewed), POST approve/reject map 409 SELF_DECISION/ALREADY_DECIDED.

- [ ] Tab 申請中 bỏ qua lọc ngày, mặc định −30 ngày
- [ ] recheck chỉ đọc, dùng đúng pipeline như RPC duyệt
- [ ] Map 403/409 sang M_xx

**AC:**
- Kết quả recheck trùng với kết quả RPC duyệt khi dữ liệu không đổi
- Mỗi lần xem bằng chứng ghi 1 dòng audit evidence_viewed


