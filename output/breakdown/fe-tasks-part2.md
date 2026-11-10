# Frontend Tasks: Product B — Yuki Cold Logistics (LAB-5)

**Date**: 2026-11-10 | **Total**: TBD

---

## E3: F01 Master & chính sách nhiệt

### S3.1: Quản lý master SKU (SCR-010)

#### FE-3.1.3: Làm layout /master và trang danh sách SKU có bộ lọc, phân trang
Layout nhóm /master/* (điều hướng theo quyền xem), trang SKU: tìm debounce, 3 bộ lọc trên query string, bảng 9 cột + badge/tooltip ngưỡng, phân trang, trạng thái loading/rỗng M_32/lỗi.

- [ ] Điều hướng /master/* chốt 1 cách (tab hoặc menu trái)
- [ ] Bộ lọc đồng bộ URL
- [ ] Badge ngưỡng hiệu lực
- [ ] Nút thêm chỉ hiện cho admin

**AC:**
- Vai trò chỉ xem không thấy nút thêm/sửa
- Reload trang giữ bộ lọc

#### FE-3.1.4: Làm dialog thêm/sửa SKU khóa trường theo inUse và xác nhận ngưng dùng
Dialog thêm/sửa: zod chung, khóa trường khi inUse (ghi chú M_130), chỉ gửi trường đổi, M_31 khi hủy có thay đổi, M_22 + 再読み込み; dialog xác nhận ngưng dùng M_131.

- [ ] Loại hạn radio không chọn sẵn
- [ ] Không đổi gì → không gọi API
- [ ] Khóa trường + ghi chú khi inUse
- [ ] Dialog M_131 khi ON→OFF

**AC:**
- SKU đã dùng không sửa được 5 trường khóa trên UI
- Đóng dialog có thay đổi hiện xác nhận M_31

### S3.2: Quản lý khách hàng (SCR-011 tab 顧客)

#### FE-3.2.2: Làm khung màn SCR-011 và tab 顧客 có dialog khách hàng
Khung 2 tab đồng bộ ?tab=, giữ bộ lọc riêng từng tab; tab 顧客: tìm, gồm ngưng dùng, bảng khách (số hợp đồng + badge 未確定), dialog thêm/sửa (mã readonly khi sửa, M_31 ngưng dùng).

- [ ] Tab đồng bộ query
- [ ] Bảng + badge 未確定
- [ ] Dialog khách + validate
- [ ] Xác nhận ngưng dùng M_31

**AC:**
- Chuyển tab không mất bộ lọc của tab kia
- Ô mã khách bị khóa ở chế độ sửa

### S3.3: Quản lý hợp đồng khách–SKU có phiên bản (SCR-011 tab 契約)

#### FE-3.3.5: Làm tab 契約: bộ lọc, bảng hợp đồng 12 cột và panel lịch sử
Ghi chú M_140, thanh đếm M_151, 5 bộ lọc, bảng 12 cột (badge 業務確認待ち, nền vàng 未確定, trạng thái phiên bản, link SCR-040), panel lịch sử phiên bản v1, v2… có effective_to.

- [ ] 5 bộ lọc đồng bộ URL
- [ ] Bảng + badge, không hiện giá trị đề xuất cho NULL
- [ ] Panel lịch sử
- [ ] auditor xem 全履歴

**AC:**
- Hợp đồng NULL hiện 未確定, không có giá trị gợi ý
- Panel lịch sử hiển thị đúng thứ tự phiên bản

#### FE-3.3.6: Làm dialog đăng ký phiên bản hợp đồng và hủy phiên bản
Dialog 2 chế độ (mới / phiên bản mới), radio window_rule 4 lựa chọn không chọn sẵn, giải thích + ví dụ 18.7, xác nhận M_146 khi chọn 未確定, hiển thị M_141–M_153; hủy phiên bản tương lai M_154.

- [ ] Radio không chọn sẵn, phiên bản mới bắt chọn lại
- [ ] Xác nhận M_146
- [ ] Map lỗi API vào field
- [ ] Dialog hủy M_154

**AC:**
- Không gửi được form khi chưa chọn window_rule
- Chọn 未確定 luôn hiện xác nhận M_146

### S3.4: Quản lý phiên bản ngưỡng nhiệt (SCR-015)

#### FE-3.4.4: Làm trang chính sách nhiệt: thẻ hiện hành, bảng tương lai và lịch sử
Ghi chú M_160, 3 thẻ ngưỡng hiện hành (下限なし, dấu U+2212, thẻ đỏ khi thiếu bản), bảng phiên bản tương lai (chênh đỏ/xanh, sửa/hủy), bảng lịch sử + lọc dải + phân trang.

- [ ] 3 thẻ + trạng thái thiếu bản
- [ ] Bảng tương lai + diff
- [ ] Lịch sử + usage count (không link)
- [ ] Nút ghi chỉ cho quality

**AC:**
- Dải thiếu bản hiệu lực hiện thẻ đỏ, không tự điền
- Vai trò chỉ xem không thấy nút tạo/sửa

#### FE-3.4.5: Làm dialog tạo/sửa phiên bản ngưỡng có xem trước ảnh hưởng
Dialog: chọn dải nạp bản gốc, 下限なし chỉ 冷凍, date picker chặn ≤ hôm nay, đếm ký tự lý do, xác nhận M_169; preview debounce 500ms, câu M_165/M_166, number line có chữ, M_168, trạng thái 計算中/lỗi.

- [ ] Form + validate client
- [ ] Preview debounce + number line (WCAG)
- [ ] Xác nhận M_169, toast M_170
- [ ] 409 M_164 → reload

**AC:**
- Không chọn được ngày ≤ hôm nay
- Đổi ngưỡng cập nhật preview sau 500ms

## E4: F02 Nhập hàng

### S4.1: Tạo phiếu nhập và ghi kết quả kiểm từng dòng (SCR-022)

#### FE-4.1.4: Làm trang danh sách phiếu nhập và dialog tạo phiếu
Vùng lọc (trạng thái, nhà cung cấp, khoảng ngày, số phiếu) đồng bộ URL, kiểm ngày M_225, bảng phiếu (số dòng, thiếu P0, ngoài ngưỡng, trạng thái, người xác nhận), phân trang, dialog tạo phiếu lọc supplier (M_200).

- [ ] Bộ lọc + URL sync
- [ ] Bảng + badge đếm lỗi
- [ ] Dialog tạo phiếu
- [ ] Nút tạo chỉ cho inbound:write

**AC:**
- Tạo phiếu xong chuyển tới trang chi tiết
- Vai trò chỉ xem không thấy nút tạo

#### FE-4.1.5: Làm trang chi tiết phiếu nhập với bảng dòng 14 cột
Header phiếu, bảng dòng 14 cột (badge nhiệt độ/hạn/bao bì/trace/ảnh, tô nền dòng lỗi, cột lô đã sinh khi confirmed), trạng thái loading/not found/empty/confirmed.

- [ ] Header + trạng thái phiếu
- [ ] Bảng + badge phán định
- [ ] Cột lô đã sinh khi confirmed
- [ ] Phiếu confirmed hiển thị giá trị ngưỡng đã chụp

**AC:**
- Dòng ngoài ngưỡng được tô nền và có badge
- Phiếu confirmed không còn nút sửa/xóa dòng

#### FE-4.1.6: Làm form dòng kiểm hàng tối ưu cửa kho và chụp/tải ảnh
Form 13 field: P0 gợi ý không chặn, giữ SKU/vị trí/bao bì sau khi lưu, máy quét + Enter chuyển focus, ô ≥44px, phán định nhiệt khi blur, vị trí lọc theo vùng (通常 / -Q), mã truy xuất theo trace_lane; ảnh capture + thumbnail + thay ảnh.

- [ ] Field + ghi chú bao bì bắt buộc có điều kiện
- [ ] Quét mã + Enter, ô ≥ 44px
- [ ] Vị trí lọc theo vùng SKU
- [ ] Ảnh accept=image/* capture, disable khi dòng chưa lưu

**AC:**
- Lưu dòng xong focus về ô mã lô, giữ SKU/vị trí/bao bì
- Không upload được ảnh khi dòng chưa lưu

### S4.2: Kiểm nhiệt 2 lớp và xác nhận phiếu idempotent (SCR-022)

#### FE-4.2.3: Làm panel kiểm trước xác nhận, dialog xác nhận và dialog kết quả
Panel nhóm Chặn ●/Báo trước ▲ sắp theo dòng, bấm → cuộn + mở form sửa (M_226); dialog xác nhận giữ Idempotency-Key cho mọi lần gửi lại (M_227); dialog kết quả (M_209, bảng lô, link SCR-031/SCR-037 theo quyền); 409/422 cập nhật panel.

- [ ] Panel + điều hướng tới dòng
- [ ] Key sinh khi mở dialog, giữ khi retry
- [ ] Dialog kết quả + link theo quyền
- [ ] Map 409 M_208 / 422 CHECK_FAILED

**AC:**
- Bấm xác nhận 2 lần không sinh 2 request khác key
- Còn lỗi chặn thì nút xác nhận bị vô hiệu

