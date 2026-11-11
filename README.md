# LAB-5 — Backlog, estimate và báo cáo tiến độ Product B (Yuki Cold Logistics)

- **Học viên:** Ngô Ngọc Linh
- **Đề:** Product B — chuỗi kho lạnh thực phẩm. Ràng buộc đặc thù: giới hạn giờ lái xe tải từ 2024 (改善基準告示).

## 1. Tổng quan

- **Nguồn:** backlog break từ bộ thiết kế **LAB-4 nộp ngày 2026/11/08** (thư mục `lab4-product-b-design`: 21 spec màn hình, 8 ADR,
  database design, business rules). Nguồn nghiệp vụ gốc là RFP hư cấu YCL-RFP-2026-01; repo này không chép RFP.
- **PREMISE.md có thay đổi:** 14 chỗ thêm/sửa spec (P-01…P-14, trong đó thêm màn mới **SCR-064 乗務実績入力**), 9 giả định bổ sung
  (A5-01…A5-09), 7 hướng đã chốt (D-01…D-07). Không bỏ spec nào. Xem [PREMISE.md](PREMISE.md).
- **Backlog:** **11 epic · 49 issue · 219 sub-issue**. Riêng ràng buộc giờ lái 2024 là epic **E9** gồm 13 issue và 50 sub-issue,
  mỗi rule BR-DRV (hoặc cặp rule dùng chung một phép tính, ví dụ BR-DRV-04/05, 07/08) là một sub-issue (nhãn `special-constraint`).
- **Estimate:** 997 SWP (skill `/tkm:sun-estimate`, đã review 5 issue mẫu) → 1.994 giờ theo quy ước 2h/SWP. Xem [estimate.md](estimate.md).
- **Sprint giả lập đã chạy:** **Sprint 1** (2026/11/16 → 2026/11/27): cam kết 36 sub-issue / 147 SWP, xong 23 / 91 SWP.
  Xem [progress-report.md](progress-report.md).

## 2. Link

| Mục | Link |
|---|---|
| Repo (public) | https://github.com/linhnn-22575/lab5-product-b-backlog |
| GitHub Project (public) | https://github.com/users/linhnn-22575/projects/1 |
| Báo cáo HTML của skill chấm SWP | [`reports/sun-estimate-lab5-product-b-backlog-261111.html`](reports/sun-estimate-lab5-product-b-backlog-261111.html) — file tự chứa; GitHub hiển thị mã nguồn, muốn xem dạng trang thì tải file về và mở bằng trình duyệt |
| Burndown Sprint 1 | [`reports/sprint-1-burndown.svg`](reports/sprint-1-burndown.svg) |

Kiểm tra truy cập không cần đăng nhập (2026/11/11): gửi request không kèm cookie hay token tới repo, Project, file HTML trong repo và
một issue (#197), cả 4 đều trả về HTTP 200.

- [ ] Đã mở thử bằng cửa sổ ẩn danh: repo, Project (bảng và field), issue epic #197 và file HTML.

Các view nên dùng trên Project: lọc `iteration:"Sprint 1"` để xem sprint; nhóm theo field `Epic` hoặc `Phụ trách`; lọc
`label:special-constraint` để xem riêng các hạng mục giờ lái 2024.

## 3. Cấu trúc repo

| File / thư mục | Nội dung |
|---|---|
| `README.md` | File này |
| [`PREMISE.md`](PREMISE.md) | Backlog khác LAB-4 ở đâu: spec thêm/sửa, giả định bổ sung, hướng đã chốt |
| [`task-breakdown.md`](task-breakdown.md) | Nguyên tắc chia task, bảng spec → issue, hạng mục giờ lái 2024, chỗ hở của spec LAB-4 |
| [`estimate.md`](estimate.md) | Issue mẫu đã review, cách quy giờ, tổng theo epic, so với estimate LAB-1 |
| [`progress-report.md`](progress-report.md) | Báo cáo tiến độ Sprint 1: trạng thái, burndown, rủi ro trễ |
| [`AI-report.md`](AI-report.md) | Đã dùng AI thế nào, review ra sao, điểm tốt và chưa tốt |
| [`reports/`](reports/) | Báo cáo HTML của skill chấm SWP và ảnh burndown Sprint 1 |
| [`output/breakdown/`](output/breakdown/) | Dữ liệu gốc của backlog: `breakdown.json` (ghép từ `parts/E1…E11.json`), file task chi tiết theo vai trò, script ghép và kiểm tra |
| [`output/github/`](output/github/) | Script đưa backlog lên GitHub (tạo Project/field, tạo issue và sub-issue, ghi SWP/giờ, áp sprint), bảng mã task → số issue, bảng người phụ trách giả định |
| [`output/estimate/`](output/estimate/) | `swp-by-issue.json`: SWP và giờ của cả 279 issue, nguồn để ghi lên Project |
| [`output/sprint/`](output/sprint/) | Script giả lập Sprint 1, kết quả từng issue, script vẽ burndown |
| [`plans/reports/`](plans/reports/) | Ghi chép trung gian khi đọc 21 spec màn hình (bản trích việc thô trước khi gộp thành sub-issue) |
| `.gitignore` | Bỏ qua file tạm, log, file trạng thái chạy script |

Không có thư mục `skills/`: bài này dùng skill có sẵn, không tự viết hay sửa skill.

## 4. Spec → epic

| Spec (mã / file LAB-4, hoặc dòng PREMISE) | Epic trên Project | Ghi chú |
|---|---|---|
| `prototype-vs-design-gap.md` G-01…G-03, G-10, G-15…G-17, G-21…G-23; ADR-001/002/003/007; architecture §6–7 | [#1 — E1 Nền tảng & sửa prototype trái RFP](https://github.com/linhnn-22575/lab5-product-b-backlog/issues/1) | Migration dùng chung, M_xx + tiếng Nhật, 9 vai trò, ngưỡng nhiệt có phiên bản, hạ tầng Tokyo |
| SCR-001, SCR-002, SCR-018; [P-14](PREMISE.md) | [#21 — E2 F12 Xác thực & phân quyền](https://github.com/linhnn-22575/lab5-product-b-backlog/issues/21) | Thẻ giờ lái trên SCR-002 tách sang E9 |
| SCR-010, SCR-011, SCR-015; [P-13](PREMISE.md) | [#43 — E3 F01 Master & chính sách nhiệt](https://github.com/linhnn-22575/lab5-product-b-backlog/issues/43) | |
| SCR-022, ADR-008, BR-INV-04 | [#69 — E4 F02 Nhập hàng](https://github.com/linhnn-22575/lab5-product-b-backlog/issues/69) | |
| SCR-030, SCR-031, SCR-037 | [#83 — E5 F03 Tồn kho & lô](https://github.com/linhnn-22575/lab5-product-b-backlog/issues/83) | |
| ADR-004, ADR-005, SCR-040…SCR-044; [P-09](PREMISE.md), [P-10](PREMISE.md) | [#106 — E6 F04 Đơn hàng & phân bổ](https://github.com/linhnn-22575/lab5-product-b-backlog/issues/106) | Pipeline phân bổ là đường găng |
| SCR-053, BR-OUT-01…03; [P-08](PREMISE.md) | [#148 — E7 F05 Kiểm trước xuất](https://github.com/linhnn-22575/lab5-product-b-backlog/issues/148) | |
| SCR-060 (phần lập tuyến), SCR-062 (vòng đời phiên bản), IF-MAP-01, IF-MAIL-01; [P-03](PREMISE.md), [P-07](PREMISE.md), [P-11](PREMISE.md) | [#167 — E8 F07 Lập tuyến & công bố (phần không thuộc luật)](https://github.com/linhnn-22575/lab5-product-b-backlog/issues/167) | Lập tuyến không thuộc luật; cổng kiểm luật khi công bố nằm ở E9 |
| SCR-016, SCR-061, SCR-063, SCR-060 §logic-11, ADR-006, BR-DRV-01…14, 20…25; [P-01](PREMISE.md) SCR-064 mới, [P-02](PREMISE.md), [P-04](PREMISE.md)…[P-06](PREMISE.md) | [#197 — E9 ★ Ràng buộc giờ lái xe tải 2024 (改善基準告示)](https://github.com/linhnn-22575/lab5-product-b-backlog/issues/197) | **Ràng buộc đặc thù của đề.** 50 sub-issue, nhãn `special-constraint`, 210 SWP (21% backlog) |
| business-rules §8 Q&A-B01…B17; ghi chú spec lỗi thời, enum lệch DB ([P-12](PREMISE.md)) | [#261 — E10 Làm rõ spec & Q&A khách (BrSE)](https://github.com/linhnn-22575/lab5-product-b-backlog/issues/261) | Q&A giờ lái (B06, B07) nằm ở E9 |
| architecture §5, §7; ADR-004/006 §5 (fixture R-06); `prototype-vs-design-gap.md` K-01…K-08 | [#269 — E11 Kiểm thử tích hợp, UAT & quản lý dự án](https://github.com/linhnn-22575/lab5-product-b-backlog/issues/269) | |
| F06, F08, F09, F10, F11, F13 | — | Hoãn Phase 2 theo LAB-4 PREMISE §2, không có issue |
