# Backend Tasks: Product B — Yuki Cold Logistics (LAB-5)

**Date**: 2026-11-10 | **Total**: TBD

---

## E9: ★ Ràng buộc giờ lái xe tải 2024 (改善基準告示)

### S9.1: Quản lý phiên bản quy tắc giờ làm tài xế (SCR-016)

#### BE-9.1.1: [DRV] Tạo migration driver_rule_versions to-be, seed 2024-04 và hàm hiệu lực
Migration driver_rule_versions thêm cột metadata (source_checked_on, ext_reason, ext_evidence_ref, copied_from_id, retired_reason, *_by/*_at) và 2 tham số mới long_day_threshold_h (14), drive_2week_anchor_date (2024-04-01); seed bản 2024-04 và hàm effective_driver_rule_version(p_at).

- [ ] CHECK ext đồng bộ (2 cột ext cùng null hoặc cùng có), UNIQUE partial effective_from WHERE active
- [ ] Trigger chặn UPDATE khi status <> 'draft'
- [ ] Seed 2024-04 đủ 17 tham số + 2 tham số mới, ext = null
- [ ] Hàm effective_driver_rule_version(p_at) + unit test SQL chọn bản theo ngày

**AC:**
- effective_driver_rule_version('2024-03-31') trả null, ('2024-04-01') trả bản 2024-04
- UPDATE trực tiếp bản active bị trigger chặn
- Bản seed có long_day_threshold_h = 14 và drive_2week_anchor_date = 2024-04-01

#### BE-9.1.2: [DRV] Xây catalog tham số, hàm diff và API đọc/so sánh quy tắc
File rule-parameter-catalog.ts (nhãn JP, cột DB, đơn vị, mức, mã BR — 19 tham số gồm 2 tham số mới) + hàm diff thuần TS; API GET /api/driver-rules, GET /api/driver-rules/{id}, GET /api/driver-rules/compare; permission driver_rule:write.

- [ ] Catalog dùng chung cho SCR-016 và engine src/lib/compliance
- [ ] GET list/detail tính displayState, boundPublishedRoutes
- [ ] Compare dùng hàm diff chung, 400 M_189
- [ ] RLS SELECT cho transport_manager/dispatcher/auditor, vai trò khác 403 M_20

**AC:**
- Compare 2 bản chỉ khác long_day_threshold_h trả đúng 1 dòng diff tham số
- admin gọi GET /api/driver-rules nhận 403
- Unit test hàm diff pass cho ext null → 3400

#### BE-9.1.3: [DRV] Làm RPC/API tạo nháp, sửa nháp, xóa nháp quy tắc
RPC create_driver_rule_draft(p_copy_from_id) + POST /api/driver-rules; PATCH /api/driver-rules/{id} với zod 19 tham số + superRefine quan hệ M_177/M_184/M_185; DELETE chỉ bản draft.

- [ ] Gợi ý version_code tháng sau JST + hậu tố -B/-C, regex M_14
- [ ] Ràng buộc quan hệ M_177 (vd. 13h ≤ 15h, 9h ≤ 11h, 10 phút ≤ 30 phút ≤ 4h×60)
- [ ] Khóa lạc quan expected_updated_at → M_22/M_183
- [ ] Ghi audit_log mọi thay đổi

**AC:**
- PATCH restraint_day_std_h=16 > restraint_day_max_h=15 → 422 M_177
- Bật ext nhưng thiếu ext_reason → M_184; ext 3300 ≤ thường 3300 → M_185
- DELETE bản active → 409 M_178

#### BE-9.1.4: [DRV] Làm kích hoạt, hủy, ảnh hưởng tuyến và job retire quy tắc
RPC activate_driver_rule_version (FOR UPDATE + pg_advisory_xact_lock), cancel_driver_rule_version, GET /api/driver-rules/{id}/activation-impact, hàm retire_superseded_driver_rule_versions() lập lịch pg_cron 00:05 JST.

- [ ] Kích hoạt: effective_from ≥ ngày mai JST (M_179), không trùng ngày (M_180), source_note + source_checked_on (M_176), khác bản hiện hành (M_190)
- [ ] Impact: đếm route_versions published/in_progress gắn bản hiện hành, số created/checked phải kiểm lại
- [ ] Hủy chỉ bản 適用予定 (M_192) + lý do
- [ ] Retire idempotent, cảnh báo khi job lỗi

**AC:**
- Kích hoạt với effective_from = hôm nay JST → M_179; = ngày mai → OK
- 2 người kích hoạt cùng ngày song song → 1 thành công, 1 nhận M_180/M_183
- Kích hoạt bản mới không đổi driver_rule_version_id của tuyến đã công bố (BR-DRV-22)

### S9.2: Khung engine kiểm giờ làm và lắp dữ liệu đầu vào

#### BE-9.2.1: [DRV] Dựng khung engine src/lib/compliance và model finding
Module TS thuần checkDriverCompliance(input, ruleVersion) → findings[]: types segment/duty day/rule version, model finding (rule_code, severity, window_start, window_end, limit_value, actual_value, detail), đơn vị giây, không đọc đồng hồ ngoài tham số.

- [ ] Mỗi rule 1 file < 200 dòng, đăng ký qua registry
- [ ] Hàm tiện ích ca/ngày: 始業, 終業, 拘束, giờ lái, tuần thứ Hai, tháng JST, năm tài chính
- [ ] Map tham số từ rule-parameter-catalog.ts
- [ ] Bộ fixture LY2 (DRV-003, D = 2026-11-08) dùng chung cho unit test các rule

**AC:**
- Engine chạy với 0 rule đăng ký trả findings rỗng, deterministic (2 lần chạy cùng input → cùng output)
- Hiển thị cắt xuống phút, so sánh bằng giây (unit test 4h00m30s > 4h)

#### BE-9.2.2: [DRV] Viết hàm SQL lắp dữ liệu đầu vào kiểm giờ làm theo ngày
Hàm select_driver_duty_days(p_driver_id, p_from, p_to, p_exclude_route_id) chọn 1 nguồn/ngày (actual_manual/actual_app > route_plan của bản published mới nhất tuyến khác, bỏ tuyến bị hủy) và get_compliance_input(p_route_version_id, p_rule_version_id) trả segments + duty days từ đầu năm tài chính → service_date + 14 ngày.

- [ ] Lọc route_versions.status = 'published' (bỏ superseded) và routes.status <> 'cancelled'
- [ ] Ngày đã qua không bản ghi = 0h, trả danh sách ngày cho M_636
- [ ] D+1 chưa có thực tế lẫn kế hoạch → đánh dấu 'không có dữ liệu', không coi 0h
- [ ] Trừ khoảng sự cố approved chồng D−1 cho BR-DRV-09 (trả kèm overlap)

**AC:**
- Ngày có cả actual_manual và route_plan → chỉ lấy actual_manual
- Bản ghi route_plan của chính tuyến đang kiểm và của bản superseded không xuất hiện
- Hàm được tái dùng bởi get_driver_month_restraint (thẻ 4.11) — cùng kết quả cho cùng tháng

#### BE-9.2.3: [DRV] Cài đặt hàm input_hash dùng chung cho kiểm và công bố
1 cài đặt duy nhất compute_compliance_input_hash(p_route_version_id, p_rule_version_id) trong SQL: SHA-256 (pgcrypto) của JSON chuẩn hóa {segments, id + giá trị duty record đã dùng, driver_rule_version_id} lấy từ get_compliance_input; POST compliance-checks và publish_route cùng gọi hàm này.

- [ ] Chuẩn hóa: sắp khóa, sắp mảng theo id/thời gian, số dạng cố định
- [ ] Không có bản TS thứ hai tính hash
- [ ] Unit test SQL: đổi 1 giá trị drive_h → hash đổi

**AC:**
- Gọi 2 lần không đổi dữ liệu → cùng hash
- Thêm actual_manual cho D−1 sau khi kiểm → hash khác (dẫn tới M_634)
- Đổi driver_rule_version_id → hash khác

### S9.3: Kiểm thời gian ràng buộc theo ngày và số ngày dài trong tuần

#### BE-9.3.1: [DRV] Cài rule BR-DRV-04/05 ràng buộc/ngày 13h cảnh báo, 15h vi phạm
Giới hạn restraint_day_std_h 13h (cảnh báo) / restraint_day_max_h 15h (vi phạm); ngày = 24h từ 始業, 拘束(D) = 終業 − 始業 + phần ca kế tiếp bắt đầu trước 始業 + 24h, kiểm lại D−1 khi 始業(D) < 始業(D−1) + 24h. Window 04 = [始業 + 13h, 終業], 05 = [始業 + 15h, 終業]; ra cả 2 dòng.

- [ ] Tính phần chồng sang D−1 và trả 拘束 D−1 cho BR-DRV-06
- [ ] Sinh 2 finding riêng 04 và 05 khi > 15h
- [ ] Unit test theo LY2 + layout 1 + ví dụ chồng ngày

**AC:**
- LY2 05:30–21:00 (15h30m) → 05 vi phạm 20:30–21:00 (+30m) và 04 cảnh báo 18:30–21:00
- 13h00m đúng → không cảnh báo; 13h20m → 04 cảnh báo 18:30–18:50; 15h00m đúng → chỉ 04
- D−1 07:30–20:00, D bắt đầu 05:30 → 拘束 D−1 = 14h30m → 04 cảnh báo cho D−1

#### BE-9.3.2: [DRV] Cài rule BR-DRV-06 số ngày ràng buộc > 14h trong tuần
Giới hạn days_over_14h_week_max 2 ngày, ngưỡng long_day_threshold_h 14h, mức cảnh báo; đếm ngày trong tuần thứ Hai–Chủ nhật chứa D có 拘束 > 14h (gồm phần chồng từ BR-DRV-04/05), cảnh báo khi D > 14h và D là ngày thứ 3 trở lên. Window = [始業 + 14h, 終業] của D.

- [ ] Đọc ngưỡng từ long_day_threshold_h (không viết cứng 14)
- [ ] Dùng 拘束 ngày đã tính ở BE-9.3.1
- [ ] Unit test LY2 và biên

**AC:**
- 11/07 14h30m + 11/08 15h30m = 2 ngày → OK; thêm 11/04 14h20m → cảnh báo 19:30–21:00
- Ngày 拘束 đúng 14h00m không được đếm
- D ≤ 14h dù tuần đã có 3 ngày > 14h → không cảnh báo cho D

### S9.4: Kiểm thời gian nghỉ giữa 2 ca (休息期間)

#### BE-9.4.1: [DRV] Cài rule BR-DRV-07/08 nghỉ giữa ca 11h cảnh báo, 9h vi phạm
Giới hạn rest_target_h 11h (cảnh báo) / rest_min_h 9h (vi phạm); nghỉ trước = 始業(D) − 終業 ca gần nhất trước, nghỉ sau = 始業 ca kế tiếp (trong 2 ngày) − 終業(D); < 9h → 08, 9h ≤ x < 11h → 07, 1 dòng/khoảng nghỉ. Window = [終業 trước, 始業 sau].

- [ ] Ca trước/sau lấy từ thực tế hoặc kế hoạch đã công bố (theo BE-9.2.2)
- [ ] Không sinh dòng 07 khi đã có 08 cho cùng khoảng
- [ ] Unit test LY2 + biên

**AC:**
- 11/07 20:00 → 11/08 05:30 = 9h30m → 07 cảnh báo (−1h30m), không có 08
- 11/07 kết thúc 21:00 → 8h30m → 08 vi phạm 21:00–05:30
- Đúng 11h00m → OK; đúng 9h00m → 07 cảnh báo, không vi phạm

### S9.5: Kiểm giờ lái trung bình 2 ngày và 2 tuần

#### BE-9.5.1: [DRV] Cài rule BR-DRV-09 giờ lái trung bình 2 ngày 9h
Giới hạn drive_2day_avg_max_h 9h, mức vi phạm: avg1 = (D−1 + D)/2, avg2 = (D + D+1)/2, D vi phạm khi cả hai > 9h; D+1 chưa có thực tế → dùng kế hoạch đã công bố, chưa có kế hoạch → avg1 > 9h chỉ cảnh báo. Window = [đầu segment lái đầu tiên, cuối segment lái cuối cùng] của D; gồm phần BR-DRV-24 lập kế hoạch (giờ lái D−1 trừ phần chồng sự cố approved, tối đa drive_h).

- [ ] Giờ lái ngày = Σ segment drive (tuyến này) hoặc drive_h (duty record)
- [ ] Không dùng max(avg1, avg2) (bản BR cũ đã bỏ)
- [ ] Trừ overlap sự cố approved cho D−1, không trừ quá drive_h
- [ ] Unit test LY2 + 3 nhánh D+1

**AC:**
- D−1 9h30m, D 10h25m (avg1 9h57m): D+1 kế hoạch 6h00m → OK; 8h00m → vi phạm 06:00–20:30; không có kế hoạch → cảnh báo 06:00–20:30
- avg1 đúng 9h00m → không vi phạm/cảnh báo
- LY2 avg1 = 8h45m, D+1 không có → OK, avg2 hiển thị 「—」

#### BE-9.5.2: [DRV] Cài rule BR-DRV-10 giờ lái trung bình 2 tuần 44h
Giới hạn drive_2week_avg_max_h 44h, mức vi phạm; khối 2 tuần cố định thứ k = [drive_2week_anchor_date + 14k ngày, + 13 ngày] chứa D; tổng giờ lái khối (thực tế + kế hoạch đã công bố + tuyến này) / 2 > 44h → vi phạm, ngày chưa có dữ liệu = 0. Window như BR-DRV-09.

- [ ] Đọc anchor từ rule version (không viết cứng 2024-04-01)
- [ ] Không dùng cửa sổ trượt
- [ ] Unit test LY2 + biên khối

**AC:**
- Anchor 2024-04-01, D = 2026-11-08 → khối 10/26–11/08; LY2 (75h10m + 10h25m)/2 = 42h47m → OK
- Tuần 10/26–11/01 = 46h00m → 44h32m → vi phạm
- D = anchor + 14k (ngày đầu khối) không cộng giờ của khối trước; tổng đúng 88h00m → OK

### S9.6: Lái liên tục 4h và tự chèn nghỉ khi lập tuyến

#### BE-9.6.1: [DRV] Cài module chuỗi lái và rule BR-DRV-11 lái liên tục 4h
Module drive-chain.ts dùng chung: cộng lái vào chuỗi, break ≥ break_min_segment_min (10 phút, BR-DRV-12) cộng vào nghỉ tích lũy, break < 10 phút bỏ qua, service/wait không phải nghỉ và không cắt chuỗi; nghỉ tích lũy ≥ break_min_total_min (30 phút, BR-DRV-13) → đóng chuỗi. Chuỗi có lái > continuous_drive_max_h 4h → vi phạm, window = [đầu lái đầu tiên, cuối lái cuối cùng của chuỗi] + detail thời điểm chạm 4h.

- [ ] API module trả chuỗi + mốc chạm 4h để BR-DRV-21 tái dùng
- [ ] Rule BR-DRV-11 chỉ gọi module, không tự cài lại
- [ ] Unit test biên ADR-006 §5 + LY2

**AC:**
- Chuỗi lái đúng 4h00m → OK; 4h01m → vi phạm
- Nghỉ 9 phút không tính; 3 lần nghỉ 10 phút = 30 phút → reset; lái 2h, nghỉ 15m, lái 2h10m → vi phạm
- LY2 chuỗi 08:10–12:25 (4h15m) → vi phạm 08:10–12:25, chạm 4h lúc 12:10; 荷待ち 40m không reset

#### BE-9.6.2: [DRV] Cài BR-DRV-21 tự chèn nghỉ 30 phút khi lưu tuyến SCR-060
Route handler PUT /api/routes/{id}/stops gọi module chuỗi lái (BE-9.6.1) để chèn nghỉ break_min_total_min (30 phút) ngay sau phục vụ tại điểm dừng gần nhất trước mốc 4h, lặp tới hết; truyền vị trí break đã tính cho build_route_segments (E8 BE-8.2.3) lưu segment_type = 'break', auto_inserted = true và tính lại giờ đến — SQL không cài lại thuật toán.

- [ ] Chèn được → M_616; không có điểm dừng trong chuỗi → không chèn, M_617
- [ ] Rule version hiệu lực hôm nay; không có → M_635, vẫn lưu, không chèn
- [ ] Nghỉ tay < 10 phút bị chặn (validate 10–180)
- [ ] Hợp đồng tham số break với build_route_segments (E8), không dùng segment_type 'rest'

**AC:**
- Chuỗi 4h00m → không chèn; 4h01m → chèn 30 phút tại điểm dừng trước mốc, giờ đến các điểm sau dời 30 phút
- Kết quả chèn của SCR-060 và kết quả kiểm BR-DRV-11 ở SCR-061 khớp trên cùng tuyến (không vi phạm sau khi chèn)

