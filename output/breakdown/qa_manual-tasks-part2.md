# QA (Manual) Tasks: Product B — Yuki Cold Logistics (LAB-5)

**Date**: 2026-11-10 | **Total**: TBD

---

## E6: F04 Đơn hàng & phân bổ

### S6.1: Pipeline evaluate_lot_for_line — nguồn duy nhất của BR-ALLOC-ORDER (làm trước)

#### QA-6.1.6: Viết test case + chạy test ma trận thứ tự lớp loại của pipeline
Ma trận BR-ALLOC-ORDER: mỗi first_reason, lô trượt nhiều lớp, 4 nhánh lớp 4 với biên floor/deadline, 消費期限 = hôm nay, on_hold, qua get_allocation_candidates và allocate_lot.

- [ ] Mỗi first_reason có ít nhất 1 lô dữ liệu mẫu
- [ ] Lô trượt nhiều lớp: first_reason đúng thứ tự, other_reasons đủ
- [ ] Biên floor/deadline 4 nhánh lớp 4
- [ ] So khớp kết quả ứng viên và kết quả allocate_lot

**AC:**
- Bộ test case được review và lưu trong repo test
- Mọi case chạy pass hoặc lỗi được tạo issue có bước tái hiện

### S6.2: Danh sách đơn hàng và hủy đơn (SCR-040)

#### QA-6.2.4: Viết test case + chạy test SCR-040
Test lọc/phân trang/escape/biên ngày, hủy theo từng trạng thái + kiểm movement unallocate và yêu cầu expired, xung đột routed, RBAC 9 vai trò + API 403.

- [ ] Lọc, phân trang, escape ký tự đặc biệt, biên ngày
- [ ] Hủy theo 6 trạng thái, kiểm movement/qty_allocated/yêu cầu expired
- [ ] RBAC 9 vai trò, gọi API trực tiếp 403

**AC:**
- Bộ test case được review và lưu trong repo test
- Mọi case chạy pass hoặc lỗi được tạo issue có bước tái hiện

### S6.3: Đăng ký đơn hàng nhập tay (SCR-041)

#### QA-6.3.5: Viết test case + chạy test SCR-041
Test 3 nhánh hợp đồng (AGR-008/AGR-014, có rule, chưa có hợp đồng), biên qty/số dòng/ref/ngày JST, gửi lại cùng key, master ngưng dùng, RBAC vào thẳng URL.

- [ ] 3 nhánh hợp đồng
- [ ] qty 0/1/99999/100000, 50/51 dòng, ref hoa/thường, khác khách, ngày quá khứ JST
- [ ] Idempotency, master ngưng dùng giữa chừng, RBAC

**AC:**
- Bộ test case được review và lưu trong repo test
- Mọi case chạy pass hoặc lỗi được tạo issue có bước tái hiện

### S6.4: Phân bổ lô cho dòng đơn và gửi ngoại lệ 日付逆転 (SCR-042)

#### QA-6.4.8: Viết test case + chạy test SCR-042 (日付逆転, đồng thời, RBAC)
Test 日付逆転 (chặn, gửi yêu cầu, chưa có lịch sử, hạn bằng nhau, không mượn lịch sử CUS-003/CUS-004), đồng thời 2 người phân bổ, idempotency, hủy phân bổ, RBAC và chế độ chỉ xem.

- [ ] 日付逆転: các case CUS-003/CUS-004, upload lỗi không để lại yêu cầu
- [ ] Đồng thời 2 người phân bổ cùng lô, idempotency
- [ ] Hủy phân bổ + trạng thái đơn, lô on_hold hiển thị
- [ ] RBAC + đơn routed/shipped/cancelled chỉ xem

**AC:**
- Bộ test case được review và lưu trong repo test
- Mọi case chạy pass hoặc lỗi được tạo issue có bước tái hiện

### S6.5: Lịch sử giao theo khách (SCR-043)

#### QA-6.5.3: Viết test case + chạy test SCR-043
Test cờ mốc (trùng delivered_at, 1 lần xuất nhiều lô, lọc ngày + chỉ mốc), biên ngày JST, giới hạn 500, 移行データ, RBAC chỉ đọc + RLS chặn ghi delivery_history, hồi quy /api/customers, /api/skus.

- [ ] Cờ mốc các case trùng thời điểm, nhiều lô
- [ ] Biên ngày JST, giới hạn 500, dòng 移行データ
- [ ] RLS chặn ghi delivery_history; hồi quy màn dùng /api/customers, /api/skus

**AC:**
- Bộ test case được review và lưu trong repo test
- Mọi case chạy pass hoặc lỗi được tạo issue có bước tái hiện

### S6.6: Duyệt ngoại lệ 日付逆転 (SCR-044)

#### QA-6.6.8: Viết test case + chạy test SCR-044
Test state machine, tự duyệt, 6 lý do expire (gồm job PREVIOUS_CHANGED), RBAC 4 nhóm vai trò, xem bằng chứng ghi audit, đồng thời (2 manager; duyệt song song allocate_lot / cancel_order).

- [ ] State machine + 6 expire_reason
- [ ] Job 00:05: REQUESTED_DATE_PASSED và PREVIOUS_CHANGED
- [ ] Đồng thời 2 manager; duyệt vs allocate_lot/cancel_order
- [ ] RBAC 4 nhóm vai trò, audit evidence_viewed

**AC:**
- Bộ test case được review và lưu trong repo test
- Mọi case chạy pass hoặc lỗi được tạo issue có bước tái hiện

## E7: F05 Kiểm trước xuất

### S7.3: Màn hình quét, kiểm và xác nhận xuất

#### QA-7.3.1: Viết test case SCR-053: kiểm a–j, idempotency, xung đột bản tuyến
Test case cho 10 kiểm tra a–j (biên nhiệt độ, 消費期限 = hôm nay, 賞味期限 hôm qua), nhập tay có/không lý do, idempotency, deviation vẫn lưu khi bị chặn, M_22 và xuất khi tuyến có bản draft.

- [ ] Ma trận a–j × đạt/chặn
- [ ] Ca bấm 2 lần + mạng chập chờn
- [ ] Ca xe + hàng ngoài ngưỡng → 2 deviation
- [ ] Ca tuyến đổi sau công bố vẫn xuất theo bản published

**AC:**
- Mỗi kiểm a–j có ít nhất 1 ca đạt và 1 ca chặn
- Có ca cho 2 sửa thiết kế (giờ xuất phát, bản published)

#### QA-7.3.2: Chạy test SCR-053 trên máy quét giả lập và 2 nhóm vai trò
Chạy bộ test case SCR-053 với máy quét giả lập bàn phím, vai trò ghi (warehouse, warehouse_lead, admin) và chỉ xem; kiểm DB shipments/deviations/exception_events sau mỗi ca.

- [ ] Chạy đủ test case QA-7.3.1
- [ ] Kiểm dữ liệu DB sau ca bị chặn
- [ ] Ghi bug kèm bằng chứng
- [ ] Re-test bug đã sửa

**AC:**
- Báo cáo pass/fail cho toàn bộ ca
- Không còn bug mức cao mở

## E8: F07 Lập tuyến & công bố (phần không thuộc luật giờ lái)

### S8.4: Màn hình lập tuyến SCR-060

#### QA-8.4.1: Viết test case + chạy test SCR-060 (gán đơn, bản đồ, nháp)
Test case + chạy: 6 lý do không gán, biên 05:00/23:00, tải 90%/100%, đồng thời M_602/M_603/M_605, bản đồ timeout/cache/nhập tay/> 24h/ghi đè manual, khóa lạc quan, auditor chỉ đọc. Ca BR-DRV-21 thuộc E9.

- [ ] Viết ca theo 4 nhóm
- [ ] Chạy ca đồng thời bằng 2 trình duyệt
- [ ] Giả lập bản đồ lỗi
- [ ] Ghi bug + re-test

**AC:**
- Mỗi lý do 1–6 có ca riêng pass
- Báo cáo pass/fail đủ ca, không bug cao còn mở

### S8.5: Quản lý phiên bản tuyến, công bố và hủy (SCR-062)

#### QA-8.5.1: Viết test case + chạy test SCR-062 vòng đời phiên bản
Test case + chạy: đổi → nháp → bỏ / công bố lại (supersede), kho vẫn xuất khi có nháp, hủy tuyến (có/không đơn đã xuất), thông báo thất bại + retry, diff, auditor. Ca cổng BR-DRV-20/22/23 thuộc E9.

- [ ] Ca vòng đời đủ nhánh
- [ ] Ca hủy có đơn shipped
- [ ] Giả lập mail relay lỗi
- [ ] Ghi bug + re-test

**AC:**
- Mọi nhánh trạng thái route_versions có ca pass
- Không bug cao còn mở

