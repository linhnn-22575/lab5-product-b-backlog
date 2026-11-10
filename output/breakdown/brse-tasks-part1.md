# BrSE Tasks: Product B — Yuki Cold Logistics (LAB-5)

**Date**: 2026-11-10 | **Total**: TBD

---

## E2: F12 Xác thực & phân quyền

### S2.3: Quản lý người dùng và vai trò (SCR-018)

#### BRSE-2.3.6: Xác nhận với khách các điểm INFERRED của xác thực và trang chủ
Gom câu hỏi SCR-001/002/018: idle 15 phút + cảnh báo 60s, claim amr của IdP, đăng ký thiết bị dùng chung, nguồn M_104, auto-refresh 5 phút, p95 1s, 1 người 1 vai trò, không xóa user.

- [ ] Soạn câu hỏi tiếng Nhật kèm giả định hiện tại
- [ ] Gửi + theo dõi trả lời
- [ ] Cập nhật spec/tham số cấu hình theo câu trả lời

**AC:**
- Mỗi điểm có câu trả lời hoặc giả định được ghi rõ
- Spec SCR-001/002/018 cập nhật

## E3: F01 Master & chính sách nhiệt

### S3.4: Quản lý phiên bản ngưỡng nhiệt (SCR-015)

#### BRSE-3.4.7: Xác nhận với khách các điểm INFERRED của master SKU, hợp đồng, ngưỡng
Gom câu hỏi SCR-010/011/015: danh sách đơn vị, tự viết hoa mã, khóa code/unit/trace_lane; effective_from = hôm nay, mẫu AGR, side-effect order_lines, ngưng khách có hợp đồng tương lai; admin xem SCR-015, 下限なし chỉ 冷凍, ngày seed, cửa sổ 30 ngày.

- [ ] Soạn câu hỏi tiếng Nhật kèm giả định
- [ ] Gửi + theo dõi trả lời
- [ ] Cập nhật spec theo câu trả lời

**AC:**
- Mỗi điểm có câu trả lời hoặc giả định ghi rõ
- Spec SCR-010/011/015 cập nhật

## E4: F02 Nhập hàng

### S4.2: Kiểm nhiệt 2 lớp và xác nhận phiếu idempotent (SCR-022)

#### BRSE-4.2.5: Xác nhận với khách 7 điểm INFERRED của kiểm hàng nhập
Mốc phiên bản ngưỡng = ngày đến; NSX không P0; quy tắc -Q áp ở xác nhận (Q&A-B05 ambient); bao bì hỏng không tự cách ly; thiếu mã trace = trace failure; giờ đến = lúc tạo phiếu; ảnh ≤10MB; chặn lô 消費期限 đã hết tại cửa kho; xóa phiếu draft rỗng.

- [ ] Soạn câu hỏi tiếng Nhật kèm giả định
- [ ] Gửi + theo dõi trả lời
- [ ] Cập nhật SCR-022 spec theo câu trả lời

**AC:**
- Mỗi điểm có câu trả lời hoặc giả định ghi rõ
- Spec SCR-022 cập nhật

## E5: F03 Tồn kho & lô

### S5.3: Máy trạng thái lô: cách ly, 保留, giải phóng, hủy có duyệt 2 người (SCR-037)

#### BRSE-5.3.9: Làm rõ với khách các điểm mở của tồn kho và máy trạng thái lô
Gom câu hỏi E5 gửi khách: N=3 ngày, phạm vi đa kho (warehouse_id), Q&A-B04, Q&A-B12, hủy một phần, tự đóng deviation khi giải phóng, evidence_no, 要移動 có chặn không, định dạng/dung lượng file.

- [ ] Soạn Q&A sheet song ngữ (JP/VN) có phương án đề xuất
- [ ] Theo dõi trả lời, cập nhật clarifications và spec
- [ ] Báo PM rủi ro nếu khách chọn đa kho

**AC:**
- Mọi câu hỏi có trạng thái trả lời/giả định được chốt
- Kết quả được phản ánh vào spec SCR-030/031/037

## E6: F04 Đơn hàng & phân bổ

### S6.1: Pipeline evaluate_lot_for_line — nguồn duy nhất của BR-ALLOC-ORDER (làm trước)

#### BRSE-6.1.7: Làm rõ với khách các điểm mở của đơn hàng, phân bổ và ngoại lệ
Gom câu hỏi E6: Q&A-B01/B02 (ngày SX hay ngày nhập), Q&A-B16, chọn lô ngoài FEFO, pending không giữ tồn, thời điểm ghi exception_events, phân bổ sau ngày yêu cầu, ref/lý do hủy bắt buộc, mặc định lọc, thông báo kết quả duyệt.

- [ ] Soạn Q&A sheet song ngữ (JP/VN), ưu tiên Q&A-B02 vì chặn lớp 4
- [ ] Kèm câu hỏi SCR-040/041/043/044 (INFERRED)
- [ ] Theo dõi trả lời, cập nhật clarifications và spec

**AC:**
- Q&A-B02 có câu trả lời trước khi BE-6.1.3 hoàn tất
- Mọi câu hỏi có trạng thái trả lời/giả định được chốt

## E7: F05 Kiểm trước xuất

### S7.3: Màn hình quét, kiểm và xác nhận xuất

#### BRSE-7.3.1: Làm rõ giả định SCR-053: mã vạch, đảo ngày, lý do nhập tay
Gửi khách Q&A cho gap 053 #1 (kiểm lại đảo ngày lúc xuất), #4 (định dạng {sku}|{lot}), #5 (lý do nhập tay, nhiệt hàng 1 giá trị, trùng niêm phong), #6 (ngoại lệ approved khi mốc giao đổi), #7 (đơn chưa gán, sort, in_progress).

- [ ] Soạn câu hỏi tiếng Nhật kèm giả định hiện tại
- [ ] Ưu tiên #4 vì chặn parser FE
- [ ] Theo dõi trả lời
- [ ] Cập nhật spec + báo task bị ảnh hưởng

**AC:**
- Mỗi gap có câu trả lời hoặc ghi rõ giữ giả định
- Định dạng mã vạch được chốt trước khi FE-7.3.3 xong

## E8: F07 Lập tuyến & công bố (phần không thuộc luật giờ lái)

### S8.5: Quản lý phiên bản tuyến, công bố và hủy (SCR-062)

#### BRSE-8.5.1: Làm rõ giả định F07: 1 tài xế/ngày, IF-MAP-01, KPI, hủy tuyến
Q&A khách cho gap 060 #1 (1 tài xế 1 tuyến/ngày), #3/#4 (timeout, > 24h IF-MAP-01), #5 (tách đơn nhiều vùng), #6 (service mặc định); 062 #2 (hủy khi đã xuất), #3 (KPI 15 phút), #5 (người lập ≠ người công bố), #9 (tuyến kẹt published khi chưa có F06).

- [ ] Soạn câu hỏi tiếng Nhật kèm giả định
- [ ] Ưu tiên 060 #1 vì ảnh hưởng engine E9
- [ ] Theo dõi trả lời
- [ ] Cập nhật spec + báo task bị ảnh hưởng

**AC:**
- Mỗi gap có câu trả lời hoặc ghi rõ giữ giả định
- 060 #1 chốt trước khi E9 làm engine gộp ca

## E9: ★ Ràng buộc giờ lái xe tải 2024 (改善基準告示)

### S9.11: Nhập giờ làm thực tế của tài xế (SCR-064 乗務実績入力 — mới)

#### BRSE-9.11.1: [DRV] Viết spec màn SCR-064 乗務実績入力
Viết SCR-064_SPEC.md theo khuôn spec màn: layout ngày × tài xế, field 始業/終業/lái/nghỉ, validation, phân quyền, message mới, API upsert driver_duty_records source=actual_manual và ảnh hưởng hash (M_634) tới tuyến đã kiểm.

- [ ] Theo mẫu SCR-0xx_SPEC.md (item list, logic, phân quyền, trạng thái, API)
- [ ] Quy tắc sửa: ai, đến bao lâu, audit giá trị cũ
- [ ] Cập nhật ADR-006 §5 và danh sách màn

**AC:**
- Spec được PM/khách review, không còn mục TBD chặn BE/FE
- Có danh sách message mới đăng ký vào message-list

### S9.13: Xác nhận pháp lý và làm rõ Q&A giờ lái

#### BRSE-9.13.2: [DRV] Làm rõ Q&A-B07 労使協定, anchor date, 1 tuyến/ngày, ngày trống
Làm rõ với khách: Q&A-B07 (có 労使協定 không, điều kiện phụ số tháng được vượt 284h), drive_2week_anchor_date thực tế, 1 tài xế tối đa 1 tuyến/ngày, ngày quá khứ không dữ liệu = 0h hay cảnh báo, xác nhận cảnh báo không chuyển sang lần kiểm mới.

- [ ] Ghi từng câu vào Q&A với phương án đề xuất
- [ ] Báo PM tác động nếu 1 tài xế chạy 2 tuyến/ngày (engine phải gộp ca)
- [ ] Cập nhật spec SCR-016/061 sau khi có trả lời

**AC:**
- 5 câu hỏi có trạng thái trả lời/hoãn trong Q&A
- Anchor date chốt được cập nhật vào bản seed hoặc bản rule mới

## E10: Làm rõ spec & Q&A khách (BrSE)

### S10.1: Gửi và chốt Q&A khách cho luồng hàng hóa

#### BRSE-10.1.1: Soạn bộ Q&A tiếng Nhật cho Q&A-B01…B05, B08…B17
Viết lại 15 câu hỏi mở của business-rules §8 thành Q&A tiếng Nhật, mỗi câu kèm phương án đang giả định và ảnh hưởng nếu khác.

- [ ] Mỗi câu có mã, bối cảnh, phương án A/B, giả định hiện tại
- [ ] Ghi issue bị ảnh hưởng
- [ ] Ưu tiên câu chặn BE (B01, B02, B03, B09, B14)
- [ ] Review nội bộ với tech lead

**AC:**
- File Q&A có đủ 15 câu, mỗi câu trỏ được tới issue
- Câu chặn BE được đánh dấu ưu tiên cao

#### BRSE-10.1.2: Hỏi khách vòng duyệt SKU master (RFP S3-01) có bắt buộc Phase 1
SCR-010 cho admin ghi thẳng, RFP S3-01 yêu cầu created→review→active→retired. Xin khách chốt có làm SCR-017 ở Phase 1 hay không (Q&A-B11).

- [ ] Nêu chênh lệch RFP vs thiết kế
- [ ] Ước tính effort nếu phải làm vòng duyệt
- [ ] Ghi kết quả vào PREMISE

**AC:**
- Có câu trả lời của khách hoặc ghi rõ giả định tiếp tục dùng
- PREMISE cập nhật dòng tương ứng

#### BRSE-10.1.3: Phản ánh câu trả lời Q&A vào spec và issue liên quan
Khi khách trả lời, sửa business-rules / spec màn hình, đổi nhãn INFERRED → EXTRACTED và comment vào issue bị ảnh hưởng.

- [ ] Cập nhật bảng Q&A (trạng thái Đã trả lời)
- [ ] Sửa spec + History of change
- [ ] Comment issue bị ảnh hưởng, báo PM nếu đổi effort

**AC:**
- Mỗi câu đã trả lời có commit sửa spec tương ứng
- Issue bị ảnh hưởng có comment trỏ commit

### S10.2: Đồng bộ spec với database design

#### BRSE-10.2.1: Sửa ghi chú lỗi thời 'chưa có trong DB' ở các spec màn hình
Rà SCR-010/011/016/018/037/040/041/043/062: bỏ các ghi chú cột/bảng 'chưa có' khi database-design §3 đã định nghĩa; thống nhất tên cột app_sessions, effective_driver_rule.

- [ ] Grep 'chưa có trong database-design' toàn bộ spec
- [ ] Đối chiếu từng chỗ với DB-001 §3
- [ ] Sửa + ghi History of change

**AC:**
- Grep không còn ghi chú lỗi thời
- Tên hàm/cột trong spec khớp DB-001

