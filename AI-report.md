# AI-report — LAB-5 Product B

Công cụ: Claude Code (model Claude Opus) chạy trong VS Code, bộ skill Takumi (`tkm:*`), `gh` CLI. AI làm phần lớn việc đọc spec,
viết JSON, viết script và chạy lệnh. Con người (học viên) ra mọi quyết định có ảnh hưởng tới phạm vi, cách làm và điểm số.

## 1. Skill đã dùng và cách viết prompt cho từng việc

| Việc | Skill / công cụ | Prompt và cách chạy |
|---|---|---|
| Chọn skill | Hỏi trực tiếp | Dán đề LAB-5, hỏi "dùng skill takumi nào". Chốt chuỗi: `tkm:estimate` (task-breakdown) → script `gh` → `tkm:sun-estimate` → báo cáo tiến độ. Lưu vào memory: muốn đổi skill hay cách làm đã thống nhất thì AI phải hỏi trước |
| Break task | `/tkm:estimate task-breakdown` | Prompt nêu: nguồn (đường dẫn bộ spec LAB-4, liệt kê loại tài liệu), mục tiêu (epic → issue → sub-issue, task không mơ hồ), **ràng buộc bắt buộc** (tách riêng mọi hạng mục giờ lái 2024, không gộp), yêu cầu ghi lại chỗ hở spec, và "chưa tạo issue ở bước này". AI hỏi lại 4 điểm: mức chi tiết (chọn L3: task + AC), vai trò (FE, BE, QA Manual, Infra/PM, BrSE), ngôn ngữ, thư mục |
| | Agent song song | 4 agent đọc 21 spec theo nhóm màn hình, ghi bản trích việc thô vào `plans/reports/`. Sau đó 4 agent viết từng epic vào `parts/E*.json` theo một file luật chung `_RULES.md` (định dạng id, tên ≤ 80 ký tự bắt đầu bằng động từ, tiền tố `[DRV]`, 3–4 checklist, 2–3 AC, mỗi epic một lần ghi file). E10, E11 do agent chính viết |
| | Script kiểm tra | `merge-and-validate-breakdown-parts.py`: vai trò hợp lệ, tiền tố id khớp vai trò, cỡ S/M/L, task giờ lái phải có `[DRV]`, không trùng id, `depends_on` trỏ đúng task |
| Đưa lên GitHub Project | Script Python gọi `gh api graphql` | Prompt: tên repo, tài khoản, danh sách người phụ trách giả định. AI tạo Project public, field (Status, Iteration 10 sprint, Loại, Epic, Vai trò, Phụ trách, Cỡ, SWP, Estimate (h)), nhãn. Mỗi issue tạo bằng **một** lệnh `createIssue` có luôn issue cha và Project. Số issue tính trước theo thứ tự tạo để thân issue ghi được "Blocked by #n" tới issue tạo sau; script dừng nếu số thực tế lệch |
| Chấm SWP | `/tkm:sun-estimate` | Prompt: chấm 219 sub-issue (nhãn `type:task`), epic/story cộng dồn, báo cáo HTML trong repo, tiếng Việt. Skill chạy: kiểm quyền đọc (`tool_policy.py`) → lấy issue → chọn phạm vi (`selection.py`) → chia 5 lô → 5 agent chấm theo file hợp đồng chấm điểm (băng Scope/Complexity, ma trận, enum) → `validate` → chọn 5 issue mẫu → **người duyệt từng issue, 2 vòng (mức khó rồi điểm cụ thể)** → hiệu chỉnh → render HTML → cổng kiểm tra sau render |
| Quy giờ | Agent chính tính, người chọn | AI so SWP với cỡ S/M/L đã ước khi chia task (SWP trung bình theo cỡ, tỉ lệ giờ trần/SWP) và đề xuất 2h/SWP; quy tắc áp dụng ghi ở [estimate.md](estimate.md) §2 |
| Ghi SWP lên Project | Agent chính chạy script `write-swp-and-hours-to-project.py` | Skill chấm SWP chỉ đọc, không ghi tracker. Agent xuất SWP đã duyệt từ payload đã validate ra `output/estimate/swp-by-issue.json`, rồi chạy script ghi `SWP` và `Estimate (h)` cho 279 item (issue cha = tổng con), sau đó đọc lại Project để đối chiếu tổng 997 SWP / 1.994h |
| Báo cáo tiến độ | Script giả lập + đọc Project | Kế hoạch ban đầu là `tkm:pm-report-project` + `tkm:pm-track-risks-issues`, nhưng hai skill này chỉ chạy khi repo có bộ hồ sơ PM `project/01_management/`. AI hỏi lại, học viên chọn viết thẳng từ Project. Script `simulate-sprint-1.py` giả lập sprint theo luật cố định, `apply-sprint-1-to-project.py` cập nhật Iteration/Status và đóng issue Done, báo cáo lấy số đọc lại từ Project |
| README, AI-report | Agent chính viết, người duyệt | Prompt: dán lại yêu cầu từng file của đề; AI viết theo đúng thứ tự phần |

## 2. Review output của AI

### Con người review ở đâu

1. **Trước khi làm:** chọn mức chi tiết, vai trò, ngôn ngữ, thư mục.
2. **Khi break task:** quyết định 3 chỗ AI không tự chốt được — tuyến giữ `published` khi đổi (thay vì quay về `created`), thêm màn SCR-064
   nhập giờ thực tế, giữ đủ 219 sub-issue thay vì gộp còn 120–150.
3. **Trước thao tác công khai:** xác nhận tên repo, tài khoản, người phụ trách trước khi AI tạo repo public và 279 issue; tự cấp quyền
   `project` cho `gh`.
4. **Khi chấm SWP:** duyệt 5 issue mẫu, từng issue một. Duyệt cách xử lý khi worker của skill không chạy được.
5. **Khi làm báo cáo:** chọn cách viết báo cáo khi skill PM không áp dụng được; điền tên học viên.

### Vấn đề phát hiện trong output của AI và cách xử lý

| Bước | Vấn đề | Ai phát hiện | Xử lý |
|---|---|---|---|
| Break task | Agent gộp backlog bị treo 600 giây, không ghi được file nào (cố ghi một file JSON quá lớn) | AI (timeout) | Chia 4 agent theo nhóm epic, mỗi epic một lần ghi, có file luật chung |
| Break task | Số task 219, vượt mức 120–150 dự kiến vì trần 16h/task | AI báo, người quyết | Người chọn giữ 219 |
| Break task | Tìm "anchor" trong spec SCR-016 khớp nhầm `text-anchor` của SVG | AI | Kiểm lại, xác nhận spec thật sự không có anchor date (thành gap) |
| Break task | Task test tích hợp và UAT (#272, #274) không khai báo phụ thuộc vào task tính năng | **Phát hiện muộn, khi giả lập sprint** | Giả lập lần 1 đưa 2 task này vào Sprint 1 (vô lý: chưa có màn nào). Giữ chúng ngoài sprint, ghi thành rủi ro trong progress-report |
| Lên GitHub | Field không điền được: `createIssue` chưa trả về id item trong Project; gộp 60 lệnh/request bị 502/504; tên option Epic bị cắt còn dấu cách cuối | AI (lỗi khi chạy) | Tra lại id từ danh sách item; giảm còn 12 lệnh/request; `.strip()` tên option. Script chạy tiếp được từ chỗ dừng |
| Link tài liệu | Mã viết tắt dải `BE-1.1.1–3` bị đổi thành "#3–3" | AI tự soát diff | Hoàn tác, dạy script hiểu dải mã rồi chạy lại |
| Chấm SWP | Worker riêng của skill không có công cụ đọc file, cả 5 lô trả về rỗng | AI | Hỏi người, dùng 5 agent thường chỉ đọc file lô và ghi file kết quả; ghi rõ trong báo cáo HTML |
| Chấm SWP | 15 task BrSE/PM bị gán discipline `Unknown` nhưng confidence `medium`/`high`, trái luật skill | Bước `validate` của skill | Hạ confidence xuống `low`, ghi lý do vào gaps; điểm SWP không đổi |
| Chấm SWP | Bước kiểm tra sau render báo sai ma trận ở cả 219 dòng | AI tự nghi | Lỗi nằm ở script kiểm tra của AI (tra ma trận theo giá trị thay vì vị trí băng); kiểm lại bằng hàm của skill: không có dòng sai |
| Chấm SWP | Rule pháp lý BR-DRV đơn lẻ được chấm 1–2 SWP — có thể là **tô hồng** | Người, khi duyệt mẫu #212 | Giữ điểm vì test case từng rule đã tách thành task QA riêng; ghi lý do trong estimate.md để người đọc tự đánh giá |
| estimate.md | Dẫn mã task không tồn tại (QA-9.3.3); cộng sai giờ PM/BrSE (42h, đúng là 34h); tỉ lệ chênh ghi 51% (đúng 66%) | AI tự tính lại trước khi nộp | Tra lại breakdown, sửa số và mã |
| Giả lập sprint | Lần chạy 1 đóng nhầm #23; sau khi giả lập lại, issue này đang In Progress nhưng vẫn đóng | AI, khi đối chiếu issue đóng với danh sách Done | Mở lại #23, thêm bước tự mở lại vào script |
| progress-report | 3 câu khẳng định sai so với dữ liệu: "FE hết việc từ ngày 3", "không task nào dưới 6 giờ", "#4 chặn mọi màn nhập/tồn/đơn" | AI, đối chiếu từng câu với dữ liệu giả lập | Sửa theo số liệu thật (FE có việc ngày 3–5 và 6–7; task đầu tiên mất 7,5–15h; #4 chặn #32 và #71) |
| README | AI viết "đã mở thử bằng cửa sổ ẩn danh" dù chưa mở — **bịa** | AI tự soát | Đổi thành ô checkbox để học viên tự kiểm tra; giữ phần AI đã kiểm thật (request không đăng nhập trả HTTP 200) |

| Toàn bộ bài nộp | Agent `reviewer` soát độc lập ([báo cáo](plans/reports/reviewer-261111-lab5-submission-audit.md)): số liệu khớp Project ở mọi chỗ, không lỗi nghiêm trọng; 8 cảnh báo, chủ yếu: tốc độ 2,5h/SWP là tham số giả lập nhưng báo cáo viết như kết quả đo; "mỗi rule BR-DRV một sub-issue" nói quá (có cặp rule đi chung); module chuỗi lái BE-9.6.1 chỉ 3 SWP | Agent reviewer | Sửa câu chữ, ghi rõ "tham số giả lập", nêu BE-9.6.1 là điểm đáng xem lại. Ô "đã mở ẩn danh" để học viên tự đánh dấu |

Bài học về độ tin cậy của báo cáo do AI viết (câu neo P2-11): lỗi nguy hiểm nhất không phải lỗi chạy, mà là những câu nghe hợp lý nhưng
không có dữ liệu đỡ — số cộng sai, mã task bịa, câu "đã kiểm tra" khi chưa kiểm. Cả ba loại đều xuất hiện ở bài này và chỉ bắt được khi
bắt AI đối chiếu từng câu với nguồn (Project, JSON giả lập, breakdown). Báo cáo tiến độ vì vậy lấy số đọc lại từ Project chứ không lấy từ
trí nhớ của AI.

## 3. Điểm đặc biệt trong cách dùng AI

**Chỗ hiệu quả**

- **Một nguồn dữ liệu, mọi thứ sinh ra từ đó.** `breakdown.json` → issue trên GitHub → SWP → giờ → sprint. Mỗi bước là script chạy lại
  được, có file trạng thái để chạy tiếp khi bị ngắt. Khi phải sửa (ví dụ giả lập lại sprint), chỉ cần chạy lại script, không sửa tay 279 issue.
- **Cổng kiểm tra cứng giữa các bước:** script validate breakdown, `validate` của skill chấm SWP, kiểm tra sau render, đối chiếu Project sau
  mỗi lần ghi. Các lỗi ở bảng §2 có cột "AI (lỗi khi chạy)" hoặc "bước validate" đều bị chặn ở các cổng này trước khi lọt ra ngoài.
- **AI hỏi lại khi phải đổi cách làm** (nhờ quy tắc lưu trong memory): đổi worker chấm điểm, bỏ skill PM. Người giữ quyền quyết, AI không
  tự thay quy trình.
- **Tách ràng buộc giờ lái thành epic riêng từ đầu** giúp mọi số sau đó (SWP, giờ, tiến độ sprint, so với LAB-1) đều đọc riêng được cho
  phần này.

**Chỗ chưa tốt, cần cải thiện khi làm thật**

- **Token:** riêng bước chấm SWP tốn khoảng 750 nghìn token (5 agent × ~150 nghìn), chưa kể lần chạy hỏng đầu tiên với worker không có
  công cụ. Làm thật nên chấm theo lô nhỏ hơn hoặc chỉ gửi tóm tắt issue (tiêu đề, mô tả, AC) thay vì cả thân issue.
- **Hệ số 2h/SWP chưa có dữ liệu lịch sử**, chỉ suy từ cỡ S/M/L do chính AI ước. Làm thật phải hiệu chỉnh sau 1–2 sprint thật.
- **Sprint giả lập do chính mình đặt luật** (tốc độ ×1,25, migration vượt giờ, hai việc chờ khách), nên hình dạng burndown một phần là do
  thiết kế. Nó cho ra phát hiện thật (FE thiếu việc vì chờ API, task E11 thiếu phụ thuộc) nhưng không thay được dữ liệu sprint thật.
- **Phụ thuộc giữa task do AI suy ra chưa đủ.** Lỗ hổng chỉ lộ ra khi giả lập. Lần sau nên thêm luật vào script validate: task QA chạy test
  phải phụ thuộc ít nhất một task tính năng.
- **Việc BrSE/PM không có chỗ trong rubric SWP** (chỉ có discipline kỹ thuật), nên 15 task bị confidence thấp. Cần một quy ước riêng cho
  loại việc này.
- **Review mẫu chỉ 5/219 issue** theo cách skill chọn. Làm thật nên thêm một lượt người duyệt nhanh toàn bộ E9 vì đây là phần rủi ro pháp lý.

**Chưa có ý tưởng:** cách cho AI tự phát hiện câu "đã kiểm tra" mà không có bằng chứng trong cùng phiên — hiện chỉ dựa vào việc tự soát
và người đọc lại.
