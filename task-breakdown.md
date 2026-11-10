# Task breakdown — Product B (Yuki Cold Logistics), LAB-5

Nguồn: bộ thiết kế LAB-4 (21 screen spec, 8 ADR, DB design, business rules) + các thay đổi ở [PREMISE.md](PREMISE.md).
Kết quả: **11 epic · 49 issue (story) · 219 sub-issue (task)**, trong đó **50 sub-issue thuộc ràng buộc giờ lái xe tải 2024**.
Dữ liệu gốc của backlog: [`output/breakdown/breakdown.json`](output/breakdown/breakdown.json); chi tiết từng task
(checklist, tiêu chí xong) theo vai trò: [`output/breakdown/breakdown-index.md`](output/breakdown/breakdown-index.md).

## 1. Nguyên tắc chia task

**Độ hạt — chia tới đâu thì dừng**
- Một sub-issue = **1 người, 1 vai trò, 1 kết quả kiểm chứng được**, cỡ **4–16 giờ**. Ước lượng thô lúc chia:
  S ≤ 4h · M ≤ 8h · L ≤ 16h. Task lớn hơn 16h thì tách tiếp, không có ngoại lệ.
- Dừng khi task đã nêu đúng **bảng / RPC / API / màn** cần làm và có tiêu chí xong đo được. Task dạng
  "làm màn SCR-061" hay "làm engine giờ lái" là quá mơ hồ, phải tách.
- Gộp ngược lại khi vụn: các việc cỡ S cùng màn, cùng vai trò gộp thành 1 task, miễn tổng không quá 16h.
- **Mỗi rule nghiệp vụ có hậu quả pháp lý là 1 task riêng** (mỗi rule BR-DRV, mỗi lớp loại trừ khi phân bổ), kể cả
  khi chỉ cỡ S. Gộp thì không review, test và ước lượng riêng từng rule được.

**Khi nào tách sub-issue**
- Story (issue) gom theo **1 màn hình** hoặc **1 năng lực dùng chung** (pipeline phân bổ, engine giờ lái, migration dùng chung).
- Trong story, tách sub-issue theo vai trò: BE (migration / RPC / API) · FE (UI) · QA (viết test case + chạy test,
  1 task/màn, màn lớn 2 task) · BrSE (làm rõ spec, tối đa 1 task/epic, riêng E9 nhiều hơn) · Infra · PM.
- RPC lớn chia theo bước, ví dụ `confirm_shipment` có 3 phần: kiểm điều kiện, gom lỗi, ghi sổ.

**Định nghĩa xong (DoD) cho một sub-issue**
1. Code merge vào `main` qua PR có ít nhất 1 người review; CI xanh (typecheck, lint, unit test).
2. RPC có test SQL (PGlite) cho nhánh lỗi và nhánh đồng thời (ADR-002). Rule BR-DRV có unit test các ca biên ghi trong task.
3. Message hiển thị qua mã `M_xx`, giao diện tiếng Nhật (G-21). Ngày giờ so sánh theo `app_today()` JST, hiển thị
   `YYYY/MM/DD HH:mm` JST (BR-TIME-01). Không xóa cứng dữ liệu nghiệp vụ; sửa sai bằng bút toán đảo hoặc phiên bản mới (BR-INV-03).
4. Đạt mọi tiêu chí trong mục "Acceptance criteria" của issue. QA đã chạy test case liên quan.
5. Thay đổi spec (nếu có) đã cập nhật lại tài liệu và ghi History of change.

**Cách dùng epic → issue → sub-issue trên GitHub Project**
- **Epic** = issue có label `epic`, tên `E9 ★ Ràng buộc giờ lái…`. **Issue** = story, gắn làm sub-issue của epic.
  **Sub-issue** = task, gắn làm sub-issue của story. Tiêu đề mở đầu bằng mã task (`BE-9.6.1 …`) để truy ngược về `breakdown.json`.
- Field của Project: `Status` (Todo / In progress / In review / Done) · `Iteration` · `Assignee` (người phụ trách giả định) ·
  `SWP` (điểm skill chấm, đã review) · `Estimate (h)` · `Role` · `Epic`.
- Label: vai trò (`be`, `fe`, `qa`…), `special-constraint` cho mọi task E9, `clarification` cho task BrSE làm rõ.
- Phụ thuộc (`depends_on` trong JSON) ghi thành dòng "Blocked by #…" trong thân issue. Hai chuỗi phải làm trước:
  pipeline phân bổ (S6.1) và khung engine + lắp dữ liệu (S9.2).

## 2. Spec → issue

| Spec | Epic | Issue / sub-issue | Phần spec chưa thành issue và vì sao |
|---|---|---|---|
| `prototype-vs-design-gap.md` G-01…G-03, G-10, G-15…G-17, G-21…G-23; ADR-001/002/003/007; architecture §6–7; BR-INV-03, BR-TIME-01 | E1 Nền tảng & sửa prototype | S1.1 migration dùng chung (BE-1.1.1–3; chặn xóa cứng ở BE-1.1.2) · S1.2 M_xx + tiếng Nhật (BE-1.2.1, FE-1.2.2) · S1.3 9 vai trò, tách lập/duyệt (BE-1.3.1–2, FE-1.3.3) · S1.4 ngưỡng nhiệt có phiên bản (BE-1.4.1–2) · S1.5 hạ tầng Tokyo, CI, phân trang (INFRA-1.5.1–2, BE-1.5.3, FE-1.5.4) | G-04, G-05, G-11–G-13, G-24 nằm ở epic nghiệp vụ tương ứng (E6, E7). G-18 master nhà cung cấp chỉ làm bảng, chưa có màn (PREMISE LAB-4 §4) |
| SCR-001 | E2 F12 | S2.1 (INFRA-2.1.1, BE-2.1.2–4, FE-2.1.5–6, QA-2.1.7) | — |
| SCR-002 | E2 F12 + E9 | S2.2 (BE-2.2.1–3, FE-2.2.4, QA-2.2.5); thẻ giờ lái ở S9.12 | Thẻ 「承認待ち」 và thẻ năm 3.300h/960h: spec không định nghĩa, chưa thêm |
| SCR-018 | E2 F12 | S2.3 (BE-2.3.1–2, FE-2.3.3–4, QA-2.3.5, BRSE-2.3.6) | Vai trò `driver`: là thực thể `drivers`, không phải vai trò app → không có task |
| SCR-010 | E3 F01 | S3.1 (BE-3.1.1–2, FE-3.1.3–4, QA-3.1.5) | Vòng duyệt master SKU (RFP S3-01, SCR-017) hoãn theo Q&A-B11 → hỏi khách ở BRSE-10.1.2 |
| SCR-011 | E3 F01 | S3.2 khách hàng (BE-3.2.1, FE-3.2.2) · S3.3 hợp đồng khách–SKU (BE-3.3.1–4, FE-3.3.5–6, QA-3.3.7) | — |
| SCR-015 | E3 F01 | S3.4 (BE-3.4.1–3, FE-3.4.4–5, QA-3.4.6, BRSE-3.4.7) | Đếm số giao dịch dùng phiên bản (link usage): để giai đoạn sau |
| SCR-022, BR-INV-04 | E4 F02 | S4.1 phiếu nhập (BE-4.1.1–3, FE-4.1.4–6) · S4.2 kiểm nhiệt 2 lớp + idempotent (BE-4.2.1–2, FE-4.2.3, QA-4.2.4, BRSE-4.2.5) | Kiểm sức chứa vị trí (FR-INV-01): ngoài phạm vi Phase 1 |
| SCR-030 | E5 F03 | S5.1 (BE-5.1.1–2, FE-5.1.3, QA-5.1.4) | — |
| SCR-031 | E5 F03 | S5.2 (BE-5.2.1–2, INFRA-5.2.3, FE-5.2.4–5, QA-5.2.6) | Màn di chuyển lô sang khu -Q và màn chi tiết deviation F08: chưa có spec (Phase 2) |
| SCR-037 | E5 F03 | S5.3 (BE-5.3.1–4, FE-5.3.5–7, QA-5.3.8, BRSE-5.3.9) | Hủy một phần lô: cần tách lô, chưa thiết kế; Phase 1 chỉ hủy cả lô |
| ADR-004, BR-ALLOC-ORDER | E6 F04 | S6.1 pipeline `evaluate_lot_for_line` (BE-6.1.1–5, QA-6.1.6, BRSE-6.1.7) | — |
| SCR-040 | E6 F04 | S6.2 (BE-6.2.1–2, FE-6.2.3, QA-6.2.4) | — |
| SCR-041 | E6 F04 | S6.3 (BE-6.3.1–2, FE-6.3.3–4, QA-6.3.5) | Nhập đơn từ file ERP (FN-0402, IF-ERP-01): Phase 2 |
| SCR-042 | E6 F04 | S6.4 (BE-6.4.1–3, FE-6.4.4–7, QA-6.4.8) | — |
| SCR-043 | E6 F04 | S6.5 (BE-6.5.1, FE-6.5.2, QA-6.5.3) | Xuất CSV lịch sử giao: spec không có |
| SCR-044, ADR-005 | E6 F04 | S6.6 (BE-6.6.1, INFRA-6.6.2, BE-6.6.3–5, FE-6.6.6–7, QA-6.6.8) | Thông báo kết quả duyệt cho người gửi: chưa thiết kế → câu hỏi trong BRSE-6.1.7 |
| SCR-053, ADR-008, BR-OUT-01…03 | E7 F05 | S7.1 RPC `confirm_shipment` (BE-7.1.1–5; BR-OUT-01/02 ở BE-7.1.4, BR-OUT-03 ở BE-7.1.5) · S7.2 API (BE-7.2.1–3) · S7.3 màn quét/kiểm (FE-7.3.1–4, QA-7.3.1–2, BRSE-7.3.1) | Link sang màn deviation F08: Phase 2 |
| SCR-060 (phần lập tuyến), G-14, DB-001 §3.2, IF-MAP-01, IF-MAIL-01 | E8 F07 | S8.1 dữ liệu + quyền F07 (BE-8.1.1–3) · S8.2 gán đơn, điểm dừng, segment (BE-8.2.1–4) · S8.3 bản đồ + mail (BE-8.3.1–2, INFRA-8.3.1–2) · S8.4 màn SCR-060 (FE-8.4.1–4, QA-8.4.1) | Chèn nghỉ BR-DRV-21 chuyển sang E9 (S9.6) |
| SCR-062 (phần vòng đời phiên bản) | E8 F07 | S8.5 (BE-8.5.1–4, FE-8.5.1–2, QA-8.5.1, BRSE-8.5.1) | Cổng tuân thủ khi công bố chuyển sang E9 (BE-9.8.3). Chuyển tay `in_progress/completed` trước F06: để mở (A5-08) |
| SCR-016, ADR-003 | E9 | S9.1 (BE-9.1.1–4, FE-9.1.5–6, QA-9.1.7) | — |
| SCR-061, ADR-006, G-14 (phần giờ lái), BR-DRV-01…14, 20, 22, 23 | E9 | S9.2–S9.5, S9.7–S9.9 (xem mục 3) | Điều kiện phụ 労使協定: chờ Q&A-B07 (A5-05) |
| SCR-060 §logic-11, BR-DRV-21 | E9 | S9.6 (BE-9.6.1–2, QA-9.6.3) | — |
| SCR-063, BR-DRV-24/25 | E9 | S9.10 (BE-9.10.1, INFRA-9.10.2, BE-9.10.3–6, FE-9.10.7–8, QA-9.10.9) | Sự cố sai → bản mới tham chiếu bản cũ (`supersedes_event_id`); chỉ có 1 `transport_manager` thì không ai duyệt: để mở, hỏi ở BRSE-9.13.2 |
| PREMISE P-01 (SCR-064 mới) | E9 | S9.11 (BRSE-9.11.1, BE-9.11.2, FE-9.11.3, QA-9.11.4) | — |
| business-rules §8 Q&A-B01…B17 | E10 + E9 | S10.1 (BRSE-10.1.1–3); Q&A-B06/B07 ở S9.13 (PM-9.13.1, BRSE-9.13.2) | — |
| Ghi chú spec lỗi thời, enum lệch DB | E10 | S10.2 (BRSE-10.2.1, BE-10.2.2) | — |
| architecture §5, §7; ADR-004/006 §5 (fixture R-06); `prototype-vs-design-gap.md` K-01…K-08 | E11 | S11.1 tích hợp (QA-11.1.1–2; hồi quy K-01…K-08 ở QA-11.1.1) · S11.2 UAT (QA-11.2.1, BRSE-11.2.2) · S11.3 sprint + phát hành (PM-11.3.1–2, INFRA-11.3.3) | — |
| F06, F08, F09, F10, F11, F13 | — | — | Phase 2: LAB-4 chỉ thiết kế tới mức kiến trúc, không có screen spec (PREMISE LAB-4 §2) |

## 3. Hạng mục chịu ràng buộc đặc thù của đề — giới hạn giờ lái xe tải từ 2024

Toàn bộ nằm trong **epic E9**, mang label `special-constraint`, tiêu đề có tiền tố `[DRV]`. Mỗi rule là một sub-issue riêng, kèm
giới hạn, mức (vi phạm / cảnh báo), cách xác định khoảng giờ vi phạm theo SCR-061 §logic-9 và ca biên trong tiêu chí xong.

| Ràng buộc | Issue | Vì sao tách riêng |
|---|---|---|
| Tham số luật có phiên bản (BR-DRV-22, ADR-003) | S9.1: BE-9.1.1–4, FE-9.1.5–6, QA-9.1.7 | Luật còn đổi (RFP tự ghi "cần kiểm lại nguồn") → tham số phải là dữ liệu có ngày hiệu lực. Đã sửa thiếu 2 tham số (P-02) |
| Khung engine, lắp dữ liệu thực tế + kế hoạch, hash | S9.2: BE-9.2.1, BE-9.2.2, BE-9.2.3 | Mọi rule dùng chung nguồn dữ liệu; làm sai ở đây thì mọi rule sai theo. Phải làm trước |
| BR-DRV-04/05 ràng buộc/ngày 13h cảnh báo, 15h vi phạm | BE-9.3.1 | "Ngày" = 24h từ 始業, chồng sang ngày trước, khác cách cộng giờ làm hiện tại của khách (PP-04) |
| BR-DRV-06 > 14h quá 2 ngày/tuần | BE-9.3.2 | Rule INFERRED (改善基準告示), có thể bị khách bỏ → tách để bật/tắt |
| BR-DRV-07/08 nghỉ giữa ca 11h / 9h | BE-9.4.1 | Cần dữ liệu ca trước (thực tế) → phụ thuộc SCR-064 |
| BR-DRV-09 lái TB 2 ngày 9h | BE-9.5.1 | Cách đọc "cả avg(D−1,D) và avg(D,D+1)" từng bị viết sai ở LAB-4 → cần test riêng |
| BR-DRV-10 lái TB 2 tuần 44h | BE-9.5.2 | Khối 2 tuần cố định từ ngày khởi điểm (P-02), không phải cửa sổ trượt |
| BR-DRV-11 lái liên tục 4h (nghỉ ≥ 10 phút, tổng ≥ 30 phút) | BE-9.6.1 | Thuật toán phức tạp nhất; một module dùng chung cho kiểm và chèn nghỉ (P-04) |
| BR-DRV-21 tự chèn nghỉ 30 phút khi lập tuyến | BE-9.6.2, QA-9.6.3 | Làm thay đổi giờ đến các điểm sau → ảnh hưởng SCR-060 và khung giờ giao của khách |
| BR-DRV-01 tăng ca 960h/năm | BE-9.7.1 | Công thức tăng ca còn chờ khách xác nhận (A5-04) → effort có buffer riêng |
| BR-DRV-02 3.300h/năm · BR-DRV-03 284h/tháng | BE-9.7.2, BE-9.7.3 | Cửa sổ năm tài chính / tháng JST khác nhau |
| BR-DRV-14 gia hạn 労使協定 3.400h/310h | BE-9.7.4 | Mặc định tắt, chỉ bật khi khách xác nhận (Q&A-B07) |
| BR-DRV-20/22/23 kết quả bất biến, xác nhận cảnh báo, chặn công bố | S9.8: BE-9.8.1–4 | Đây là cổng chặn: tuyến vi phạm không được công bố; kết quả là bằng chứng kiểm toán |
| Màn timeline + vi phạm SCR-061 | S9.9: BE-9.9.1, FE-9.9.2–4, QA-9.9.5–6 | Phải chỉ đúng khoảng giờ vi phạm (FR-SCH-02); test theo từng rule với seed R-06 |
| BR-DRV-24/25 sự cố bất khả kháng, báo cáo riêng, vượt kế hoạch | S9.10: BE-9.10.1, INFRA-9.10.2, BE-9.10.3–6, FE-9.10.7–8, QA-9.10.9 | Chỉ loại 04/05, 09, 11 khỏi báo cáo lịch thường; các giới hạn tháng/năm/nghỉ vẫn tính đủ |
| Nhập giờ làm thực tế (màn mới SCR-064) | S9.11: BRSE-9.11.1, BE-9.11.2, FE-9.11.3, QA-9.11.4 | Không có thì engine tính sai tháng/năm/nghỉ (P-01) |
| Cảnh báo trên trang chủ (tài xế ≥ 90% 284h, tuyến vi phạm) | S9.12: BE-9.12.1, FE-9.12.2, QA-9.12.3 | Dùng chung hàm chọn dữ liệu với engine, tránh 2 con số khác nhau (P-07) |
| Xác nhận pháp lý, Q&A giờ lái | S9.13: PM-9.13.1, BRSE-9.13.2 | Bảng BR-DRV một phần là INFERRED; chốt sai là rủi ro pháp lý cho khách |

**Ảnh hưởng tới ước lượng:** E9 chiếm 50/219 sub-issue và khoảng 20% giờ trần (520/2.560h). Riêng phần kiểm rule
(S9.3–S9.7) là 12 task, đều có unit test biên (4h00 đạt / 4h01 vi phạm; nghỉ 9 phút không tính; 3 lần × 10 phút reset khối;
13h00 / 15h00 đúng biên). Ở LAB-1, F07 chỉ được ước lượng chung là "điều phối tuyến" (xem `estimate.md`).

## 4. Chỗ hở hoặc mâu thuẫn của spec LAB-4 phát hiện khi break

| Spec | Chỗ hở / mâu thuẫn | Xử lý |
|---|---|---|
| ADR-006 §5, SCR-061 §logic-5 | Engine cần giờ thực tế nhưng không có màn nhập | Đã sửa thiết kế → PREMISE P-01 |
| SCR-016 §5 item 9.2 vs DB-001 §3.2 | Thiếu tham số `long_day_threshold_h`, `drive_2week_anchor_date` | Đã sửa thiết kế → PREMISE P-02 |
| SCR-062 §logic-12 vs SCR-053 §9 bước 4 | Đổi tuyến sau công bố làm kho không xuất được | Đã sửa thiết kế → PREMISE P-03 |
| SCR-060 §logic-11 vs ADR-006 §3 | Thuật toán chuỗi lái có ở 2 nơi (SQL + TS) | Đã sửa thiết kế → PREMISE P-04 |
| SCR-061 §9 vs SCR-062 §logic-5 | Hash đầu vào cài 2 lần | Đã sửa thiết kế → PREMISE P-05 |
| SCR-063 §logic-6 | Báo cáo là hàm SQL nhưng phải gọi engine TS | Đã sửa thiết kế → PREMISE P-06 |
| SCR-062 §logic-5 bước 3.8 | Duty record của bản `superseded` không được lọc → cộng trùng giờ | Đã sửa thiết kế → PREMISE P-07 |
| SCR-053 §logic-10-4 vs SCR-060 §logic-6-5 | Giờ xuất phát lấy nhầm 始業 | Đã sửa thiết kế → PREMISE P-08 |
| SCR-042 §5 item 8-2 / 5.5-2 / 13.9-4 | Thiếu lô `on_hold`; đọc có ghi; rollback Storage không được | Đã sửa thiết kế → PREMISE P-09 |
| SCR-044 §9 job vs BR-DATE-02 | Job hết hạn thiếu `PREVIOUS_CHANGED` | Đã sửa thiết kế → PREMISE P-10 |
| SCR-062 §logic-7 | Hủy tuyến không xử lý đơn đã xuất | Đã sửa thiết kế → PREMISE P-11 |
| SCR-022/031/037/060 vs DB-001 | Enum `deviation_type`, `event_type`, `segment_type` lệch; thiếu chỗ lưu tham số hệ thống | Đã sửa thiết kế → PREMISE P-12 |
| SCR-015 §9 | Cơ chế bỏ qua trigger khi seed không định nghĩa (lỗ bảo mật) | Đã sửa thiết kế → PREMISE P-13 |
| SCR-001 item 2-6 vs SCR-002 item 4-16 | Callback không cập nhật `mfa_verified_at` | Đã sửa thiết kế → PREMISE P-14 |
| SCR-060 §logic-6-4 | 1 tài xế 1 tuyến/ngày là INFERRED | Giả định → PREMISE A5-01 |
| SCR-063 §logic-6 | BR-DRV-11 trên dữ liệu thực tế không có segment | Giả định → PREMISE A5-02 |
| SCR-061 §logic-5 bước 2.2 | Ngày trống = 0h im lặng có thể làm lọt vi phạm | Giả định → PREMISE A5-03 |
| BR §7, Q&A-B06 | Công thức tăng ca, phạm vi loại sự cố chưa chốt | Giả định → PREMISE A5-04 + tạo issue làm rõ PM-9.13.1 |
| SCR-061 §logic-9 BR-DRV-14 | Điều kiện phụ 労使協定 chưa thiết kế | Giả định → PREMISE A5-05 + tạo issue làm rõ BRSE-9.13.2 |
| SCR-030 §7 (FR-INV-06) | Thiết kế 1 kho trong khi Product B là chuỗi kho | Giả định → PREMISE A5-06 + tạo issue làm rõ BRSE-5.3.9 |
| SCR-053 §logic-11-6 | Định dạng mã vạch chưa có trong RFP | Giả định → PREMISE A5-07 + tạo issue làm rõ BRSE-7.3.1 |
| SCR-062 §3 | Trước F06, tuyến kẹt ở `published` | Để mở → PREMISE A5-08: cần khách quyết định có làm nút chuyển tay không; hỏi ở BRSE-8.5.1 |
| SCR-010 §7 vs RFP S3-01 | Không có vòng duyệt master SKU | Tạo issue làm rõ BRSE-10.1.2 |
| SCR-001 item 7-2 | M_104 không có nhánh nào sinh ra | Tạo issue làm rõ BRSE-2.3.6 |
| SCR-011 item 18-14 | Job 00:05 đổi trạng thái dòng đơn là INFERRED, không có trong ADR | Tạo issue làm rõ BRSE-3.4.7 |
| SCR-010 item 2 vs SCR-011 item 1-2 | Điều hướng master: tab chung hay menu trái | Đã sửa thiết kế trong task FE-3.1.3 (chọn 1 cách cho cả nhóm `/master/*`) |
| SCR-063 vs business-rules sm-unforeseeable | "Sai → tạo bản mới tham chiếu bản cũ" nhưng không có cột tham chiếu | Để mở: chưa đủ chắc để thêm cột; hỏi ở BRSE-9.13.2 |
| Nhiều spec (SCR-010/016/018/037/040/041/043/062) | Ghi "chưa có trong database-design" đã lỗi thời | Tạo issue làm rõ BRSE-10.2.1 (rà đồng bộ) |
