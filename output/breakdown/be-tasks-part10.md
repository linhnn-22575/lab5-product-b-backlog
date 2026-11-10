# Backend Tasks: Product B — Yuki Cold Logistics (LAB-5)

**Date**: 2026-11-10 | **Total**: TBD

---

## E9: ★ Ràng buộc giờ lái xe tải 2024 (改善基準告示)

### S9.7: Kiểm giới hạn tháng, năm, tăng ca và gia hạn 労使協定

#### BE-9.7.1: [DRV] Cài rule BR-DRV-01 tăng ca tối đa 960h/năm tài chính
Giới hạn overtime_year_max_h 960h, mức vi phạm; tăng ca ngày = max(0, 拘束 − nghỉ giữa ca − standard_work_day_h 8h) (INFERRED Q&A-B06), Σ từ đầu năm tài chính (fiscal_year_start_month 4) tới hết D gồm tuyến này. Window = thời điểm lũy kế vượt hạn theo 'đồng hồ làm việc' (thời gian trôi trừ break, tăng ca bắt đầu khi > 8h) → 終業; đã vượt từ trước → cả ca.

- [ ] Công thức tách thành 1 hàm để đổi khi Q&A-B06 chốt
- [ ] Đọc tháng bắt đầu năm tài chính từ rule version
- [ ] Unit test LY2 + ví dụ 955h

**AC:**
- LY2: 512.0h + 5.5h = 517.5h → OK
- Lũy kế 955.0h → window 20:30–21:00, 960.5h → vi phạm; lũy kế cuối ca đúng 960.0h → OK
- Lũy kế trước ca đã 961h → window = cả ca 始業–終業

#### BE-9.7.2: [DRV] Cài rule BR-DRV-02 thời gian ràng buộc 3.300h/năm
Giới hạn restraint_year_max_h 3.300h (hoặc ext khi BR-DRV-14 bật), mức vi phạm; Σ (終業 − 始業) mọi ca trong năm tài chính + tuyến này. Window = [始業 + (hạn − lũy kế trước tuyến), 終業].

- [ ] Lấy hạn qua hàm resolve của BR-DRV-14
- [ ] Lũy kế trước tuyến lấy từ BE-9.2.2
- [ ] Unit test LY2 + biên

**AC:**
- LY2: 1,712.0 + 15.5 = 1,727.5h → OK
- Lũy kế 3,290.0h, ca 05:30–21:00 → vi phạm window 15:30–21:00; lũy kế 3,284.5h → tổng đúng 3,300.0h → OK

#### BE-9.7.3: [DRV] Cài rule BR-DRV-03 thời gian ràng buộc 284h/tháng
Giới hạn restraint_month_max_h 284h (hoặc ext khi BR-DRV-14 bật), mức vi phạm; Σ 拘束 trong tháng dương lịch JST chứa D + tuyến này. Window = [始業 + (hạn − lũy kế trước tuyến), 終業]; định nghĩa tháng dùng chung với get_driver_month_restraint (thẻ 4.11).

- [ ] Tháng theo duty_date JST
- [ ] Dùng cùng hàm chọn dữ liệu với thẻ SCR-002 4.11
- [ ] Unit test LY2 + biên

**AC:**
- LY2: 62.5 + 15.5 = 78.0h → OK
- Lũy kế 270.0h → vi phạm window 19:30–21:00 (285.5h); lũy kế 268.5h → đúng 284.0h → OK
- D = ngày 1 của tháng không cộng giờ tháng trước

#### BE-9.7.4: [DRV] Cài rule BR-DRV-14 công tắc gia hạn 労使協定 cho hạn năm/tháng
Hàm resolveRestraintLimits(ruleVersion): ext_restraint_year_max_h / ext_restraint_month_max_h khác null → thay hạn của BR-DRV-02/03 (3.400h/310h); null (bản 2024-04) → 3.300h/284h. Không kiểm điều kiện phụ của 告示 (chờ Q&A-B07).

- [ ] Hàm thuần, dùng bởi BE-9.7.2, BE-9.7.3 và thẻ 4.11
- [ ] Finding ghi rõ hạn đang áp (thường/gia hạn) trong detail
- [ ] Unit test 2 trạng thái

**AC:**
- ext null: tháng 285.0h → vi phạm hạn 284h
- ext 310: tháng 285.0h → OK; 310.5h → vi phạm hạn 310h; năm 3,350h → OK với ext 3400

### S9.8: Lưu kết quả kiểm bất biến, xác nhận cảnh báo và cổng công bố

#### BE-9.8.1: [DRV] Tạo bảng kết quả kiểm, RPC save_compliance_check và trigger bất biến
Migration compliance_check_results (input_hash, route_version_id, driver_rule_version_id, violation_count, warning_count, checked_by/at) + compliance_violations (+detail jsonb); RPC save_compliance_check(p_route_version_id, p_rule_version_id, p_input_hash, p_findings) INSERT trong 1 transaction và chuyển routes created↔checked; trigger chặn UPDATE/DELETE (BR-DRV-23).

- [ ] Khóa routes FOR UPDATE trong RPC
- [ ] 0 vi phạm → checked; có vi phạm khi đang checked → created
- [ ] Trigger bất biến trên compliance_check_results, compliance_violations
- [ ] Ghi audit_log

**AC:**
- UPDATE/DELETE trực tiếp compliance_check_results bị chặn kể cả bằng service role qua SQL thường
- Chạy kiểm 2 lần → 2 bản ghi, bản cũ giữ nguyên
- Tuyến checked chạy lại có 1 vi phạm → routes.status = created

#### BE-9.8.2: [DRV] Tạo bảng và RPC/API xác nhận cảnh báo giờ làm
Migration compliance_warning_acks (check_id, violation_id, category 6 giá trị, note, acked_by/at, UNIQUE) + RPC ack_compliance_warning + POST /api/compliance-violations/{id}/acks; đây là 'phân loại + bằng chứng' cho slot vượt kế hoạch (BR-DRV-20/25).

- [ ] Chặn severity = violation (vi phạm không xác nhận cho qua)
- [ ] Chặn lần kiểm không phải mới nhất và tuyến đã công bố
- [ ] Bắt buộc 区分 (M_639) + 根拠メモ 10–500 (M_06); bất biến, M_638
- [ ] auditor 403

**AC:**
- Ack dòng violation → 422; ack cảnh báo lần kiểm cũ → 422
- Ack lần 2 cùng violation_id → 409 (UNIQUE), bản ghi đầu không đổi
- Memo 9 ký tự → M_06; 10 ký tự → OK

#### BE-9.8.3: [DRV] Làm RPC publish_route: cổng tuân thủ, gắn rule version, ghi duty record
RPC publish_route(p_route_id, p_check_id): khóa, kiểm theo thứ tự checked (M_642) → lần kiểm mới nhất & 0 vi phạm (M_631) → cảnh báo đã xác nhận (M_632) → rule version còn hiệu lực effective_driver_rule_version(app_today()) (M_633) → compute_compliance_input_hash khớp (M_634) → map > 24h (M_622); rồi gọi apply_route_publish (E8 BE-8.5.1), gắn driver_rule_version_id và INSERT driver_duty_records source=route_plan.

- [ ] Dừng ở lỗi đầu tiên, trả mã M_xxx cho FE làm mới checklist
- [ ] Hash tính bằng hàm dùng chung BE-9.2.3, không cài lại
- [ ] duty record route_plan: shift_start/end, drive_h, break_h từ segment
- [ ] Bản mới công bố: reader lọc theo route_versions.status='published' (062 gap #7)

**AC:**
- Có 1 cảnh báo chưa xác nhận → M_632, tuyến không đổi trạng thái
- Ghi actual_manual mới cho D−1 sau khi kiểm → M_634; rule version mới có hiệu lực giữa kiểm và công bố → M_633
- Công bố thành công → route_versions.driver_rule_version_id = bản hiệu lực, có duty record route_plan

#### BE-9.8.4: [DRV] Làm API POST compliance-checks chạy engine và lưu kết quả
POST /api/routes/{id}/compliance-checks: guard M_637 (thiếu tài xế), M_608 (thiếu điểm giao), M_635 (không rule version), M_607 (đã công bố); gọi get_compliance_input + compute_compliance_input_hash, chạy engine TS, gọi save_compliance_check.

- [ ] Chỉ dispatcher/transport_manager, tuyến created/checked
- [ ] Trả M_630 + check_id mới, danh sách ngày M_636
- [ ] Integration test với fixture LY2

**AC:**
- Tuyến LY2 → 2 vi phạm (05, 11) + cảnh báo (04, 07), tuyến giữ created
- Tuyến chưa gán tài xế → 422 M_637, không tạo bản ghi

### S9.9: Màn timeline tài xế và vi phạm giờ làm (SCR-061)

#### BE-9.9.1: [DRV] Làm RPC get_route_timeline và API GET timeline tuyến
RPC get_route_timeline + GET /api/routes/{id}/timeline: segments D và duty D−1/D+1, danh sách lần kiểm (gồm cũ) + hash, findings + acks, lũy kế theo rule, overlay unforeseeable_events approved, cờ stale (hash hiện tại ≠ hash lần kiểm → M_634; rule version đổi → M_633).

- [ ] stale tính bằng compute_compliance_input_hash (BE-9.2.3)
- [ ] auditor xem được lần kiểm cũ, chỉ đọc
- [ ] Zod response, no-store

**AC:**
- Sau khi ghi thực tế D−1 mới, response trả stale = true với mã M_634
- Chọn check_id cũ trả đúng findings của lần đó, không lẫn lần mới

### S9.10: Sự cố bất khả kháng và báo cáo tuân thủ (SCR-063)

#### BE-9.10.1: [DRV] Tạo migration unforeseeable_events và trigger bất biến
Migration unforeseeable_events (+evidence_file_path, evidence_sha256, evidence_ref_no, decision_comment, decided_at) + CHECK approved_by <> reported_by, end_at > start_at, có file hoặc số tham chiếu; trigger chỉ cho 1 lần chuyển submitted → approved|rejected (M_667).

- [ ] Giữ 1 cột evidence_ref_no (bỏ evidence_ref trùng nghĩa)
- [ ] View unforeseeable_events_list_view
- [ ] RLS SELECT theo vai trò

**AC:**
- UPDATE bản approved → lỗi M_667
- INSERT không file và không số tham chiếu → vi phạm CHECK

#### BE-9.10.3: [DRV] Làm RPC và API đăng ký sự cố bất khả kháng
RPC create_unforeseeable_event (khóa drivers FOR UPDATE, kiểm chồng ca tài xế M_662 và chồng sự cố submitted/approved M_671, outbox, audit) + POST multipart (upload trước ngoài transaction, SHA-256 server, zod, Idempotency-Key).

- [ ] Ca tài xế lấy từ thực tế hoặc route_plan bản published (lọc status='published')
- [ ] Validate: bước 5 phút, không tương lai M_668, end > start M_661, ≤ 24h M_05, file/ref M_660, file M_670
- [ ] Tuyến published/in_progress/completed trong 30 ngày

**AC:**
- Sự cố không chồng ca tài xế → M_662; chồng sự cố approved khác của cùng tài xế → M_671
- File 10MB + 1 byte → M_670; gửi lại cùng Idempotency-Key → không tạo bản thứ 2

#### BE-9.10.4: [DRV] Làm RPC duyệt/từ chối và API danh sách, chi tiết sự cố
RPC decide_unforeseeable_event + POST approve/reject (FOR UPDATE, người duyệt ≠ người ghi M_665, M_22, nhận xét từ chối 10–500); GET list (lọc chồng khoảng ngày, M_13, > 366 ngày M_05) và GET detail (signed URL 5 phút, kết quả kiểm liên quan của bản đã công bố).

- [ ] Duyệt không chạy lại/sửa kết quả kiểm (BR-DRV-23)
- [ ] Chỉ transport_manager duyệt
- [ ] Outbox thông báo, không SMS

**AC:**
- Người ghi tự duyệt → M_665
- Duyệt xong, compliance_check_results liên quan không đổi (so sánh trước/sau)

#### BE-9.10.5: [DRV] Làm báo cáo tuân thủ tháng tách lịch thường và sự cố (BR-DRV-24)
Service compliance_report_summary(p_month) + GET /api/compliance-reports/summary: chạy engine TS trên giờ thực tế từng tài xế-ngày, cắt khoảng sự cố approved chỉ cho BR-DRV-04/05, 09, 11 và chuyển vi phạm 3 nhóm này sang báo cáo sự cố; BR-DRV-01/02/03, 06, 07/08, 10 tính đủ; submitted/rejected không cắt.

- [ ] Dùng lại engine + select_driver_duty_days, không cài rule lần 2
- [ ] BR-DRV-11 trên thực tế dùng segment kế hoạch tuyến đã chạy (giả định, 063 gap #2)
- [ ] Không ghi vào compliance_check_results

**AC:**
- Vi phạm BR-DRV-05 nằm trong khoảng sự cố approved → ở báo cáo sự cố, không ở lịch thường
- Vi phạm BR-DRV-08 trong khoảng sự cố approved vẫn ở lịch thường; sự cố rejected không cắt gì

#### BE-9.10.6: [DRV] Làm xuất CSV sự cố và báo cáo vượt kế hoạch (BR-DRV-25)
GET /api/compliance-reports/events.csv (UTF-8 BOM, sự cố approved + vi phạm trong khoảng) và view over_plan_acks_view + GET /api/compliance-reports/over-plan liệt kê cảnh báo đã xác nhận theo 区分 cho transport_manager.

- [ ] CSV dùng dữ liệu của BE-9.10.5
- [ ] Over-plan lọc theo tháng, tài xế, 区分
- [ ] Chỉ transport_manager/auditor

**AC:**
- CSV mở bằng Excel không lỗi font tiếng Nhật (BOM)
- Cảnh báo 04 đã xác nhận 区分 荷待ち xuất hiện trong over-plan với memo và người xác nhận

### S9.11: Nhập giờ làm thực tế của tài xế (SCR-064 乗務実績入力 — mới)

#### BE-9.11.2: [DRV] Làm RPC/API upsert giờ làm thực tế actual_manual
RPC upsert_actual_duty_records + PUT /api/driver-duty-records (theo ngày) ghi driver_duty_records source=actual_manual: validate ca không chồng nhau trong cùng tài xế, shift_end > shift_start, drive_h + break_h ≤ độ dài ca, không ngày tương lai; audit giá trị cũ; GET danh sách theo ngày × tài xế.

- [ ] UNIQUE (driver_id, duty_date, source) cho actual_manual
- [ ] Chồng với ca ngày kề (D−1 kết thúc sau 始業 D) → lỗi
- [ ] Chỉ dispatcher/transport_manager ghi

**AC:**
- Ca D 05:00 trong khi ca D−1 kết thúc 06:00 → lỗi chồng ca
- Lái 9h + nghỉ 2h trong ca 10h → lỗi; ghi hợp lệ làm tuyến đã kiểm liên quan thành stale (M_634)

