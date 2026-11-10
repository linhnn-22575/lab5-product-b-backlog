# Frontend Tasks: Product B — Yuki Cold Logistics (LAB-5)

**Date**: 2026-11-10 | **Total**: TBD

---

## E5: F03 Tồn kho & lô

### S5.1: Tra cứu tồn kho theo lô (SCR-030)

#### FE-5.1.3: Dựng màn tra cứu tồn kho: vùng lọc 10 điều kiện, tóm tắt và bảng lô
Trang SCR-030 gọi GET /api/lots: vùng lọc đồng bộ URL, dòng tóm tắt, bảng 12 cột có badge nhãn hạn/trạng thái/要移動/廃棄承認待ち, link SCR-031, phân trang 50.

- [ ] Lọc áp khi bấm 検索/Enter, URL sync, 条件クリア về mặc định, vị trí phụ thuộc vùng (reset khi đổi vùng)
- [ ] Multi-select trạng thái (bỏ chọn hết = hiện cả 5)
- [ ] Tooltip lý do khả dụng = 0, badge 要移動, 廃棄承認待ち, link SCR-031 giữ bộ lọc
- [ ] Trạng thái loading (giữ số cũ mờ), empty M_32, error M_40/M_41 + 再試行

**AC:**
- Reload trang với URL có điều kiện cho ra cùng kết quả
- Mã lô sai Format_Code hoặc hạn từ > hạn đến hiện M_13/M_303, không gọi API

### S5.2: Chi tiết lô, lịch sử sự kiện và cách ly thủ công (SCR-031)

#### FE-5.2.4: Dựng phần đầu, thông tin lô 12 trường và dialog cách ly SCR-031
Header lô (badge trạng thái/hạn/廃棄承認待ち), thông tin 12 trường, bảng deviation, link SCR-022/SCR-037 theo quyền; nút 隔離 + dialog gọi POST /api/lots/{id}/quarantine.

- [ ] Nút 隔離 chỉ hiện khi allowedActions có quarantine; disable khi có phân bổ (M_302)
- [ ] Dialog: lý do + bộ đếm (M_06), chọn deviation, file hoặc số tham chiếu 1–100, Idempotency-Key sinh khi mở
- [ ] Map lỗi M_301/M_302/M_316, thành công M_306 + reload
- [ ] Nút quay lại giữ bộ lọc SCR-030; trạng thái loading/not found/error

**AC:**
- Mỗi trạng thái lô (available/có phân bổ/quarantine/on_hold/chờ hủy/disposed) hiển thị đúng nút và badge
- Bấm gửi 2 lần chỉ tạo 1 lần cách ly

#### FE-5.2.5: Dựng timeline sự kiện lô: 10 loại, lọc, さらに表示, copy correlation ID
Timeline gọi GET /api/lots/{id}/events: bảng ánh xạ 10 loại sự kiện (nhãn, màu, biến động), lọc loại, tải thêm keyset 50 thẻ, gộp correlation, link tham chiếu theo quyền.

- [ ] Bảng ánh xạ 10 loại (receive…adjust), sự kiện ship hiện 便 {route_no}
- [ ] Lọc kinds, さらに表示 dùng before
- [ ] Copy correlation ID (auditor), link chỉ khi có quyền xem màn đích
- [ ] Timeline rỗng hiện 初期データ

**AC:**
- Thẻ cùng correlation_id hiển thị gộp 1 nhóm
- Không có thao tác sửa/xóa thẻ nào trên UI

### S5.3: Máy trạng thái lô: cách ly, 保留, giải phóng, hủy có duyệt 2 người (SCR-037)

#### FE-5.3.5: Dựng khung màn SCR-037: tab vùng, bộ lọc, bảng lô cách ly, cột thao tác
Trang gọi GET /api/lots/quarantine: tab 冷蔵(C-Q)/冷凍(F-Q)/常温 kèm số lô, bộ lọc đồng bộ query, bảng 4.1–4.12, cột thao tác theo allowedActions, ghi chú 常温 M_314, trang 403.

- [ ] Tab mặc định, nhãn động 常温, bộ lọc SKU/mã lô/trạng thái
- [ ] Badge 要移動 (chỉ cảnh báo), cờ hạn, deviation, badge yêu cầu hủy, tooltip 保留/期限超過
- [ ] Disable nút khi pending (M_321) hoặc có phân bổ
- [ ] Loading skeleton, empty M_32, lỗi M_40/M_41 + 再試行

**AC:**
- warehouse_lead/auditor thấy bảng nhưng không thấy nút thao tác
- Lô quá reevaluation_due chỉ hiện 期限超過, trạng thái không đổi

#### FE-5.3.6: Dựng dialog 保留, giải phóng và hủy lô trên SCR-037
Dialog [10] 保留, [6] giải phóng (upload bằng chứng qua POST /api/evidence, chọn vị trí đích), [7] hủy (nhãn nút theo ngưỡng, M_323), gọi POST /api/lots/{id}/hold|release|dispose.

- [ ] 保留: kế hoạch + ngày dự kiến (M_325/M_326)
- [ ] Giải phóng: vị trí đích lọc theo vùng, file hoặc số tham chiếu (M_307/M_316), map lỗi M_204/M_313
- [ ] Hủy: đổi nhãn nút khi vượt ngưỡng, thông báo M_323; sửa câu M_317 theo trạng thái hiện tại
- [ ] Xung đột → reload bảng

**AC:**
- Lô ở khu -Q không gửi được giải phóng khi chưa chọn vị trí đích
- Hủy vượt ngưỡng hiển thị trạng thái 廃棄承認待ち sau khi gửi

#### FE-5.3.7: Dựng bảng hủy chờ duyệt và dialog duyệt/từ chối hủy lô
Bảng [5] yêu cầu hủy pending từ GET /api/lot-disposal-requests và dialog [8] duyệt/từ chối gọi POST …/decision; ẩn thao tác với người gửi (canDecide).

- [ ] Bảng request_no, lô, qty, người gửi, thời điểm
- [ ] Ẩn nút khi canDecide = false
- [ ] Từ chối bắt buộc comment 10–500 (M_318), map M_311/M_312

**AC:**
- Người gửi yêu cầu không thấy nút duyệt cho yêu cầu của chính mình
- Yêu cầu đã quyết định bởi người khác → thông báo M_312 và tải lại

