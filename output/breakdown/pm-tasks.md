# PM Tasks: Product B — Yuki Cold Logistics (LAB-5)

**Date**: 2026-11-10 | **Total**: TBD

---

## E9: ★ Ràng buộc giờ lái xe tải 2024 (改善基準告示)

### S9.13: Xác nhận pháp lý và làm rõ Q&A giờ lái

#### PM-9.13.1: [DRV] Lấy xác nhận pháp lý OPS-LAW-01/Q&A-B06 từ phụ trách vận tải
Lấy xác nhận bằng văn bản của người phụ trách vận tải khách về bảng BR-DRV (giá trị seed 2024-04 so với 改善基準告示), công thức tăng ca (拘束 − nghỉ giữa ca − 8h) và phạm vi loại sự cố (chỉ 04/05, 09, 11) trước khi chốt engine.

- [ ] Gửi bảng BR-DRV + ví dụ LY2
- [ ] Ghi biên bản vào Q&A-B06
- [ ] Cập nhật source_checked_on cho bản seed

**AC:**
- Có câu trả lời ghi nhận cho công thức tăng ca và phạm vi sự cố
- Thay đổi (nếu có) được chuyển thành issue sửa rule tương ứng

## E11: Kiểm thử tích hợp, UAT & quản lý dự án

### S11.3: Quản lý sprint, báo cáo tiến độ và phát hành Phase 1

#### PM-11.3.1: Lập kế hoạch sprint và vận hành board GitHub Project
Chia Iteration, gán người phụ trách, theo dõi trạng thái và đường phụ thuộc (pipeline phân bổ, engine giờ lái) mỗi sprint.

- [ ] Tạo Iteration 2 tuần
- [ ] Gán issue theo phụ thuộc
- [ ] Daily cập nhật trạng thái
- [ ] Retro cuối sprint

**AC:**
- Mỗi issue trong sprint có người phụ trách, SWP, giờ
- Board phản ánh đúng trạng thái thực tế

#### PM-11.3.2: Viết báo cáo tiến độ sprint gửi khách (trạng thái, burndown, rủi ro)
Báo cáo tiến độ mỗi sprint: số issue/SWP theo trạng thái, burndown, rủi ro trễ kèm hành động và người phụ trách.

- [ ] Xuất số liệu từ Project
- [ ] Vẽ burndown
- [ ] Bảng rủi ro
- [ ] Review trước khi gửi

**AC:**
- Báo cáo khớp số liệu trên Project
- Mỗi rủi ro có hành động + người + hạn
