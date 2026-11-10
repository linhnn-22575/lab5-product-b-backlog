# Backend Tasks: Product B — Yuki Cold Logistics (LAB-5)

**Date**: 2026-11-10 | **Total**: TBD

---

## E9: ★ Ràng buộc giờ lái xe tải 2024 (改善基準告示)

### S9.12: Thẻ cảnh báo giờ lái trên trang chủ (SCR-002 4.8/4.10/4.11)

#### BE-9.12.1: [DRV] Làm get_driver_month_restraint và truy vấn thẻ 4.8/4.10/4.11
Hàm get_driver_month_restraint(p_month) dùng select_driver_duty_days (thực tế > route_plan bản published) và hạn từ rule version hiệu lực (restraint_month_max_h hoặc ext, BR-DRV-14), ngưỡng 90%, top 5; truy vấn thẻ 4.8 (latest check của route_version hiện tại có violation_count > 0) và 4.10 (sự cố submitted, loại do chính mình ghi).

- [ ] Gắn vào khung get_home_summary của epic trang chủ
- [ ] Không viết cứng 284
- [ ] Lọc route_versions.status='published' (062 gap #7)

**AC:**
- Tài xế 255.6h/284h (= 90%) xuất hiện ở 4.11; 255.5h không xuất hiện
- Bật ext 310h → ngưỡng thành 279h; số giờ tháng khớp lũy kế BR-DRV-03 của SCR-061 cùng tài xế


