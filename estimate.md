# Estimate — Product B (Yuki Cold Logistics), LAB-5

**Báo cáo HTML của skill chấm SWP:** [`reports/sun-estimate-lab5-product-b-backlog-261111.html`](reports/sun-estimate-lab5-product-b-backlog-261111.html)
(skill `/tkm:sun-estimate`, mô hình `swp-matrix-v2`, chạy ngày 2026/11/11, trạng thái hiệu chỉnh `accepted`).
Mở file sau khi tải repo về, hoặc xem bản trên GitHub qua nút *Raw* → lưu `.html` → mở bằng trình duyệt (file tự chứa, không gọi mạng).

Kết quả: **219 sub-issue · 997 SWP · 1.994 giờ**. Epic và issue (story) không chấm riêng; SWP của chúng là tổng các sub-issue con,
không tra lại ma trận. Số SWP và giờ đã ghi vào field `SWP` và `Estimate (h)` của cả 279 item trên
[GitHub Project](https://github.com/users/linhnn-22575/projects/1). Bảng nguồn: [`output/estimate/swp-by-issue.json`](output/estimate/swp-by-issue.json).

## 1. Issue mẫu skill chọn để kiểm

Skill chọn 5 issue theo luật cố định (nhỏ nhất, trung vị, lớn nhất, xa trung vị nhất, độ tin cậy thấp nhất). Tôi duyệt từng issue:
chọn mức khó trước, rồi chọn điểm cụ thể trong mức đó.

| Issue | Skill chấm (Scope × Complexity → SWP) | Bạn chốt | Lý do |
|---|---|---|---|
| [#156](https://github.com/linhnn-22575/lab5-product-b-backlog/issues/156) BE-7.2.1 Sửa giờ xuất phát = `planned_arrival + service_min` | 1 × 1 → **1** (rất dễ) · lý do skill: issue nhỏ nhất | **1** — giữ | Một hàm SQL `route_departure_time` + unit test. Công thức đã chốt ở [PREMISE P-08](PREMISE.md), không còn quyết định thiết kế nào |
| [#66](https://github.com/linhnn-22575/lab5-product-b-backlog/issues/66) FE-3.4.5 Dialog tạo/sửa phiên bản ngưỡng nhiệt có xem trước | 3 × 2 → **5** (dễ) · trung vị | **5** — giữ | Dialog 3 khối (form, preview, trục số). Khó ở preview debounce, trạng thái 計算中/lỗi và xung đột 409 `M_164`. Đúng mức một màn form có trạng thái |
| [#4](https://github.com/linhnn-22575/lab5-product-b-backlog/issues/4) BE-1.1.2 Tạo `inventory_movements`, `lot_status_events`, enum trạng thái | 5 × 3 → **10** (vừa) · lớn nhất | **10** — giữ | Migration có chuyển dữ liệu prototype, số dư sau migrate phải khớp `qty_on_hand`, sổ append-only + chặn DELETE (ADR-007). Đây là task nặng nhất backlog nên 10 hợp lý; không tách vì migration phải chạy trong 1 transaction |
| [#212](https://github.com/linhnn-22575/lab5-product-b-backlog/issues/212) BE-9.3.2 [DRV] Rule BR-DRV-06 số ngày ràng buộc > 14h trong tuần | 1 × 1 → **1** (rất dễ) · xa trung vị nhất | **1** — giữ | Rule chỉ đếm ngày trên kết quả 拘束 đã tính ở BE-9.3.1 ([#211](https://github.com/linhnn-22575/lab5-product-b-backlog/issues/211)), ngưỡng đọc từ `driver_rule_versions`. Unit test biên đã nằm trong DoD; test case theo từng rule do QA viết riêng ở QA-9.9.5 ([#237](https://github.com/linhnn-22575/lab5-product-b-backlog/issues/237)) |
| [#42](https://github.com/linhnn-22575/lab5-product-b-backlog/issues/42) BRSE-2.3.6 Xác nhận với khách các điểm INFERRED của xác thực, trang chủ | 2 × 1 → **3** (dễ) · độ tin cậy thấp nhất | **3** — giữ | Khoảng 8 câu hỏi của 3 spec (SCR-001/002/018). Độ tin cậy thấp chỉ vì rubric không có nhóm discipline cho việc BrSE, không phải vì thiếu thông tin |

Không sửa issue nào. Lý do giữ nguyên: cả 5 issue đều ghi rõ bảng/RPC/màn cần làm, và hai trục skill chấm khớp với cỡ S/M/L
đã ước khi chia task (task cỡ M trung bình 4,0 SWP, cỡ L trung bình 5,4 SWP). Vì không có chỉnh sửa nên không có luật hiệu chỉnh
nào lan sang issue khác. Điểm đáng chú ý khi review: các rule BR-DRV đơn lẻ được chấm 1–2 SWP là thấp so với hậu quả pháp lý,
nhưng hợp lý vì test case theo từng rule có task QA riêng (QA-9.9.5) và phần khó (module chuỗi lái, lắp dữ liệu, kết quả bất biến) đã tách thành task riêng
có điểm cao hơn (BE-9.6.1, BE-9.2.x, BE-9.8.x).

## 2. Cách quy ra giờ

- **Cách chọn:** quy ước đổi SWP ra giờ, **1 SWP = 2 giờ**, áp dụng cho mọi sub-issue. Không ước giờ trực tiếp từng issue.
- **Vì sao:** SWP do skill chấm theo một ma trận cố định, cùng mô tả cho cùng điểm. Ước giờ tay từng issue sẽ lẫn cảm tính của từng người
  và không so được giữa các vai trò. Một hệ số duy nhất giữ được thứ tự lớn/nhỏ của skill và dễ hiệu chỉnh sau sprint 1.
- **Hệ số 2 lấy từ đâu:** đối chiếu với cỡ đã ước khi chia task (trần S = 4h, M = 8h, L = 16h).
  - Task cỡ M trung bình 4,02 SWP → 8,0h, đúng bằng trần M.
  - Task cỡ L trung bình 5,43 SWP → 10,9h, dưới trần 16h.
  - Task cỡ S trung bình 2,21 SWP → 4,4h, sát trần 4h.
  - Tổng 997 SWP → 1.994h, bằng 78% tổng giờ trần 2.560h. Trần là mức tối đa nên tổng thực tế thấp hơn là đúng hướng.
- **Quy tắc áp dụng nhất quán:**
  1. Sub-issue: `Estimate (h) = SWP × 2`, số nguyên, không làm tròn thêm, không cộng buffer vào từng issue.
  2. Issue (story) và epic: `SWP` và `Estimate (h)` = tổng của sub-issue con. Không tra lại ma trận, không thêm giờ quản lý.
  3. Giờ là thời gian một người làm xong sub-issue theo DoD (gồm tự test, PR, sửa theo review). Họp, quản lý dự án và buffer rủi ro
     không nằm trong giờ của issue; rủi ro trễ theo dõi ở [progress-report.md](progress-report.md).
  4. Sau mỗi sprint, so SWP đã xong với giờ thực tế để chỉnh hệ số cho cả backlog (không sửa điểm từng issue). Sprint 1 giả lập
     cho tốc độ thực tế thấp hơn kế hoạch (2,5h/SWP); xem [progress-report.md](progress-report.md) §2 và rủi ro ở §3.

## 3. Tổng theo epic

| Epic | Số issue (story / sub-issue) | Tổng SWP | Tổng giờ | Ghi chú |
|---|---|---:|---:|---|
| [#1](https://github.com/linhnn-22575/lab5-product-b-backlog/issues/1) E1 Nền tảng & sửa prototype trái RFP | 5 / 14 | 71 | 142 | Task lớn nhất backlog (#4, 10 SWP) nằm ở đây. Là nền cho mọi epic khác |
| [#21](https://github.com/linhnn-22575/lab5-product-b-backlog/issues/21) E2 F12 Xác thực & phân quyền | 3 / 18 | 89 | 178 | SCR-001/002/018; MFA callback theo [P-14](PREMISE.md) |
| [#43](https://github.com/linhnn-22575/lab5-product-b-backlog/issues/43) E3 F01 Master & chính sách nhiệt | 4 / 21 | 104 | 208 | Ngưỡng nhiệt có phiên bản (ADR-003) |
| [#69](https://github.com/linhnn-22575/lab5-product-b-backlog/issues/69) E4 F02 Nhập hàng | 2 / 11 | 51 | 102 | Kiểm nhiệt 2 lớp + idempotent (ADR-008) |
| [#83](https://github.com/linhnn-22575/lab5-product-b-backlog/issues/83) E5 F03 Tồn kho & lô | 3 / 19 | 92 | 184 | |
| [#106](https://github.com/linhnn-22575/lab5-product-b-backlog/issues/106) E6 F04 Đơn hàng & phân bổ | 6 / 35 | 157 | 314 | Pipeline phân bổ S6.1 là đường găng; 3 sửa ở SCR-042 theo [P-09](PREMISE.md) |
| [#148](https://github.com/linhnn-22575/lab5-product-b-backlog/issues/148) E7 F05 Kiểm trước xuất | 3 / 15 | 57 | 114 | Giờ xuất phát theo [P-08](PREMISE.md) |
| [#167](https://github.com/linhnn-22575/lab5-product-b-backlog/issues/167) E8 F07 Lập tuyến & công bố (phần không thuộc luật) | 5 / 24 | 118 | 236 | Tuyến giữ `published` khi đổi ([P-03](PREMISE.md)) |
| [#197](https://github.com/linhnn-22575/lab5-product-b-backlog/issues/197) **E9 ★ Ràng buộc giờ lái xe tải 2024** | 13 / 50 | **210** | **420** | **Ràng buộc đặc thù của đề**, nhãn `special-constraint`. Epic lớn nhất: 21% SWP. Gồm màn mới SCR-064 ([P-01](PREMISE.md), 18 SWP) |
| [#261](https://github.com/linhnn-22575/lab5-product-b-backlog/issues/261) E10 Làm rõ spec & Q&A khách (BrSE) | 2 / 5 | 12 | 24 | |
| [#269](https://github.com/linhnn-22575/lab5-product-b-backlog/issues/269) E11 Kiểm thử tích hợp, UAT & quản lý dự án | 3 / 7 | 36 | 72 | Chỉ các sản phẩm cụ thể (kịch bản test, UAT, runbook, báo cáo); không gồm công quản lý hằng ngày |
| **Tổng** | **49 / 219** | **997** | **1.994** | |

Phân bổ E9 theo vai trò: BE 118 SWP · QA 42 · FE 40 · BrSE 6 · Infra 3 · PM 1. Tỉ lệ QA trong E9 (20%) cao hơn mức chung (17%)
vì mỗi màn giờ lái có task QA riêng, thêm task test case theo từng rule (QA-9.9.5) và test biên lái liên tục (QA-9.6.3, [#221](https://github.com/linhnn-22575/lab5-product-b-backlog/issues/221)) theo ca mẫu ADR-006 §5.

## 4. So với estimate LAB-1

LAB-1 ước theo người-ngày (MD) cho cả gói cơ bản S3-05 (1.516 MD), đã gồm buffer 20% và giảm 15% nhờ AI. Để so, đổi MD ra giờ
bằng 1 MD = 8h.

| Phần (chức năng / epic) | LAB-1 | LAB-5 | Chênh | Vì sao |
|---|---:|---:|---:|---|
| Nền tảng, hạ tầng, NFR → E1 | 115 MD = 920h | 142h | −778h | LAB-1 ước hạ tầng/NFR như hạng mục độc lập (42 + 35 MD). Ở LAB-5 kiến trúc đã chốt ở LAB-4 (Vercel + Supabase Tokyo, ADR-001), phần còn lại chỉ là cấu hình và migration dùng chung; việc infra khác nằm rải trong epic (INFRA-2.1.1, 5.2.3, 11.3.3) |
| F12 Xác thực & phân quyền → E2 | 50 MD = 400h | 178h | −222h | Dùng Supabase Auth sẵn có; 9 vai trò đã có ma trận quyền ở LAB-4 nên không còn phân tích |
| F01 Master → E3 | 72 MD = 576h | 208h | −368h | Vòng duyệt SKU master (SCR-017) hoãn chờ khách trả lời ([#264](https://github.com/linhnn-22575/lab5-product-b-backlog/issues/264)) |
| F02 Nhập hàng → E4 | 67 MD = 536h | 102h | −434h | Phase 1 bỏ nhập từ file và kiểm sức chứa vị trí (LAB-4 PREMISE §3); còn 1 màn SCR-022 |
| F03 Tồn kho & lô → E5 | 75 MD = 600h | 184h | −416h | Màn di chuyển lô sang khu -Q và chi tiết deviation chưa có spec (Phase 2) |
| F04 Đơn & phân bổ → E6 | 79 MD = 632h | 314h | −318h | Chênh ít nhất trong nhóm chức năng: pipeline phân bổ vẫn là khối khó, LAB-5 còn thêm 3 sửa ở SCR-042 ([P-09](PREMISE.md)) và PREVIOUS_CHANGED ([P-10](PREMISE.md)) |
| F05 Xuất hàng → E7 | 40 MD = 320h | 114h | −206h | Phase 1 chỉ có kiểm trước xuất SCR-053; lấy hàng/xếp xe chưa làm |
| F07 phần lập tuyến (FN-0701/0702/0705) → E8 | 39 MD = 312h | 236h | −76h | Gần nhau: thêm việc giữ tuyến `published` khi đổi ([P-03](PREMISE.md)) và chặn hủy tuyến có đơn đã xuất ([P-11](PREMISE.md)) bù lại phần đã thiết kế xong |
| **F07 giờ lái 2024 (FN-0703/0704/0706) → E9** | 42 MD = 336h | **420h** | **+84h** | **Phần duy nhất LAB-5 cao hơn LAB-1.** Detail design cho thấy việc nhiều hơn lúc ước: thêm màn SCR-064 nhập giờ thực tế ([P-01](PREMISE.md), 36h); SCR-016 thêm 2 tham số ([P-02](PREMISE.md)); module chuỗi lái dùng chung ([P-04](PREMISE.md)) và hash dùng chung ([P-05](PREMISE.md)); kết quả bất biến + cổng công bố (ADR-006); mỗi rule BR-DRV một task + test biên riêng |
| Phân tích, PM & BrSE (nhóm 0 và 21) → E10 + phần PM/BrSE của E11 | 333 MD = 2.664h | 34h | −2.630h | Phân tích đã làm ở LAB-1→4. Công quản lý hằng ngày không thành issue (quy tắc 3 ở §2); backlog chỉ giữ việc có sản phẩm cụ thể |
| Thiết kế UI | 74 MD = 592h | 0h | −592h | Wireframe và spec màn hình đã xong ở LAB-4; giờ dựng UI nằm trong task FE |
| Test tự động + tích hợp/UAT → QA/BrSE của E11 | 93 MD = 744h | 50h | −694h | Không có vai trò QA Auto trong team LAB-5; test chức năng nằm trong task QA từng màn (174 SWP = 348h); E11 chỉ còn kịch bản xuyên màn và UAT |
| Đào tạo, go-live & hypercare | 58 MD = 464h | 12h | −452h | Chỉ có runbook phát hành (INFRA-11.3.3); đào tạo và hypercare chưa đưa vào Phase 1 backlog |
| F06, F08, F09, F10, F11, F13 | 379 MD = 3.032h | 0h | −3.032h | Hoãn Phase 2 theo LAB-4 PREMISE §2 (cần thiết bị/dữ liệu ngoài, khớp lộ trình upsale LAB-3) |
| **Tổng** | **1.516 MD = 12.128h** | **1.994h** | **−10.134h** | 66% phần chênh (6.706h) do phạm vi Phase 2 và các hạng mục không thành issue (PM/BrSE, thiết kế UI, đào tạo); phần còn lại do LAB-5 ước sau khi có detail design |

Đọc bảng này cần lưu ý ba điểm:

1. Hai con số khác bản chất. LAB-1 là estimate đấu thầu khi chưa có thiết kế: có buffer 20%, hệ số độ phức tạp và kinh nghiệm,
   cộng toàn bộ công quản lý. LAB-5 là giờ thực thi từng sub-issue sau khi thiết kế đã xong, không buffer. Không nên dùng 1.994h
   để báo giá.
2. Ở cùng một chức năng, LAB-5 thấp hơn LAB-1 khoảng 2–5 lần, trừ F07. Lý do chính: phần phân tích và quyết định kỹ thuật đã tiêu ở
   LAB-1→4. Nếu sprint 1 cho thấy hệ số 2h/SWP quá lạc quan (bản giả lập: thực tế cần khoảng 2,5h/SWP), tổng Phase 1 lên khoảng 2.500h.
3. F07 giờ lái đi ngược chiều: càng chi tiết càng thấy thêm việc. Đây là bằng chứng cho yêu cầu của đề — ràng buộc giờ lái 2024
   làm tăng effort và phải tách riêng thành epic E9 để theo dõi.
