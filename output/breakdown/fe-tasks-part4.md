# Frontend Tasks: Product B — Yuki Cold Logistics (LAB-5)

**Date**: 2026-11-10 | **Total**: TBD

---

## E6: F04 Đơn hàng & phân bổ

### S6.2: Danh sách đơn hàng và hủy đơn (SCR-040)

#### FE-6.2.3: Dựng màn danh sách đơn: thanh lọc, bảng đơn và dialog hủy đơn
Trang SCR-040 gọi GET /api/orders và POST cancel: thanh lọc đồng bộ query string, bảng 11.1–11.12 (badge trạng thái/tiến độ/business_review/ngoại lệ), phân trang 50, dialog hủy [13].

- [ ] Validation từ ngày > đến ngày (M_13), clear, giữ query khi quay lại từ SCR-042
- [ ] Ngày yêu cầu quá hạn chữ đỏ + tooltip M_444; ẩn 取消 khi routed (kèm hướng dẫn gỡ tuyến)
- [ ] Dialog hủy tải số phân bổ/yêu cầu mới nhất, M_400, lý do, 「取消中…」
- [ ] Ẩn nút theo quyền, menu cho mọi vai trò

**AC:**
- Vai trò chỉ xem không thấy 新規受注/引当/取消
- Hủy thành công thì dòng cập nhật trạng thái cancelled không cần reload tay

### S6.3: Đăng ký đơn hàng nhập tay (SCR-041)

#### FE-6.3.3: Dựng form đăng ký đơn: phần đầu và bảng dòng SKU động
Phần đầu (khách, ngày yêu cầu với hôm nay từ server, mã tham chiếu check khi blur) và bảng dòng 6.1–6.8: thêm/xóa ≤ 50, chống trùng SKU, tra hợp đồng từng dòng, badge window_rule, điều kiện giao.

- [ ] Ref ^[0-9A-Za-z_-]{1,50}$, gọi check-ref khi blur (M_408)
- [ ] Đổi khách/ngày → tra lại hợp đồng mọi dòng
- [ ] Cảnh báo M_407 (thiếu rule), M_413 (đổi điều kiện giao), chặn M_405
- [ ] Badge vùng/loại hạn mỗi dòng

**AC:**
- Không thêm được dòng thứ 51 và SKU trùng
- Đổi ngày yêu cầu cập nhật badge hợp đồng của mọi dòng

#### FE-6.3.4: Làm gửi form đơn: tóm tắt lỗi, Idempotency-Key, giữ form khi 401
Tóm tắt lỗi, submit POST /api/orders với Idempotency-Key sinh khi mở form, toast M_412 → SCR-042, xác nhận rời trang M_31, lưu/khôi phục form từ sessionStorage khi 401.

- [ ] Map error body {code, messageId, params} vào dòng/field
- [ ] Chống gửi 2 lần
- [ ] M_31 khi rời trang có thay đổi
- [ ] Khôi phục sessionStorage sau đăng nhập lại

**AC:**
- Bấm đăng ký 2 lần chỉ tạo 1 đơn
- Hết phiên rồi đăng nhập lại vẫn còn dữ liệu form

### S6.4: Phân bổ lô cho dòng đơn và gửi ngoại lệ 日付逆転 (SCR-042)

#### FE-6.4.4: Dựng khung SCR-042: thông tin đơn, đầu panel dòng, bảng phân bổ đã có
Header + badge đơn, thông tin đơn (基準日 từ server, 要求日超過), chú giải ①–⑥, đầu panel mỗi dòng + banner business_review, bảng phân bổ 11.1–11.6 + dialog hủy phân bổ [15].

- [ ] Chế độ chỉ xem theo vai trò và trạng thái routed/shipped/cancelled (M_430)
- [ ] Banner business_review link SCR-011 theo quyền, ẩn chọn/phân bổ
- [ ] Dialog hủy phân bổ lý do bắt buộc, xem chi tiết bằng chứng
- [ ] 404 M_23, xung đột M_22 + tự tải lại

**AC:**
- Đơn routed hiển thị chỉ xem, không có nút hủy phân bổ
- Dòng business_review không có ô chọn lô kể cả với admin

#### FE-6.4.5: Dựng bảng lô ứng viên 8.1–8.12 có badge lý do loại và lô on_hold
Bảng ứng viên từ GET allocation-candidates: hạn/ngày còn, SX/nhập, vị trí, trạng thái (badge 保留 cho on_hold — G-1), khả dụng, lần giao trước + link 納品履歴を見る, bằng chứng cửa sổ, badge first_reason + tooltip other_reasons.

- [ ] Badge ①–⑥ theo first_reason, tooltip other_reasons
- [ ] Checkbox hiện lô bị loại (lưu localStorage)
- [ ] Link 「納品履歴を見る」 mở SCR-043 với khách + SKU (G-12)
- [ ] Ẩn bảng khi dòng allocated

**AC:**
- Lô on_hold hiện khi bật checkbox, badge 保留 và lý do ③
- Lô bị loại bởi nhiều lớp hiện badge lớp đầu, tooltip liệt kê các lớp còn lại

#### FE-6.4.6: Làm form phân bổ lô và dialog xác nhận lô quá 賞味期限
Radio chọn lô (mặc định FEFO), nhập SL, cảnh báo M_425 khi chọn ngoài FEFO, dialog [14] xác nhận lô quá 賞味期限, gửi POST /api/allocations với Idempotency-Key, tải lại mọi panel.

- [ ] SL 1..min(残, khả dụng), map M_05/M_426/M_427
- [ ] Dialog 賞味期限 gửi cờ xác nhận (tránh M_424)
- [ ] Idempotency-Key, chống gửi 2 lần
- [ ] Tải lại tất cả panel sau thành công/xung đột

**AC:**
- Chọn lô không phải FEFO hiện M_425 trước khi gửi
- Phân bổ thành công cập nhật SL đã phân bổ/còn và trạng thái đơn

#### FE-6.4.7: Dựng bảng yêu cầu ngoại lệ và dialog gửi ngoại lệ 日付逆転
Bảng 12.1–12.5 từ GET /api/date-reversal-requests?orderId= và dialog [13] gửi ngoại lệ: khối so sánh hạn, trục ngày, SL, lý do, bằng chứng file hoặc số biên bản, gửi multipart.

- [ ] Nút ngoại lệ chỉ khi first_reason = DATE_REVERSAL và vai trò sales_planner
- [ ] Validation M_442/M_434/M_435, trùng pending M_436
- [ ] Hiển thị DRX-xxxxxx, trạng thái pending/approved/rejected/expired + expire_reason

**AC:**
- sales_manager/admin không thấy nút gửi ngoại lệ
- Gửi thành công thêm 1 dòng pending vào bảng, không tạo phân bổ

### S6.5: Lịch sử giao theo khách (SCR-043)

#### FE-6.5.2: Dựng màn lịch sử giao: thanh lọc combobox và bảng có badge mốc
Thanh lọc (khách, SKU gồm 「（無効）」, mã lô, ngày giao, chỉ dòng mốc) nhận/ghi URL; bảng 12.1–12.8 có badge 日付逆転比較基準/移行データ, link SCR-031/SCR-053, phân trang, 500件以上 + M_462.

- [ ] Lần đầu tự tìm theo URL; đổi combobox không tự tìm
- [ ] Từ > đến → M_461 không gọi API; mã lô M_13/M_04
- [ ] Dòng 移行データ không link + M_463; shipment_id null → 「—」
- [ ] Skeleton, M_32, M_40 + correlation_id/M_41 + 再試行

**AC:**
- Mở URL từ link SCR-042 hiển thị sẵn kết quả theo khách + SKU
- Kết quả > 500 dòng hiện 500件以上 và M_462

### S6.6: Duyệt ngoại lệ 日付逆転 (SCR-044)

#### FE-6.6.6: Dựng trang danh sách duyệt 日付逆転: tab, bộ lọc, menu và deep-link
Route /approvals/date-reversal: 5 tab + đếm, bộ lọc khách/SKU/ngày gửi (M_13) ghi query string, bảng DRX-xxxxxx có so hạn và badge 本日期限, paging; menu 「日付逆転承認」, guard route, deep-link ?id= / ?orderId=.

- [ ] Tab + đếm theo API, sort theo tab
- [ ] Guard: vai trò ngoài 4 vai trò → M_20
- [ ] Deep-link mở sẵn panel chi tiết
- [ ] Loading/Empty M_32/Error M_40/M_41

**AC:**
- Mở /approvals/date-reversal?id=X hiển thị đúng yêu cầu X
- Vai trò không có quyền vào thẳng URL nhận M_20

#### FE-6.6.7: Dựng panel chi tiết yêu cầu, khối kiểm lại và dialog duyệt/từ chối
Panel 8.1–8.3 (so hạn, lý do, link bằng chứng), khối 8.4 kiểm lại hiện tại, timeline 8.8, nút 承認/却下 theo quyền/trạng thái, dialog xác nhận [9], M_454, banner kết quả [10], M_450 → reload.

- [ ] Kiểm lại có ✕ vẫn cho 承認 (ghi expired) theo spec, có chú thích
- [ ] Từ chối nhận xét 10–500, duyệt nhận xét ≤ 500
- [ ] Banner hiển thị approved/expired + expire_reason

**AC:**
- Người gửi yêu cầu không thấy nút 承認/却下 với yêu cầu của mình
- Duyệt ra expired hiển thị banner lý do, không báo lỗi

## E7: F05 Kiểm trước xuất

### S7.3: Màn hình quét, kiểm và xác nhận xuất

#### FE-7.3.1: Dựng trang /outbound: tab, bộ lọc, bảng chờ xuất và đã xuất
Trang /outbound gọi GET pending-and-done: tab 出荷待ち/出荷済み có đếm, lọc ngày + tuyến (gồm ルート未割当), sort, nút 検品開始 + tooltip M_465/M_466 khi bị chặn.

- [ ] Tab + số đếm
- [ ] Bộ lọc giữ trên URL
- [ ] Nút 検品開始 disable theo canStartCheck
- [ ] Hiện xe, tài xế, giờ xuất phát

**AC:**
- Đơn tuyến chưa published hiện tooltip M_465/M_466
- Lọc ルート未割当 chỉ ra đơn chưa gán tuyến

#### FE-7.3.2: Dựng trang kiểm: header, khung tuyến, khung 積込確認
Trang /outbound/[orderId]: header đơn, khung tuyến (bản, xe, tài xế, giờ xuất phát), render theo ma trận trạng thái 053#8, ghi chú chỉ xem M_484; khung 積込確認 mã xe (M_472), niêm phong, 2 nhiệt độ, nhãn ngưỡng, cảnh báo M_479, M_483/M_473.

- [ ] Render theo ma trận đơn × tuyến × vai trò
- [ ] Validate mã xe/vùng xe phía client
- [ ] Hiện ngưỡng nhiệt áp dụng
- [ ] Cảnh báo nhiệt ngoài ngưỡng trước khi gửi

**AC:**
- Vai trò chỉ xem không thấy nút xác nhận, có ghi chú M_484
- Nhiệt ngoài ngưỡng hiện M_479 ngay khi nhập

#### FE-7.3.3: Làm bảng kiểm dòng hỗ trợ máy quét và nhập tay có lý do
Bảng kiểm dòng: radio scan/manual, tách mã vạch {sku}|{lot} (M_486), cấm paste khi scan, Enter nhảy ô SL, badge đối chiếu/hạn/cách ly/đảo ngày, lý do nhập tay bắt buộc.

- [ ] Parser mã vạch tách riêng để thay khi khách chốt định dạng
- [ ] Điều hướng phím Enter
- [ ] Chặn paste ở chế độ scan
- [ ] Badge kết quả đối chiếu từng dòng

**AC:**
- Quét sai lô hiện M_469/M_487 trên đúng dòng
- Chọn manual không nhập lý do thì không gửi được

#### FE-7.3.4: Làm luồng xác nhận xuất với dialog, idempotency và xử lý lỗi
Enable nút khi đủ trường, dialog M_482 + M_488, sinh Idempotency-Key 1 lần/lần mở dialog, xử lý 201 / 409 blocked (khung 17 map allocationId/field) / 409 trạng thái / M_22 / 403 / 401 / 500 / mạng, khung 18 đã xuất, guard rời trang M_31.

- [ ] Key giữ nguyên khi retry trong cùng dialog
- [ ] Map lỗi về đúng dòng/trường
- [ ] Hiện bản ghi đã xuất sau 201
- [ ] beforeunload khi có dữ liệu

**AC:**
- Bấm 2 lần chỉ tạo 1 lần xuất
- 409 blocked hiện đủ lỗi tại dòng tương ứng

