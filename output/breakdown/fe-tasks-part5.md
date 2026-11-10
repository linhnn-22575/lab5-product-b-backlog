# Frontend Tasks: Product B — Yuki Cold Logistics (LAB-5)

**Date**: 2026-11-10 | **Total**: TBD

---

## E8: F07 Lập tuyến & công bố (phần không thuộc luật giờ lái)

### S8.4: Màn hình lập tuyến SCR-060

#### FE-8.4.1: Dựng khung trang lập tuyến và bảng đơn chưa gán
Chọn ngày qua URL ?date= (chặn quá khứ, guard nháp M_31), badge dịch vụ bản đồ; bảng đơn chưa gán với badge lý do + tooltip, disable đơn lý do tĩnh, nút gán + M_606 + M_609.

- [ ] Đổi ngày khi có nháp → M_31
- [ ] Badge 正常/キャッシュ使用中/障害
- [ ] Chọn nhiều đơn hợp lệ
- [ ] Hiện kết quả gán từng đơn

**AC:**
- Đơn NOT_ALLOCATED không chọn được
- Gán vào tuyến checked hỏi M_606 trước khi gửi

#### FE-8.4.2: Làm bảng tuyến, dialog 新規ルート và các nút lưu/kiểm
Bảng tuyến (xe, vùng, tài xế, 出庫, tải %, 計画拘束 tham khảo, trạng thái), dialog 新規ルート (xe/tài xế đã dùng disable, giờ bước 5 phút), nút 保存/再取得/拘束時間チェック (lưu nháp rồi sang SCR-061), chỉ đọc khi published hoặc auditor (M_607).

- [ ] 計画拘束 không tô màu 13h/15h
- [ ] Option đã dùng disable
- [ ] Nút 拘束時間チェック lưu trước khi chuyển
- [ ] Chế độ chỉ đọc ẩn mọi nút ghi

**AC:**
- Tuyến published hiện chỉ đọc + M_607
- Tạo tuyến xong xuất hiện ngay trong bảng

#### FE-8.4.3: Làm bảng điểm dừng dạng nháp với sắp xếp và service time
Bảng điểm dừng nháp: ↑↓/外す, sửa service time, badge khung giờ khách/サービス時間外, hiển thị badge 自動 cho segment auto_inserted (logic chèn ở E9), dòng tổng, beforeunload, xử lý M_22/M_614/M_615 khi lưu.

- [ ] Mọi sửa là nháp tới khi 保存
- [ ] Badge cảnh báo khung khách
- [ ] Hiển thị nghỉ tự động chỉ đọc
- [ ] Guard rời trang

**AC:**
- Đổi thứ tự rồi rời trang hỏi M_31
- Lưu bị rollback M_614 giữ nguyên nháp trên màn

#### FE-8.4.4: Làm dialog thêm điểm nghỉ và nhập tay thời gian di chuyển
Dialog thêm điểm nghỉ (10–180 phút, < 10 phút không tính nghỉ) và dialog nhập tay thời gian di chuyển (1–720 phút, căn cứ 10–500 ký tự, banner M_620), confirm ghi đè đoạn manual M_31.

- [ ] Validate M_06
- [ ] Banner khi bản đồ 障害
- [ ] Confirm trước khi ghi đè manual
- [ ] Đưa kết quả vào nháp

**AC:**
- Nghỉ 9 phút bị chặn với thông báo
- Nhập tay thiếu căn cứ không lưu được

### S8.5: Quản lý phiên bản tuyến, công bố và hủy (SCR-062)

#### FE-8.5.1: Làm header, dải trạng thái, checklist và nút 公開 SCR-062
Header + badge bản, dải 5 bước, checklist trước công bố (dữ liệu kiểm/xác nhận/rule version do E9 cung cấp, độ mới thời gian di chuyển, số đoạn nhập tay), nút 公開 + dialog M_640 (+M_648), lỗi 422 làm mới checklist; khối trạng thái thông báo + KPI.

- [ ] Link sang SCR-061
- [ ] Làm mới checklist khi 422
- [ ] Badge 送信待ち/送信済/送信失敗
- [ ] KPI 目標/基準値

**AC:**
- Publish lỗi hiện lý do và checklist cập nhật
- Thông báo thất bại hiện badge đỏ

#### FE-8.5.2: Làm bảng phiên bản, diff và dialog đổi/hủy/bỏ nháp
Bảng phiên bản + chọn so sánh (M_649) + bảng diff + đơn ảnh hưởng; dialog 公開後の変更 (M_644, 区分, lý do), dialog hủy tuyến (M_647, lỗi khi có đơn đã xuất), nút bỏ nháp (M_31).

- [ ] Chỉ cho chọn đúng 2 bản
- [ ] Validate lý do 10–500
- [ ] Hiện lỗi chặn hủy rõ đơn nào đã xuất
- [ ] Ẩn nút với auditor

**AC:**
- Chọn 3 bản → M_649
- Sau tạo nháp, badge tuyến vẫn published kèm chú thích có nháp

## E9: ★ Ràng buộc giờ lái xe tải 2024 (改善基準告示)

### S9.1: Quản lý phiên bản quy tắc giờ làm tài xế (SCR-016)

#### FE-9.1.5: [DRV] Dựng trang danh sách và form chi tiết tham số quy tắc giờ làm
Trang /master/driver-rules: bảng phiên bản (badge trạng thái, chọn tối đa 2), banner M_175/M_191; form 5 nhóm tham số gồm 2 field mới (14h超 ngưỡng ngày dài, ngày khởi điểm khối 2 tuần) và nhóm gia hạn 労使協定.

- [ ] Cột chung: giá trị, đơn vị, badge 違反/警告, mã BR tooltip, mặc định 2024-04
- [ ] Tô vàng khi khác bản nguồn (M_193), readonly khi không phải draft
- [ ] Toggle 労使協定: lần đầu nạp 3400/310, OFF thì clear (M_186)
- [ ] Validation client khớp zod server

**AC:**
- dispatcher mở trang thấy form readonly, không có nút sửa
- Field long_day_threshold_h và drive_2week_anchor_date hiển thị và lưu được ở bản draft
- Tắt toggle 労使協定 rồi lưu → 2 giới hạn ext lưu null

#### FE-9.1.6: [DRV] Làm nút thao tác, dialog kích hoạt và màn so sánh quy tắc
Nhóm nút theo ma trận trạng thái (lưu/xóa nháp, sao chép, hủy M_187), dialog kích hoạt gọi activation-impact (M_194/M_182/M_181) và màn compare ?a=&b= (diff tham số + metadata, chỉ hiện khác biệt).

- [ ] Dialog tự lưu trước, gọi lại impact khi đổi ngày
- [ ] Chặn kích hoạt khi không khác bản hiện hành (M_190), lỗi 409 hiện trong dialog
- [ ] Compare đồng bộ URL, định dạng +40 / — → 3400 / 無効 → 有効
- [ ] Guard rời trang khi chưa lưu (M_31)

**AC:**
- Đổi ngày hiệu lực trong dialog → số tuyến ảnh hưởng được tải lại
- Compare 2 bản giống hệt với 'chỉ hiện khác biệt' → bảng rỗng + dòng tổng 0

### S9.9: Màn timeline tài xế và vi phạm giờ làm (SCR-061)

#### FE-9.9.2: [DRV] Dựng component Gantt timeline tài xế với dải vi phạm
Gantt hàng D−1/D/D+1, trục 04–23 + vùng ngoài khung dịch vụ, màu segment, nghỉ tự chèn, dải vi phạm (đỏ nhạt viền đứt) / cảnh báo (vàng) từ window_start–window_end, đoạn đỏ đậm BR-DRV-11 từ mốc chạm 4h, dải 休息 vắt 2 hàng, overlay sự cố 「事象 EV-xxxxxx」, chú giải 8 ký hiệu.

- [ ] Dải vẽ đúng phút theo window từ API, không tự tính lại rule
- [ ] Màu kèm chữ/ký hiệu (WCAG), aria-label
- [ ] Wait/service hiển thị khác break

**AC:**
- Fixture LY2: dải 05 20:30–21:00, dải 11 08:10–12:25 với đỏ đậm 12:10–12:25, dải 休息 20:00 (D−1) – 05:30 (D)
- Overlay sự cố approved hiện nhưng không đổi dải vi phạm

#### FE-9.9.3: [DRV] Làm bảng phát hiện và dialog xác nhận cảnh báo SCR-061
Bảng phát hiện (rule, mức, khoảng giờ, giới hạn, giá trị, chênh, diễn giải, popover gợi ý sửa) + checkbox xác nhận chỉ cho warning, dialog 区分 (6 giá trị) + 根拠メモ gọi POST acks.

- [ ] Dòng violation hiện 「—（公開不可）」
- [ ] Đã xác nhận → khóa, hiện 「確認済 MM/DD HH:mm người」
- [ ] Disable khi xem lần kiểm cũ / tuyến đã công bố, ẩn với auditor

**AC:**
- Thiếu 区分 → M_639, memo < 10 ký tự → M_06 ngay trên dialog
- Xác nhận xong không bỏ tick được, reload vẫn khóa

#### FE-9.9.4: [DRV] Làm header, bảng phán định theo rule và cổng 公開へ進む
Header tuyến + nhãn rule version (link SCR-016, ghi chú không áp ngược), nút チェック実行, chọn lần kiểm cũ (chỉ đọc), banner M_633/M_634; bảng phán định 1 dòng/rule (04/05, 07/08 gộp) với lũy kế, avg1/avg2, XhYYm; nút 公開へ進む disable kèm lý do đầu tiên.

- [ ] Cổng: checked + lần kiểm mới nhất + 0 vi phạm + mọi cảnh báo đã xác nhận + hash khớp + rule version hiệu lực
- [ ] Lý do disable theo thứ tự M_631/M_632/M_634/M_633
- [ ] Cột 9.7 = mức nặng nhất của rule

**AC:**
- Còn 1 cảnh báo chưa xác nhận → nút disable với lý do M_632
- Xem lần kiểm cũ → nút chạy kiểm và 公開へ進む disable

### S9.10: Sự cố bất khả kháng và báo cáo tuân thủ (SCR-063)

#### FE-9.10.7: [DRV] Dựng trang danh sách, chi tiết và duyệt sự cố SCR-063
Trang SCR-063: bộ lọc (mặc định theo vai trò), bảng sự cố EV-xxxxxx, panel chi tiết + tải bằng chứng signed URL + kết quả kiểm liên quan 'không đổi', nút 承認/却下 + nhận xét (M_664).

- [ ] Ẩn duyệt với người ghi và vai trò không phải transport_manager
- [ ] Signed URL hết hạn → tải lại
- [ ] Trạng thái loading/lỗi

**AC:**
- Từ chối thiếu nhận xét → M_06
- auditor thấy danh sách, không thấy nút duyệt

#### FE-9.10.8: [DRV] Làm dialog đăng ký sự cố và khối báo cáo tuân thủ
Dialog 事象を登録 (chọn tuyến prefill ?route_id, tài xế tự lấy, loại, datetime bước 5 phút, upload, validate client, banner bất biến, M_31) và khối tổng hợp báo cáo tuân thủ (chọn tháng, lịch thường / theo sự cố, link CSV).

- [ ] Validate client khớp server
- [ ] Gửi multipart kèm Idempotency-Key
- [ ] Hiển thị 2 bảng báo cáo tách biệt

**AC:**
- Mở từ SCR-061 với ?route_id → tuyến và tài xế điền sẵn
- Chọn tháng → 2 bảng và link CSV đúng tháng

### S9.11: Nhập giờ làm thực tế của tài xế (SCR-064 乗務実績入力 — mới)

#### FE-9.11.3: [DRV] Dựng màn nhập giờ làm thực tế theo ngày × tài xế
Màn SCR-064: chọn ngày, lưới tài xế (kế hoạch đã công bố làm gợi ý, ô 始業/終業/lái/nghỉ), lưu theo ngày, hiển thị lỗi theo dòng, đánh dấu ngày còn trống (liên quan M_636).

- [ ] Prefill từ route_plan bản published
- [ ] Validate client khớp server, guard M_31
- [ ] Chỉ đọc cho auditor

**AC:**
- Lưu ngày có 1 dòng lỗi → dòng đó tô đỏ, dòng khác không mất dữ liệu đã nhập
- Ngày quá khứ chưa nhập được đánh dấu 'chưa nhập'

### S9.12: Thẻ cảnh báo giờ lái trên trang chủ (SCR-002 4.8/4.10/4.11)

#### FE-9.12.2: [DRV] Làm thẻ 4.11 với bảng tài xế gần chạm hạn 拘束時間
Thẻ 4.11 dùng component thẻ chung + bảng con tài xế (badge 残り, 超過, 「ほか n名」, chú thích 拘束時間 ≠ 運転時間); thẻ 4.8/4.10 cấu hình link SCR-061/SCR-063 theo quyền.

- [ ] Số 0 → xám 対応不要
- [ ] Màu kèm chữ (WCAG)
- [ ] Link chỉ khi vai trò được xem màn đích

**AC:**
- 7 tài xế ≥ 90% → hiện 5 + 「ほか 2名」
- Tài xế vượt 284h hiện badge 超過

