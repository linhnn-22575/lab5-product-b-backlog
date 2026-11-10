# QA (Manual) Tasks: Product B — Yuki Cold Logistics (LAB-5)

**Date**: 2026-11-10 | **Total**: TBD

---

## E9: ★ Ràng buộc giờ lái xe tải 2024 (改善基準告示)

### S9.1: Quản lý phiên bản quy tắc giờ làm tài xế (SCR-016)

#### QA-9.1.7: [DRV] Viết test case + chạy test SCR-016
Test case ma trận validation M_177 từng cặp, biên ngày hiệu lực, vòng đời draft→active→retired, RBAC 3 vai trò + 403, BR-DRV-22 không áp ngược, so sánh, 2 tham số mới; chạy cả kịch bản đồng thời và job retire qua nửa đêm JST.

- [ ] Ma trận M_177/M_184/M_185
- [ ] Kích hoạt đồng thời, sửa nháp sau khi bị kích hoạt (M_183)
- [ ] Job retire 00:05 JST chuyển bản cũ sang 廃止
- [ ] Ghi kết quả + bug

**AC:**
- 100% test case đã chạy, bug ghi lại có bước tái hiện
- Có case xác nhận tuyến đã công bố giữ bản cũ sau khi kích hoạt bản mới

### S9.6: Lái liên tục 4h và tự chèn nghỉ khi lập tuyến

#### QA-9.6.3: [DRV] Viết test case + chạy test biên lái liên tục và tự chèn nghỉ
Test BR-DRV-11/21 trên SCR-060 → SCR-061: biên 4h00/4h01, nghỉ 9 phút, 3×10 phút, không có điểm dừng M_617, thiếu rule version M_635, nghỉ tay < 10 phút bị chặn.

- [ ] Dữ liệu tuyến dựng sẵn cho từng biên
- [ ] Kiểm hiển thị nghỉ tự chèn trên bảng điểm dừng và Gantt
- [ ] Ghi kết quả + bug

**AC:**
- Mọi biên ADR-006 §5 có ít nhất 1 case pass/fail rõ ràng
- Case xác nhận SCR-060 và SCR-061 cho cùng kết luận trên cùng tuyến

### S9.9: Màn timeline tài xế và vi phạm giờ làm (SCR-061)

#### QA-9.9.5: [DRV] Viết test case theo từng rule giờ làm SCR-061
Thiết kế test case cho từng rule BR-DRV-01..14 từ ví dụ SCR-061 §logic-9 (LY2, layout 1/2) và biên ADR-006 §5, kiểm window hiển thị đúng phút trên Gantt và bảng.

- [ ] Mỗi rule ≥ 1 case OK, 1 case biên, 1 case vượt
- [ ] Dữ liệu seed theo R-06 routes-and-drivers.csv
- [ ] Case BR-DRV-14 bật/tắt

**AC:**
- Bộ test case phủ 12 rule kiểm + BR-DRV-14, có giá trị mong đợi window cụ thể
- Được BrSE review với ví dụ spec

#### QA-9.9.6: [DRV] Chạy test luồng kiểm–sửa–xác nhận–công bố với seed R-06
Chạy bộ test QA-9.9.5 và luồng: kiểm → vi phạm → sửa → kiểm lại → checked → xác nhận → công bố; hash lệch khi ghi thực tế mới; đổi rule version; auditor xem lần kiểm cũ; seed R-06.

- [ ] Chạy trên seed R-06
- [ ] Luồng M_633/M_634 và cổng SCR-062
- [ ] Ghi kết quả + bug

**AC:**
- 100% case đã chạy, mọi vi phạm của seed R-06 khớp giá trị mong đợi
- Không công bố được tuyến còn vi phạm ở mọi đường (UI và gọi API trực tiếp)

### S9.10: Sự cố bất khả kháng và báo cáo tuân thủ (SCR-063)

#### QA-9.10.9: [DRV] Viết test case + chạy test SCR-063
Test bất biến (UPDATE trực tiếp bị chặn), duyệt 2 người, chồng ca/chồng sự cố, file sai định dạng/quá 10MB, phạm vi cắt sự cố theo từng rule (04/05, 09, 11 cắt; 01/02/03/06/07/08/10 không cắt), CSV, signed URL hết hạn.

- [ ] Ma trận rule × sự cố approved/rejected
- [ ] Case báo cáo over-plan
- [ ] Ghi kết quả + bug

**AC:**
- 100% case đã chạy, mỗi rule có case cắt/không cắt rõ ràng
- Có case xác nhận duyệt sự cố không đổi kết quả kiểm cũ

### S9.11: Nhập giờ làm thực tế của tài xế (SCR-064 乗務実績入力 — mới)

#### QA-9.11.4: [DRV] Viết test case + chạy test SCR-064
Test nhập thực tế: chồng ca, tổng lái + nghỉ vượt ca, ngày tương lai, phân quyền, audit, và tác động: kiểm lại SCR-061 dùng thực tế thay kế hoạch, hash lệch M_634.

- [ ] Case thực tế ưu tiên hơn kế hoạch trong engine
- [ ] Case audit giá trị cũ
- [ ] Ghi kết quả + bug

**AC:**
- 100% case đã chạy
- Có case BR-DRV-09 đổi kết luận sau khi nhập thực tế D−1

### S9.12: Thẻ cảnh báo giờ lái trên trang chủ (SCR-002 4.8/4.10/4.11)

#### QA-9.12.3: [DRV] Viết test case + chạy test thẻ giờ lái SCR-002
Test thẻ 4.8/4.10/4.11: 284h vs 310h ext, ngưỡng 90%, actual vs plan published, bản superseded không bị cộng, khớp số với SCR-061.

- [ ] Biên 90%
- [ ] Theo vai trò thấy/không thấy thẻ
- [ ] Ghi kết quả + bug

**AC:**
- 100% case đã chạy
- Số giờ thẻ 4.11 bằng lũy kế tháng ở SCR-061 trên cùng dữ liệu

## E11: Kiểm thử tích hợp, UAT & quản lý dự án

### S11.1: Kiểm thử tích hợp luồng hàng hóa end-to-end

#### QA-11.1.1: Viết kịch bản tích hợp xuyên màn hình SCR-022→042→060→061→062→053
Kịch bản end-to-end theo luồng architecture §5.1–5.4, gồm nhánh lỗi: lô cách ly, 日付逆転 có/không ngoại lệ, tuyến vi phạm giờ lái không công bố, đổi tuyến sau công bố vẫn xuất được.

- [ ] Luồng chính 1 khách/1 SKU/1 tuyến
- [ ] Nhánh 日付逆転 + SCR-044
- [ ] Nhánh vi phạm giờ lái chặn công bố
- [ ] Nhánh đổi tuyến sau công bố
- [ ] Hồi quy K-01…K-08 (phần prototype đang đúng, phải giữ): 日付逆転 so lần giao gần nhất, 消費期限 chặn cứng, app_today() JST, ngưỡng nhiệt là dữ liệu, RLS mọi bảng, tự cách ly khi nhập ngoài ngưỡng

**AC:**
- Mỗi kịch bản có dữ liệu đầu vào và kết quả mong đợi cụ thể
- Phủ đủ 4 nhánh trên
- Cả 8 mục K-01…K-08 có ca test và đạt sau khi làm xong E1–E7

#### QA-11.1.2: Chạy kiểm thử tích hợp trên môi trường staging và ghi lỗi
Chạy toàn bộ kịch bản QA-11.1.1 trên staging, ghi bug thành issue có bước tái hiện, kiểm lại sau khi sửa.

- [ ] Chuẩn bị seed staging
- [ ] Chạy và ghi kết quả từng kịch bản
- [ ] Tạo issue bug
- [ ] Retest

**AC:**
- Báo cáo kết quả có tỉ lệ pass
- Mọi bug mức cao đã retest

### S11.2: UAT với fixture RFP R-06

#### QA-11.2.1: Nạp fixture R-06 và đối chiếu kết quả mong đợi
Nạp fixture R-06 (CUS-003/CHI-002, AGR-008/014, routes-and-drivers.csv) vào staging, chạy và so với kết quả mong đợi của RFP.

- [ ] Script nạp fixture
- [ ] Chạy kịch bản phân bổ
- [ ] Chạy kịch bản giờ lái
- [ ] Bảng đối chiếu kết quả

**AC:**
- Mọi dòng fixture có kết quả thực tế = mong đợi hoặc có issue giải thích

