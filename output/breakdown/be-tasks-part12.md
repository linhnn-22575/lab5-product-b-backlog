# Backend Tasks: Product B — Yuki Cold Logistics (LAB-5)

**Date**: 2026-11-10 | **Total**: TBD

---

## E10: Làm rõ spec & Q&A khách (BrSE)

### S10.2: Đồng bộ spec với database design

#### BE-10.2.2: Thống nhất enum lệch giữa spec và DB trước khi viết migration
Chốt một bộ giá trị cho deviations.deviation_type, lot_status_events.event_type (thêm sự kiện tạo lô), route_segments.segment_type (break/rest), gộp unforeseeable_events.evidence_ref/evidence_ref_no, thêm cột tham chiếu đối tượng cho idempotency_keys.

- [ ] Lập bảng enum hiện tại spec vs DB
- [ ] Chốt giá trị cùng BrSE
- [ ] Cập nhật database-design
- [ ] Báo các issue migration liên quan

**AC:**
- database-design chỉ còn 1 định nghĩa cho mỗi enum
- Migration E1/E4/E8/E9 dùng đúng enum đã chốt

