# Trích xuất spec màn hình — Nhóm B (SCR-016, 018, 022, 030, 031)

Nguồn: `lab4-product-b-design/specs/05-screens/SCR-<id>_SPEC.md` (đã đọc hết từng file). Đối chiếu thêm với
`04-business-rules/business-rules.md`, `03-database/database-design.md`, `02-adr/ADR-006…`, `06-common/role-permission-matrix.md`,
`06-common/common-format.md`, `06-common/message-list.md` (mọi mã M_xx dùng trong 5 màn đều có trong message-list).

Quy ước cỡ task: S ≤ 4h · M ≤ 8h · L ≤ 16h. Không task nào > 16h.
Viết tắt: "spec#5-14.2" = file spec của màn đó, mục 5 (Detail spec), item 14.2.

---

## Tổng quan

| Màn | Tên | Dính giờ lái 2024? | Số sub-task |
|---|---|---|---|
| SCR-016 | ドライバー規則版管理 | **CÓ — lõi** | 23 |
| SCR-018 | ユーザー・ロール管理 | Gián tiếp (gán vai trò `transport_manager`/`dispatcher`) | 12 |
| SCR-022 | 入荷検品・確定 | Không | 21 |
| SCR-030 | 在庫照会 | Không | 9 |
| SCR-031 | ロット詳細・履歴 | Không | 11 |
| **Tổng** | | | **76** |

---

## SCR-016 — ドライバー規則版管理 (Quản lý phiên bản quy tắc giờ làm tài xế)

### 1. Mục đích & vai trò
- Quản lý phiên bản tham số giờ làm tài xế xe tải (quy định 2024-04); engine kiểm tra tuyến (ADR-006, SCR-061) đọc toàn bộ giới hạn từ phiên bản, không viết cứng.
- Ghi: `transport_manager` (permission `driver_rule:write`, bắt MFA). Chỉ xem: `dispatcher`, `auditor`. `admin` và các vai trò khác: **không thấy** (403 M_20). Route `/master/driver-rules`, `/master/driver-rules/compare?a=&b=`.

### 2. Khu vực / component
- Banner cảnh báo kiểm lại nguồn luật M_175 (+ M_191 nếu `source_checked_on` > 365 ngày) — không đóng được.
- Bảng danh sách phiên bản (checkbox chọn tối đa 2, badge 下書き/適用予定/適用中/廃止, ngày hiệu lực, nguồn, gia hạn, số tuyến đã công bố gắn bản → link SCR-062).
- Nút tạo phiên bản mới (chọn bản nguồn để sao chép) + nút so sánh.
- Chi tiết phiên bản: header (version_code, status, effective_from, source_note, source_checked_on) + 5 nhóm tham số (年/月/日・週/休息/運転, 15 tham số) với cột chung (giá trị, đơn vị, mức 違反/警告, mã BR, giá trị mặc định 2024-04).
- Nhóm gia hạn 労使協定 (toggle + 2 giới hạn + lý do + bằng chứng).
- Nhóm nút thao tác theo trạng thái (lưu nháp, kích hoạt, xóa nháp, hủy bản sắp áp dụng, sao chép).
- Màn so sánh (layout 2): bảng diff tham số 18 dòng + diff metadata, "chỉ hiện khác biệt".
- Dialog kích hoạt (layout 3): ngày hiệu lực, ảnh hưởng tuyến đã/chưa công bố (M_194/M_182), diff vs bản đang áp dụng, xác nhận cuối M_181.

### 3. Dữ liệu
- Bảng: `driver_rule_versions` (đọc/ghi), `route_versions` (đọc — đếm tuyến gắn bản, theo `status`, `service_date`), `compliance_check_results` (FK chặn xóa), `audit_log` (ghi).
- API (tất cả **mới**): `GET /api/driver-rules`, `GET /api/driver-rules/{id}`, `POST /api/driver-rules`, `PATCH /api/driver-rules/{id}`, `DELETE /api/driver-rules/{id}`, `GET /api/driver-rules/{id}/activation-impact`, `POST /api/driver-rules/{id}/activate`, `POST /api/driver-rules/{id}/cancel`, `GET /api/driver-rules/compare`.
- RPC: `create_driver_rule_draft(p_copy_from_id)`, `activate_driver_rule_version(p_id, p_effective_from, p_expected_updated_at)` (lock dòng + `pg_advisory_xact_lock`), `cancel_driver_rule_version`, hàm `effective_driver_rule_version(p_at)`, job `retire_superseded_driver_rule_versions()` 00:05 JST; trigger chặn UPDATE khi `status <> 'draft'`.
- File hằng số dùng chung đề xuất: `src/modules/routes/driver-compliance/rule-parameter-catalog.ts` (màn này + engine ADR-006).
- BR: BR-DRV-01..14 (tham số), BR-DRV-20 (mức vi phạm chặn công bố), BR-DRV-22 (không áp ngược), BR-DRV-23 (kết quả kiểm bất biến + hash), BR-TIME-01; OPS-LAW-01; FR-SCH-02; NFR-AUD-01; BR-INV-03.
- ADR: ADR-003 (versioned policy tables), ADR-006 (driver-hours engine), ADR-002 (RPC), ADR-007 (audit).

### 4. Validation / trạng thái / luồng đặc biệt
- Vòng đời `draft → active → retired`; chỉ `draft` sửa được. Trạng thái hiển thị tính từ `status + effective_from + app_today()`.
- Kích hoạt: `effective_from ≥ ngày mai JST` (M_179), không trùng ngày với bản active khác (M_180), bắt buộc `source_note` 10–2000 ký tự + `source_checked_on ≤ hôm nay` (M_176); chặn nếu không khác bản hiện hành (M_190).
- Ràng buộc quan hệ (INFERRED, chống nhập nhầm) → M_177: 7.2 ≤ 7.3; 7.3 ≥ 8.1; 9.1 ≤ 9.2 ≤ 24; 9.4 ≤ 9.1; 10.2 ≤ 10.1 ≤ 24; 11.1 ≤ 9.2; 11.4 ≤ 11.5 ≤ 11.3×60.
- Gia hạn 労使協定: ON → 4 field bắt buộc (M_184), giới hạn gia hạn > giới hạn thường (M_185); OFF → NULL hết.
- Version code regex `^\d{4}-(0[1-9]|1[0-2])(-[A-Z0-9]{1,10})?$` (INFERRED); trùng M_14.
- Khóa lạc quan `expected_updated_at` → M_22; bản vừa bị người khác kích hoạt → M_183; hủy chỉ bản 適用予定 (M_192), lý do `Format_Reason`.
- Luôn đúng 1 bản áp dụng tại mọi ngày; 適用中 không có nút "kết thúc" thủ công.
- Trạng thái màn: skeleton, lỗi tải M_40/M_41 + 再試行, hết phiên M_21 (giữ `?id=`), unsaved-changes guard M_31, đang lưu/kích hoạt, xung đột.

### 5. Ràng buộc giờ lái xe 2024 — **CÓ (toàn bộ màn hình)**
- Đây là nơi định nghĩa mọi ngưỡng của engine ADR-006: 960h/3.300h/284h/13h-15h/2 ngày >14h/nghỉ 11h-9h/lái TB 9h (2 ngày), 44h (2 tuần)/lái liên tục 4h, ngắt ≥10 phút, tổng 30 phút; gia hạn 3.400h/310h.
- Kích hoạt phiên bản ảnh hưởng tới tuyến chưa công bố (phải kiểm lại vì hash không khớp — BR-DRV-23) nhưng **không** đổi tuyến đã công bố (BR-DRV-22).
- Phụ thuộc chéo: SCR-060/061/062 (route), `publish_route()` gọi `effective_driver_rule_version(app_today())`.

### 6. Sub-task đề xuất (23)
- [BE] Migration `driver_rule_versions` to-be: cột `source_checked_on`, `ext_reason`, `ext_evidence_ref`, `copied_from_id`, `created/updated/activated/retired_by/at`, `retired_reason`, `long_day_threshold_h`, `drive_2week_anchor_date`; CHECK effective_from theo status, CHECK ext đồng bộ, UNIQUE partial effective_from WHERE active; trigger khóa bản không phải draft — M
- [BE] Seed bản `2024-04` + hàm `effective_driver_rule_version(p_at)` + unit test SQL chọn bản theo ngày — S
- [BE] `rule-parameter-catalog.ts` (nhãn JP, cột DB, đơn vị, mức, mã BR) + hàm diff thuần TS (dùng cho compare + dialog) + unit test — M
- [BE] RPC `create_driver_rule_draft` + `POST /api/driver-rules` (sao chép, gợi ý version_code tháng sau JST + hậu tố -B/-C, reset `source_checked_on`) — M
- [BE] `GET /api/driver-rules` + `GET /api/driver-rules/{id}` (tính `displayState`, `boundPublishedRoutes`) + RLS SELECT cho 3 vai trò — M
- [BE] `PATCH /api/driver-rules/{id}`: zod 17 tham số + `superRefine` quan hệ (M_177/M_184/M_185) + khóa lạc quan + map 409 (M_14/M_22/M_183) + audit_log — M
- [BE] `DELETE /api/driver-rules/{id}` (chỉ draft, 409 M_178/M_22) — S
- [BE] `GET …/activation-impact` (đếm route_versions published/in_progress gắn bản hiện hành, số có service_date ≥ ngày hiệu lực, số created/checked; diff) — M
- [BE] RPC `activate_driver_rule_version` (for update, advisory lock, kiểm đủ điều kiện, khác bản hiện hành, set active, audit) + `POST …/activate` + map lỗi — L
- [BE] RPC + `POST …/cancel` (chỉ active tương lai, lý do, retired_reason/at, audit) — S
- [BE] `GET /api/driver-rules/compare` (dùng hàm diff chung, 400 M_189) — S
- [BE] Hàm `retire_superseded_driver_rule_versions()` (idempotent) — S
- [Infra] Lập lịch job 00:05 JST cho hàm retire (pg_cron hoặc scheduler) + cảnh báo khi job lỗi — S
- [BE] Permission `driver_rule:write` trong role-permissions + `requireApiRole` + `has_role(['transport_manager'])` trong RPC; API đọc 403 cho vai trò ngoài 3 vai trò — S
- [FE] Trang danh sách: bảng phiên bản, badge trạng thái, checkbox chọn tối đa 2 (bỏ dòng chọn sớm nhất), banner M_175/M_191, link số tuyến → SCR-062, mặc định mở bản 適用中 — M
- [FE] Form chi tiết 5 nhóm tham số + cột chung (đơn vị, badge mức, mã BR tooltip, giá trị mặc định, tô vàng khi khác bản nguồn M_193), chế độ readonly, validation client — L
- [FE] Nhóm gia hạn 労使協定 (toggle, nạp sẵn 3400/310 lần bật đầu, disable/clear khi OFF, M_186) — S
- [FE] Nhóm nút theo ma trận trạng thái + lưu nháp/xóa nháp/sao chép/hủy (dialog lý do M_187) + chặn rời trang khi chưa lưu — M
- [FE] Dialog kích hoạt: tự lưu trước, gọi impact API (gọi lại khi đổi ngày), hiển thị M_194/M_182/diff, chặn khi không khác (M_190), xác nhận cuối M_181, lỗi 409 trong dialog — M
- [FE] Màn so sánh layout 2 (select A/B đồng bộ URL, bảng diff tham số + metadata, "chỉ hiện khác biệt", dòng tổng, định dạng `+40`/`— → 3400`/`無効 → 有効`) — M
- [QA] Viết test case SCR-016: ma trận validation (M_177 từng cặp, biên ngày hiệu lực), vòng đời trạng thái, RBAC 3 vai trò + 403, BR-DRV-22 không áp ngược, so sánh — M
- [QA] Chạy test + kịch bản đồng thời (2 người kích hoạt cùng ngày, sửa nháp sau khi bị kích hoạt → M_183, job retire qua nửa đêm JST) — M
- [BrSE] Làm rõ với khách: OPS-LAW-01 (kiểm giá trị seed với 改善基準告示), Q&A-B06 (công thức tăng ca), Q&A-B07 (điều kiện gia hạn 労使協定), ngưỡng 365 ngày M_191, `drive_2week_anchor_date`, cách gắn bản cho tuyến công bố trước ngày hiệu lực — M

### 7. Gap / mâu thuẫn
| # | Vị trí | Mô tả | Đề xuất |
|---|---|---|---|
| G16-1 | spec#5-9.2 (9.3), spec#9 PATCH (17 tham số) vs `database-design.md` §3.2 bảng bổ sung (`long_day_threshold_h` 14, `drive_2week_anchor_date`) và `business-rules.md` BR-DRV-06, BR-DRV-10 | **Màn hình/API thiếu 2 tham số** engine cần: ngưỡng "ngày dài" 14h (BR-DRV-06 dùng `long_day_threshold_h`) và ngày khởi điểm khối 2 tuần (BR-DRV-10). Spec ghi cứng nhãn "14h超" và không có field anchor. Ảnh hưởng trực tiếp tính đúng giờ lái 2024. | **Sửa thiết kế**: thêm 2 field vào nhóm 日・週 / 運転, catalog, compare (20 dòng). Mở issue BrSE xác nhận anchor date. |
| G16-2 | spec#9 "Dữ liệu" ("Spec cần thêm (chưa có trong database-design)") vs `database-design.md` §3.4 `driver_rule_versions` | Câu "chưa có" đã cũ: DB-design đã có `source_checked_on`, `ext_reason`, `ext_evidence_ref`, `activated_by/at`, `retired_by/at`. Vẫn lệch: spec có `copied_from_id`, `retired_reason`, `updated_by` mà DB không có; DB có `retired_by` mà spec không dùng. | Giả định: hợp cả 2 tập cột trong migration; issue nhỏ cập nhật spec/DB-design. |
| G16-3 | spec#9 ("`effective_driver_rule_version(p_at)`") vs `database-design.md` §3.3 ("`effective_driver_rule(at_date)`") | Tên hàm khác nhau giữa 2 tài liệu; engine/`publish_route()` (ADR-006) gọi hàm này. | Chốt 1 tên (đề xuất tên của spec) — sửa DB-design. |
| G16-4 | spec#9 Seed (`source_checked_on = NULL`, dòng「出典確認日 未設定」) | Dòng cảnh báo "chưa đặt ngày kiểm nguồn" không có mã M_xx trong message-list; bản seed active nhưng vi phạm điều kiện kích hoạt (thiếu ngày kiểm). | Issue làm rõ: thêm message mới hoặc seed ngày kiểm sau khi BrSE xác nhận OPS-LAW-01. |
| G16-5 | spec#5-16.3, spec#5-14.3 | Chưa nói khi đã có 1 bản 適用予定 mà kích hoạt thêm bản khác (ngày sớm hơn/muộn hơn): diff so với 適用中 hay với bản sắp áp dụng; số tuyến ảnh hưởng tính theo bản nào. | Issue làm rõ BrSE; giả định tạm: cho phép nhiều bản 適用予定, diff luôn so với 適用中. |
| G16-6 | spec#5-16.4 (BR-DRV-22 hệ quả: tuyến công bố trước ngày hiệu lực vẫn gắn bản cũ dù chạy sau ngày đó) | Có thể trái kỳ vọng pháp lý (chạy sau ngày quy định mới nhưng kiểm theo bản cũ). Spec tự ghi "xem báo cáo, Q&A". | Issue làm rõ với khách (BrSE) — rủi ro tuân thủ. |
| G16-7 | spec#5-13.4 | Ý nghĩa bật gia hạn (thay ngưỡng năm/tháng) là INFERRED; điều kiện kèm theo (giới hạn số tháng được vượt) **chưa thiết kế**, chờ Q&A-B07. | Giả định: chỉ thay ngưỡng; issue BrSE Q&A-B07 chặn phần engine. |
| G16-8 | spec#5-9.3 (9.4), BR "Tăng ca" | Công thức tăng ca INFERRED (Q&A-B06) → ảnh hưởng BR-DRV-01. | Issue BrSE Q&A-B06. |
| G16-9 | spec#5-12.3 | Mức 違反/警告 cố định theo BR (không lưu theo phiên bản) — INFERRED, cần xác nhận. | Giả định theo spec; ghi chú trong issue BrSE. |
| G16-10 | spec#5-16.7 + spec#5-16 | Hai lớp xác nhận (dialog kích hoạt rồi thêm hộp M_181) — UX trùng. | Giả định giữ theo spec; PO quyết khi review UI. |
| G16-11 | spec#5-3.8, spec#5-16.2/16.3 | Phụ thuộc bảng `route_versions` (`service_date`, status) và filter theo phiên bản quy tắc ở SCR-062 — thuộc nhóm F07 chưa có trong prototype. | Đánh dấu dependency trong backlog (impact API sau migration F07). |

---

## SCR-018 — ユーザー・ロール管理 (Người dùng & vai trò)

### 1. Mục đích & vai trò
- `admin` gán 1 vai trò chính (9 vai trò) cho user, xem MFA, vô hiệu hóa / kích hoạt lại. `auditor` xem chỉ đọc (`users:read`). Vai trò khác: M_20. Không tạo / không xóa user ở màn này (JIT qua SSO; demo tạo ở Supabase Dashboard).

### 2. Khu vực / component
- Tiêu đề + ghi chú cách tạo user (khác nhau production / demo theo `AUTH_PASSWORD_LOGIN_ENABLED`).
- Bộ lọc: tìm kiếm (debounce 300ms), vai trò (gồm「未割当」), trạng thái (mặc định 有効), "chỉ user đặc quyền chưa MFA"; đồng bộ URL; preset `?role=none`, `?mfa=unverified` từ SCR-002.
- Bảng user: email, họ tên, select vai trò trong ô, badge MFA, badge trạng thái, lần đăng nhập cuối, nút 無効化/有効化; dòng "（自分）".
- Hộp kết quả thành công/lỗi (role=status/alert); phân trang 50/trang.
- Dialog đổi vai trò (cảnh báo đặc quyền M_125 hoặc M_31; cảnh báo đỏ khi bỏ vai trò).
- Dialog vô hiệu hóa (lý do 10–500, bộ đếm).

### 3. Dữ liệu
- Bảng: `profiles` (đọc/ghi qua RPC), `audit_log`, `auth.sessions` / `auth.refresh_tokens` (xóa khi vô hiệu).
- API: `GET /api/users` (to-be có filter + paging), `PATCH /api/users/:id/role` (to-be: `expectedRole`), `PATCH /api/users/:id/status` (**mới**).
- RPC: `admin_set_user_role(p_user_id, p_role, p_expected_role)`, `admin_set_user_active(p_user_id, p_active, p_expected_active, p_reason)` — security definer, for update, audit; lỗi `P0001` + `hint` = mã M_xx. Trigger tự đặt `mfa_required` theo vai trò; `current_app_role()` trả NULL khi `is_active = false`; thu hồi grant `update(role)`.
- Tham chiếu: RBAC-001, NFR-SEC-01/02, NFR-AUD-01, BR-INV-03, IF-IDP-01, SCR-001 (callback ghi `mfa_verified_at`, M_106, re-auth MFA), SCR-002. ADR: không nêu trực tiếp (ADR-002 RPC, ADR-007 audit áp dụng chung).

### 4. Validation / trạng thái / luồng đặc biệt
- Không tự đổi vai trò (M_120) / tự vô hiệu hóa (M_122) — chặn cả UI và API. Không đổi vai trò user bị vô hiệu (M_127).
- Đổi vai trò không lưu ngay: mở dialog; Hủy/lỗi → trả select về giá trị cũ. Khóa lạc quan `expectedRole` / `expectedActive` → M_22 (tự tải lại dòng).
- Vô hiệu hóa có hiệu lực ngay: RLS chặn, middleware hủy phiên → `/login?error=deactivated` (M_106), xóa refresh token. Kích hoạt lại giữ vai trò cũ (M_124).
- Đổi sang vai trò đặc quyền khi user đang trong phiên → request kế tiếp phải đăng nhập lại có MFA.
- State machine user: active_no_role ↔ active_with_role ↔ inactive.
- Trạng thái màn: loading skeleton 5 dòng, rỗng M_32, đang lưu 1 dòng (khóa mọi dòng), lỗi tải, lỗi lưu, không quyền (không render bảng).

### 5. Ràng buộc giờ lái xe 2024 — **Gián tiếp**
- Không có logic giờ lái. Nhưng đây là nơi cấp vai trò `transport_manager` (người duy nhất sửa/kích hoạt quy tắc giờ làm SCR-016, bắt MFA) và `dispatcher`. Test RBAC của SCR-016 phụ thuộc màn này.

### 6. Sub-task đề xuất (12)
- [BE] Migration `profiles`: `is_active`, `deactivated_at/by/reason` (CHECK 10–500), `mfa_verified_at`, `last_sign_in_at`, CHECK `role` 9 giá trị; trigger `mfa_required` theo vai trò; sửa `current_app_role()` lọc `is_active`; thu hồi grant `update(role)` — M
- [BE] RPC `admin_set_user_role` + `PATCH /api/users/:id/role` (zod 9 vai trò + null, map P0001 hint → M_120/M_127/M_22, 404 M_23, audit before/after) — M
- [BE] RPC `admin_set_user_active` + `PATCH /api/users/:id/status` (reason bắt buộc khi deactivate, xóa refresh token, audit) — M
- [BE] Spike: cách thu hồi phiên Supabase an toàn (xóa trực tiếp `auth.refresh_tokens` trong RPC vs Admin API `signOut`) — S
- [BE] `GET /api/users` to-be: q (escape `%`/`_`), role/none, status, mfa=unverified, paging 50, RLS `profiles_select_admin_or_auditor`, quyền `users:read` — M
- [BE] Middleware: user bị vô hiệu → hủy phiên + redirect `/login?error=deactivated`; đổi sang vai trò đặc quyền → bắt re-auth MFA (phối hợp SCR-001) — M
- [FE] Trang danh sách: bộ lọc + URL sync + debounce 300ms + preset từ SCR-002 + bảng + badge MFA/trạng thái + phân trang + chế độ chỉ đọc cho auditor — M
- [FE] Select vai trò trong ô + dialog đổi vai trò (M_125 / M_31, cảnh báo bỏ vai trò, rollback khi hủy/lỗi, cập nhật dòng từ response) — M
- [FE] Dialog vô hiệu hóa (bộ đếm, M_06) + xác nhận kích hoạt lại + hộp kết quả (map lỗi 403/404/409/400/500/mạng) + trạng thái dòng (自分, vô hiệu, đang lưu) — M
- [QA] Viết test case: state machine user, tự bảo vệ, auditor read-only, 409 đồng thời, hiệu lực ngay sau vô hiệu hóa, MFA re-auth khi lên vai trò đặc quyền — M
- [QA] Chạy test + kiểm bảo mật (gọi API thẳng không quyền → 403, RLS profiles, UPDATE trực tiếp bị chặn, audit_log có bản ghi) — M
- [BrSE] Xác nhận: không xóa cả user chưa có lịch sử (INFERRED); 1 người 1 vai trò (Q&A-B10); khóa tài khoản IdP do IT làm riêng — S

### 7. Gap / mâu thuẫn
| # | Vị trí | Mô tả | Đề xuất |
|---|---|---|---|
| G18-1 | spec#9 ("`profiles` to-be … chưa có trong database-design") vs `database-design.md` §3.3 dòng `profiles` | Câu đã cũ — DB-design đã có đủ các cột. Không lệch kỹ thuật, chỉ tài liệu. | Sửa spec (issue docs nhỏ). |
| G18-2 | spec#5-11.5 (c) | Xóa refresh token trong RPC đụng schema `auth` của Supabase (không phải API công khai) — rủi ro khi nâng cấp Supabase / quyền security definer. | Spike BE (đã đưa vào task); nếu không ổn → dùng Admin API ở route handler. |
| G18-3 | spec#5-10.2 | Đổi giữa 2 vai trò **đặc quyền** khác nhau (vd. `quality` → `admin`) chỉ hiện M_31, không cảnh báo — dù quyền thay đổi lớn. | Giả định theo spec; ghi chú cho BrSE. |
| G18-4 | spec#3 (9 vai trò) vs SCR-022/030/031 §7 (dòng `driver`) | Nhóm B có màn nhắc vai trò `driver` nhưng ma trận quyền chỉ có 9 vai trò (không có `driver`). SCR-018 không cho gán `driver`. | Issue làm rõ: `driver` là thực thể (bảng drivers) hay vai trò đăng nhập? Giả định: không phải vai trò app. |
| G18-5 | spec#5-7.3.5 | Đổi vai trò có hiệu lực từ request kế tiếp nhưng tab đang mở vẫn hiển thị menu cũ cho tới khi tải lại. | Giả định chấp nhận; QA kiểm API trả 403 đúng. |

---

## SCR-022 — 入荷検品・確定 (Kiểm hàng nhập & xác nhận phiếu)

### 1. Mục đích & vai trò
- Người nhận hàng ghi kết quả kiểm từng dòng phiếu nhập rồi xác nhận phiếu → sinh lô bất biến, ghi sổ di chuyển, tự cách ly lô không đạt và mở deviation.
- Ghi (`inbound:write`): `admin`, `warehouse`, `warehouse_lead`. Chỉ xem: `quality`, `sales_planner`, `sales_manager`, `dispatcher`, `transport_manager`, `auditor`.

### 2. Khu vực / component
- Layout 1 `/inbound`: vùng lọc (trạng thái, nhà cung cấp, khoảng ngày đến, số phiếu; URL sync), nút + dialog tạo phiếu (chọn supplier), bảng phiếu (số dòng, số dòng thiếu P0, số dòng ngoài ngưỡng, trạng thái, người xác nhận), phân trang.
- Layout 2 `/inbound/[id]`: header phiếu, panel kiểm trước xác nhận (Chặn ● / Báo trước ▲, bấm để nhảy tới dòng), bảng dòng (14 cột: SKU, lô, NSX, loại hạn, hạn, nhiệt độ & phán định, bao bì, SL, vị trí, mã truy xuất, ảnh, lô đã sinh, sửa/xóa), form thêm/sửa dòng (13 field + ảnh), nút xác nhận, dialog xác nhận.
- Layout 3: dialog kết quả (số lô tạo / cách ly / deviation + bảng lô).

### 3. Dữ liệu
- Bảng: `inbound_receipts`, `inbound_lines`, `suppliers`, `skus` (`trace_lane`, `expiry_type`, `temp_zone`), `locations` (`is_quarantine`), `temp_zone_policy_versions`, `lots`, `lot_status_events`, `inventory_movements`, `deviations`, `idempotency_keys`, `audit_log`, Storage bucket `inbound-photos`.
- API: `GET/POST /api/inbound-receipts`, `GET /api/inbound-receipts/{id}` (kèm `check`), `POST/PATCH/DELETE …/lines[/{lineId}]`, `POST …/lines/{lineId}/photo` (mới), `POST …/confirm` (Idempotency-Key), `GET /api/suppliers`, `GET /api/locations`, `GET /api/skus`.
- View/hàm: `inbound_receipt_list_view`, `inbound_lines_with_temp_check` (mở rộng), `inbound_receipt_check(p_receipt_id)` (dùng chung GET + RPC), `effective_temp_policy(zone, arrived_at)`.
- RPC: `confirm_inbound_receipt(p_receipt_id, p_idempotency_key)` — 8 bước (role, idempotency, lock, NO_LINES, check, sinh lô/sự kiện/movement/deviation/snapshot, update phiếu + audit, lưu response).
- BR: BR-TEMP-01/02/03, BR-INV-02/04, BR-EXP-01/02, BR-DELWIN-01, BR-TIME-01; FR-REC-02/04/05. ADR: ADR-002, ADR-003, ADR-008 (2 lớp kiểm nhiệt: A không chặn, B chặn).

### 4. Validation / trạng thái / luồng đặc biệt
- Field P0: SKU, mã lô, hạn, nhiệt độ đo, bao bì, SL, vị trí, **ảnh**. Lưu dòng được khi thiếu P0 (chỉ bắt SKU); thiếu P0 chặn xác nhận, liệt kê từng field từng dòng (M_202).
- Chặn xác nhận: thiếu P0, vùng SKU ≠ vùng vị trí (M_204), quy tắc khu `-Q` (M_212/M_213), vị trí/SKU ngưng (M_215/M_210), trùng lô trong phiếu (M_224) / trong kho (M_206), không có phiên bản ngưỡng (M_214).
- Báo trước (không chặn): ngoài ngưỡng → cách ly + deviation (M_205); thiếu mã truy xuất beef/rice → cách ly (M_216); thiếu NSX (M_219); hạn trước ngày đến (M_220).
- Validation lưu dòng: NSX ≤ hôm nay (M_203), NSX < hạn (M_221), bao bì ≠ 良好 ⇒ ghi chú (M_222), beef 10 chữ số (M_217), nhiệt độ −50..50 1 số lẻ (M_05/M_13), SL 1..99 999, ảnh JPG/PNG/HEIC ≤10MB (M_223).
- Phiên bản ngưỡng chọn theo **ngày JST của `arrived_at`**; phiếu đã xác nhận hiển thị giá trị chụp lại.
- Idempotency: key sinh khi mở dialog, giữ cho mọi lần gửi lại; cùng key → trả kết quả cũ 200; key khác sau khi đã xác nhận → 409 M_208. 422 `CHECK_FAILED` trả **toàn bộ** lỗi.
- Phiếu `draft → confirmed` một chiều. Trạng thái màn: loading, empty, error, not found, draft còn lỗi / sạch, đang xác nhận, confirmed, xung đột (M_208/M_211).
- UX cửa kho: ô ≥ 44px, số lớn, nhận máy quét (Enter chuyển focus), giữ SKU/vị trí/bao bì sau khi lưu dòng.

### 5. Ràng buộc giờ lái xe 2024 — **Không**
- Không đụng lịch giao / giờ tài xế. (Chỉ chung cơ chế versioned policy ADR-003 với SCR-016.)

### 6. Sub-task đề xuất (21)
- [BE] Migration nhập hàng: master `suppliers` + `inbound_receipts.supplier_id` (migrate `supplier_name`, hậu tố 未登録), cột mới `inbound_lines` (NSX, bao bì, ghi chú, vị trí, mã truy xuất, ảnh, policy_version_id, temp_out_of_range, lot_id), `locations`, `deviations`, `idempotency_keys`, `lots` (location, NSX, 5 trạng thái) — L
- [BE] View `inbound_receipt_list_view` + `GET /api/inbound-receipts` (filter, escape like, refine ngày M_225, paging 50, đếm thiếu P0 / ngoài ngưỡng) — M
- [BE] `POST /api/inbound-receipts` theo `supplier_id` (422 M_218, grant cột) — S
- [BE] Hàm `inbound_receipt_check(p_receipt_id)` trả đủ blocking + warnings với `lineNo`, `messageId`, `params` (P0, BR-TEMP-02 B, -Q, ngưng, trùng lô, thiếu policy, cảnh báo A/trace/NSX/hạn) + test SQL — L
- [BE] Mở rộng view `inbound_lines_with_temp_check` + `GET /api/inbound-receipts/{id}` kèm `check` — M
- [BE] `POST/PATCH/DELETE` dòng: zod cho phép thiếu P0, refine M_203/M_221/M_222, beef M_217 ở DB, map 409 M_211 / 422 M_210, trigger 0800 B — M
- [BE] `POST …/photo`: upload private, tính SHA-256 server-side, metadata + audit_log, cập nhật `photo_ref`, thay ảnh giữ ảnh cũ, signed URL 5 phút — M
- [Infra] Bucket Storage `inbound-photos` private + policy truy cập + giới hạn kích thước/loại file — S
- [BE] RPC `confirm_inbound_receipt` đủ 8 bước (idempotency, for update, check, sinh `lots` + `lot_status_events` + `inventory_movements` + `deviations`, snapshot dòng, audit, `correlation_id` chung) — L
- [BE] `POST …/confirm`: bắt buộc header `Idempotency-Key`, map 409/422/403/404/5xx, response kết quả — S
- [BE] API master cho select: `GET /api/suppliers?active=`, `GET /api/locations?zone=&active=&quarantine=`, `GET /api/skus` thêm `traceLane` — S
- [FE] Trang danh sách: vùng lọc + URL sync + kiểm ngày (M_225) + bảng + phân trang + dialog tạo phiếu (lọc supplier, M_200) — M
- [FE] Trang chi tiết: header + bảng dòng (badge nhiệt độ/hạn/bao bì/trace/ảnh, tô nền dòng lỗi, cột lô đã sinh khi confirmed) + trạng thái not found/empty — M
- [FE] Panel kiểm trước xác nhận (nhóm Chặn/Báo trước, sắp theo dòng, bấm → cuộn + mở form sửa, M_226) — M
- [FE] Form dòng: P0 gợi ý không chặn, giữ field sau khi lưu, quét mã + Enter, ô ≥44px, phán định nhiệt độ khi blur, vị trí lọc theo vùng (nhóm 通常 / -Q), mã truy xuất theo `trace_lane`, ghi chú bao bì bắt buộc có điều kiện — L
- [FE] Chọn/chụp ảnh (`accept="image/*" capture`), upload, thumbnail, thay ảnh, disable khi dòng chưa lưu — M
- [FE] Dialog xác nhận (giữ Idempotency-Key, M_227) + dialog kết quả (M_209, bảng lô, link SCR-031/SCR-037 theo quyền) + map lỗi 409/422 cập nhật panel — M
- [QA] Viết test case: ma trận P0 (từng field), lớp A/B ADR-008, quy tắc -Q (gồm ngoại lệ ambient Q&A-B05), trace beef/rice, phiên bản ngưỡng theo ngày đến, RBAC — M
- [QA] Chạy test danh sách / form dòng / ảnh (định dạng, cỡ, SHA-256 trong audit) — M
- [QA] Chạy test luồng xác nhận: bấm 2 lần / mạng chập chờn cùng key, 2 tab khác key (M_208), kiểm DB `lots`/`inventory_movements`/`lot_status_events`/`deviations` đúng số — M
- [BrSE] Làm rõ 7 điểm INFERRED: mốc phiên bản = ngày đến; NSX không P0; quy tắc -Q áp ở xác nhận; bao bì hỏng không tự cách ly; thiếu mã trace = trace failure; giờ đến = lúc tạo phiếu; ảnh ≤10MB; có chặn lô 消費期限 đã hết hạn tại cửa kho không — S

### 7. Gap / mâu thuẫn
| # | Vị trí | Mô tả | Đề xuất |
|---|---|---|---|
| G22-1 | spec#9 RPC bước 6 (`deviation_type = 'temperature'` / `'traceability'`) vs `database-design.md` ERD `deviations.deviation_type "temp_out_of_range\|trace_missing\|zone_mismatch"` | **Giá trị enum lệch** giữa spec và DB. SCR-031 spec#5-7.2 cũng đọc `deviation_type`. | Sửa thiết kế: chốt enum DB (`temp_out_of_range`, `trace_missing`), cập nhật spec 022/031. |
| G22-2 | spec#9 RPC bước 6 (insert `lot_status_events (from_status = null, …, reason = 'INBOUND_OK' …)`) vs `database-design.md` ERD `lot_status_events.event_type "quarantine\|hold\|release\|dispose"` | Sự kiện tạo lô lúc nhập không có `event_type` hợp lệ (enum không có `receive`/`create`). | Sửa thiết kế: thêm `event_type = 'create'` (hoặc `inbound`) hoặc không ghi status event cho lô `available`; cập nhật timeline SCR-031. |
| G22-3 | spec#9 RPC bước 2 (tìm theo `key`, endpoint, `receipt_id`; "key đã dùng cho phiếu khác → 409") vs `database-design.md` §3.3 `idempotency_keys (key PK, endpoint, response jsonb, created_at)` | Bảng không có cột tham chiếu đối tượng (receipt_id) → không phân biệt được key dùng cho phiếu khác. | Sửa thiết kế: thêm `ref_id`/`request_hash`; dùng chung cho `quarantine_lot` (SCR-031). |
| G22-4 | spec#5-11.13.3 (SHA-256 lưu metadata + `audit_log.after`) vs ERD `inbound_lines.photo_sha256` | DB có cột `photo_sha256` nhưng spec không ghi vào cột. | Giả định: ghi cả cột `photo_sha256`; sửa spec. |
| G22-5 | spec#5-8.3, spec#5-4.2.2 | Chọn sai nhà cung cấp không sửa được; xóa phiếu draft là P1 "chưa thiết kế" → phiếu rỗng sai bị bỏ lại vĩnh viễn. | Issue làm rõ (PO): đưa xóa phiếu draft rỗng vào phạm vi hay chấp nhận rác. |
| G22-6 | spec#5-11.11.3, spec#5-9.2 | Quy tắc khu -Q ở bước xác nhận là INFERRED; ambient chưa có `A-Q-xx` (Q&A-B05) → nhánh ngoại lệ M_314 phụ thuộc master. | Giả định theo spec; issue BrSE Q&A-B05. |
| G22-7 | spec#5-11.6.2, spec#5-11.8.2, spec#5-11.12.3 | Chưa chốt: chặn lô 消費期限 đã hết tại cửa kho? bao bì hỏng có cách ly? cách hiểu "トレーサビリティ不足". | Issue BrSE (đã gộp vào task BrSE). |
| G22-8 | spec#7 (dòng `driver`) | Vai trò `driver` không có trong 9 vai trò (xem G18-4). | Gộp với G18-4. |
| G22-9 | spec#5-11.11.5 | Kiểm sức chứa vị trí (FR-INV-01) ngoài phạm vi phase này. | Ghi out-of-scope trong issue. |

---

## SCR-030 — 在庫照会 (Tra cứu tồn kho theo lô)

### 1. Mục đích & vai trò
- Tra cứu tồn kho theo lô với 10 điều kiện lọc; thấy ngay lô bị chặn (cách ly, 保留, 消費期限) và lô chỉ cảnh báo (賞味期限). Chỉ đọc.
- Mọi vai trò nghiệp vụ (9 vai trò) xem; chưa có vai trò → 403.

### 2. Khu vực / component
- Vùng lọc 10 điều kiện (SKU, mã lô, supplier, hạn từ/đến, loại hạn, vùng nhiệt, trạng thái chọn nhiều, vị trí phụ thuộc vùng, nhãn cảnh báo hạn) + 検索 / 条件クリア; URL sync; chỉ áp khi bấm.
- Dòng tóm tắt (số lô, tổng tồn, tổng khả dụng trên toàn bộ kết quả).
- Bảng lô 12 cột, sắp cố định FEFO (hạn → ngày nhập → id); badge 要移動, 廃棄承認待ち; phân trang 50.

### 3. Dữ liệu
- Bảng/view: `lot_stock_view` (mở rộng, `security_invoker`), `lots`, `skus`, `locations`, `inbound_lines` → `inbound_receipts` → `suppliers`, `lot_disposal_requests` (pending), tham số `consumption_warning_days`.
- API: `GET /api/lots` (to-be: 10 filter + summary), `GET /api/skus|suppliers|locations` (dùng chung SCR-022).
- RPC: `search_lot_stock(p_filter jsonb, p_page, p_page_size)` (security invoker, trả rows + total + summary).
- Index: `lots (sku_id, status, expiry_date, received_at)`, thêm `lots (location_id)`, `lots (lower(lot_code) text_pattern_ops)`.
- BR: BR-EXP-01/02, BR-FEFO-01, BR-INV-01, BR-TIME-01, BR-TEMP-03; FR-INV-05/06, FR-REC-05. ADR: không nêu trực tiếp.

### 4. Validation / trạng thái / luồng đặc biệt
- Nhãn hạn (thứ tự): 消費期限 `days_left ≤ 0` → 消費期限到達 (đỏ, chặn); 消費期限 `1..N` (N=3) → 消費期限間近; 賞味期限 `days_left < 0` → 賞味期限切れ (cho phép). Chỉ tính cho lô còn hàng chưa hủy.
- `qty_available` = 0 khi `status ≠ available` hoặc 消費期限到達; còn lại `on_hand − allocated`. Không trừ lý do phụ thuộc khách (xem SCR-042).
- `days_left` tính trong SQL theo `app_today()` (JST), không theo đồng hồ trình duyệt.
- Validation: mã lô `Format_Code` ≤50 (M_13), hạn từ ≤ hạn đến (M_303).
- Trạng thái: loading (giữ số cũ mờ), empty M_32, error M_40/M_41 + 再試行, lỗi điều kiện. Hiệu năng ≤ 2s / 50 dòng / dữ liệu 3 năm (INFERRED).

### 5. Ràng buộc giờ lái xe 2024 — **Không**

### 6. Sub-task đề xuất (9)
- [BE] Mở rộng `lot_stock_view`: temp_zone, NSX, vị trí (+ is_quarantine), supplier (left join chuỗi nhập), `expiry_flag` CASE, `pending_disposal`, công thức `qty_available` mới — M
- [BE] Lưu tham số `consumption_warning_days` (=3) ở bảng tham số hệ thống, view đọc tham số thay vì hằng số — S
- [BE] RPC `search_lot_stock` + `GET /api/lots` (zod 10 filter, status csv mặc định 3 trạng thái, escape like, summary, paging) + index mới — M
- [BE] Kiểm hiệu năng: sinh dữ liệu 3 năm, EXPLAIN, đạt ≤ 2s — M
- [FE] Vùng lọc 10 điều kiện + URL sync + áp khi bấm/Enter + multi-select trạng thái + vị trí phụ thuộc vùng (reset khi khác vùng) + clear về mặc định — M
- [FE] Tóm tắt + bảng lô (sắp cố định, badge loại hạn/nhãn hạn/trạng thái, tooltip lý do khả dụng = 0, 要移動, 廃棄承認待ち, link SCR-031) + phân trang + các trạng thái màn — M
- [QA] Viết test case: biên nhãn hạn (days_left −1/0/1/3/4 × 2 loại hạn), qty_available theo trạng thái, AND 10 filter, FEFO, supplier filter loại lô seed — M
- [QA] Chạy test + kiểm số tổng khớp toàn bộ kết quả (không chỉ trang) — M
- [BrSE] Xác nhận N = 3 ngày (`consumption_warning_days`); giả định 1 kho → mọi vai trò xem toàn kho; mặc định ẩn lô 廃棄/出庫完了 — S

### 7. Gap / mâu thuẫn
| # | Vị trí | Mô tả | Đề xuất |
|---|---|---|---|
| G30-1 | spec#6 ("lưu ở bảng tham số hệ thống") vs `database-design.md` (không có bảng tham số / settings nào) | Không có bảng để lưu `consumption_warning_days`. | Sửa thiết kế: thêm bảng `app_parameters` (key, value, updated_by/at, audit) hoặc tạm hằng số có ghi chú. |
| G30-2 | spec#5-2.8.2 ("Bỏ chọn hết = không lọc (hiện cả 4)") vs spec#5-2.8.1 (5 trạng thái) | Đếm sai: có 5 trạng thái lưu. | Giả định "hiện cả 5"; sửa spec. |
| G30-3 | spec#5-4.8.2 (要移動 chỉ cho `quarantine`) vs SCR-031 spec#5-3.9 (`quarantine` / `on_hold`) | Điều kiện hiện badge 要移動 khác nhau giữa 2 màn. | Sửa thiết kế: thống nhất (đề xuất gồm `on_hold`, cùng hàm dùng chung). |
| G30-4 | spec#7 (FR-INV-06 "倉庫権限を尊重" → INFERRED 1 kho) | Bối cảnh Product B là **chuỗi** kho lạnh; nếu nhiều kho thì phải lọc theo `warehouse_id` — DB chưa có cột này. | Issue làm rõ BrSE/PM (phạm vi đa kho), rủi ro thiết kế lớn nếu đổi. |
| G30-5 | spec#9 hiệu năng (≤ 2s, INFERRED theo NFR-PERF) | Chỉ tiêu suy ra, không có số liệu khối lượng cụ thể. | Giả định; xác nhận khối lượng dữ liệu với khách. |
| G30-6 | spec#5-4.11.3 | Khả dụng ở màn này ≠ khả dụng thực khi phân bổ (thiếu cửa sổ giao, 日付逆転) — có thể gây hiểu nhầm. | Giả định theo spec; thêm chú thích UI nếu PO muốn. |

---

## SCR-031 — ロット詳細・履歴 (Chi tiết lô & lịch sử)

### 1. Mục đích & vai trò
- Xem đầy đủ thông tin 1 lô và dòng thời gian sự kiện bất biến (nhập, di chuyển, phân bổ, hủy phân bổ, cách ly, 保留, giải phóng, hủy, xuất, điều chỉnh); điểm bắt đầu truy xuất lô; điểm cách ly thủ công.
- Mọi vai trò nghiệp vụ xem. Cách ly (`lot:quarantine`): `quality`, `warehouse_lead`. `admin` **không** cách ly được (khác prototype). `auditor` thấy correlation ID và link SCR-037.

### 2. Khu vực / component
- Header lô (mã lô, badge trạng thái, badge nhãn hạn, 廃棄承認待ち).
- Thông tin lô 12 trường (SKU, vùng, loại hạn, hạn + số ngày, NSX, supplier, phiếu nhập link SCR-022, nhiệt độ lúc nhập + phiên bản ngưỡng chụp lại, vị trí + 要移動, tồn, phân bổ, khả dụng + lý do).
- Nút 隔離 + dialog cách ly (lô đối tượng, lý do, deviation liên quan, bằng chứng file/số tham chiếu).
- Timeline sự kiện (lọc loại, 50 thẻ/lần + さらに表示, gộp theo correlation_id, actor, correlation ID copy).
- Bảng deviation liên quan. Link mở SCR-037.

### 3. Dữ liệu
- Bảng/view: `lot_stock_view`, `inbound_lines`, `temp_zone_policy_versions`, `deviations`, `lot_disposal_requests`, `inventory_movements`, `lot_status_events`, `date_reversal_exception_requests` (dòng phụ 日付逆転), view mới `lot_event_timeline`, `idempotency_keys`, `audit_log`, bucket `quality-evidence`.
- API: `GET /api/lots/{id}` (to-be, `allowedActions`), `GET /api/lots/{id}/events` (mới, keyset `before`, `kinds`), `POST /api/lots/{id}/quarantine` (mới, Idempotency-Key), `POST /api/evidence` (mới, dùng chung SCR-037).
- RPC: `quarantine_lot(p_lot_id, p_reason, p_deviation_id, p_evidence_ref, p_idempotency_key)` — 7 bước (role, idempotency, for update, kiểm trạng thái + phân bổ, update + status event, gắn deviation, audit).
- BR: BR-INV-02/03/04, BR-EXP-01/02, BR-TEMP-01/03, BR-DATE-02, BR-DELWIN-01; FR-INV-03/05, state machine lô. ADR: ADR-002, ADR-005 (ngoại lệ 日付逆転), ADR-007 (append-only).

### 4. Validation / trạng thái / luồng đặc biệt
- Chỉ chuyển `available → quarantine` trên màn này; nút chỉ hiện khi `available` (không hiện nút disable cho bước nhảy sai); `qty_allocated > 0` → disable (M_302, Q&A-B04). Server: M_301 `INVALID_TRANSITION`, M_302 `LOT_ALLOCATED`, 422 deviation không hợp lệ.
- Lý do `Format_Reason` 10–500 (M_06), lưu với tiền tố `MANUAL:`. Bằng chứng không bắt buộc: file PDF/JPG/PNG ≤10MB (M_316) hoặc số tham chiếu 1–100.
- Idempotency-Key sinh khi mở dialog; gửi lại không cách ly 2 lần.
- Timeline chỉ đọc tuyệt đối; sửa sai = thẻ mới (bút toán đảo). Link tham chiếu chỉ khi người xem có quyền xem màn đích.
- Lô 消費期限到達 vẫn cách ly được. Di chuyển vật lý sang -Q là thao tác riêng (chưa có màn).
- Trạng thái màn: loading, not found, error, timeline rỗng (初期データ), theo từng trạng thái lô (available / có phân bổ / quarantine / on_hold / chờ hủy / disposed-depleted / hết 消費期限).

### 5. Ràng buộc giờ lái xe 2024 — **Không**
- Timeline sự kiện `ship` hiển thị `便 {route_no}` (chỉ tham chiếu tuyến, không có logic giờ lái).

### 6. Sub-task đề xuất (11)
- [BE] View `lot_event_timeline` (union `inventory_movements` + `lot_status_events`, gộp theo `correlation_id`, map 10 loại) + `GET /api/lots/{id}/events` (keyset `occurred_at,id`, `kinds`, limit) + index `(lot_id, occurred_at)` — L
- [BE] `GET /api/lots/{id}` to-be: lot + thông tin nhập chụp lại + deviations + pendingDisposal + `allowedActions` theo vai trò & state machine — M
- [BE] RPC `quarantine_lot` + `POST /api/lots/{id}/quarantine` (idempotency, for update, M_301/M_302, gắn deviation, audit) — M
- [BE] `POST /api/evidence` dùng chung (multipart, kiểm loại/cỡ M_316, trả `evidence_ref`, signed URL 5 phút khi xem) — S
- [Infra] Bucket Storage `quality-evidence` private (đường dẫn `{yyyy}/{uuid}`) + policy — S
- [FE] Header + thông tin lô 12 trường (badge trạng thái/hạn, 要移動, lý do khả dụng = 0, link SCR-022) + bảng deviation + link SCR-037 theo quyền + nút quay lại giữ bộ lọc SCR-030 — M
- [FE] Timeline: bảng ánh xạ 10 loại sự kiện (nhãn, màu, biến động, nội dung), lọc loại, さらに表示 keyset, copy correlation ID, link theo quyền — L
- [FE] Nút + dialog cách ly (M_305, lý do + bộ đếm, chọn deviation, file hoặc số tham chiếu, Idempotency-Key, map lỗi, reload sau thành công M_306) — M
- [QA] Viết test case: hiển thị nút theo vai trò × trạng thái lô, chặn khi có phân bổ, timeline đủ loại sự kiện + gộp correlation, phân trang keyset, bằng chứng file/số — M
- [QA] Chạy test + đồng thời (cách ly trong lúc phân bổ `allocate_lot` → không phân bổ được lô vừa cách ly; gửi lại cùng key) + kiểm audit_log — M
- [BrSE] Làm rõ: Q&A-B04 (chặn cách ly khi có phân bổ), Q&A-B12 (đường tắt quarantine → available/disposed), cách ly thủ công không tự mở deviation, màn 移動 sang -Q ngoài phạm vi — S

### 7. Gap / mâu thuẫn
| # | Vị trí | Mô tả | Đề xuất |
|---|---|---|---|
| G31-1 | spec#9 #2 (`kinds` gồm `receive, move, allocate, unallocate, quarantine, hold, release, dispose, ship, adjust`) vs `database-design.md` `lot_status_events.event_type` + chưa thấy enum `inventory_movements.movement_type` cho `allocate`/`unallocate`/`dispose` | Cần đối chiếu enum movement_type; sự kiện tạo lô lúc nhập không có event_type (G22-2). | Sửa thiết kế: chốt 1 danh sách enum dùng chung cho SCR-022/031. |
| G31-2 | spec#5-7.2 (`deviation_type` → 温度 / トレーサビリティ) vs ERD (`temp_out_of_range\|trace_missing\|zone_mismatch`) | Cùng lỗi enum G22-1; thiếu nhãn cho `zone_mismatch`. | Gộp với G22-1. |
| G31-3 | spec#5-5.3.1 | Cách ly thủ công không tạo deviation mới vì `deviations.source` chỉ có `inbound\|outbound\|logger` — INFERRED. | Issue BrSE; giả định theo spec. |
| G31-4 | spec#5-5.5.4 | Di chuyển vật lý sang khu -Q (FR-INV-03) chưa có màn → lô treo「要移動」không có cách xử lý trong hệ thống. | Issue PM: thêm màn 移動 vào backlog phase sau hoặc chấp nhận. |
| G31-5 | spec#5-7.1.1 | Màn chi tiết deviation (F08) chưa spec → không link. | Out-of-scope, ghi chú. |
| G31-6 | spec#5-3.9 vs SCR-030 spec#5-4.8.2 | Điều kiện 要移動 lệch (xem G30-3). | Gộp với G30-3. |
| G31-7 | spec#9 #3 (`evidence_ref` ≤ 200) vs spec#5-5.4.1 (số tham chiếu 1–100) | Giới hạn độ dài khác nhau giữa UI và API (API phải chứa cả đường dẫn file). | Giả định: UI 100 cho số tham chiếu, API 200; ghi rõ trong spec. |
| G31-8 | spec#9 RPC bước 2 | Idempotency phụ thuộc bảng `idempotency_keys` thiếu cột tham chiếu (G22-3). | Gộp với G22-3. |

---

## Gap ưu tiên cao (gom cho backlog)

1. **G16-1** — SCR-016 thiếu 2 tham số engine giờ lái (`long_day_threshold_h`, `drive_2week_anchor_date`) dù DB-design và BR-DRV-06/10 có → sửa thiết kế trước khi làm engine ADR-006.
2. **G16-6 / G16-7 / G16-8** — rủi ro tuân thủ giờ lái 2024: tuyến công bố trước ngày hiệu lực chạy theo bản cũ; điều kiện 労使協定 chưa thiết kế (Q&A-B07); công thức tăng ca chưa chốt (Q&A-B06); giá trị seed cần kiểm nguồn luật (OPS-LAW-01).
3. **G22-1 / G22-2 / G31-1** — enum lệch giữa spec và DB (`deviation_type`, `lot_status_events.event_type` cho lô mới nhập) → chốt trước migration.
4. **G22-3** — `idempotency_keys` thiếu cột tham chiếu đối tượng → không thực hiện được "key dùng cho phiếu khác → 409".
5. **G30-1** — không có bảng tham số hệ thống cho `consumption_warning_days`.
6. **G18-4** — vai trò `driver` được nhắc ở 3 màn nhưng không nằm trong 9 vai trò.
7. **G30-4** — giả định 1 kho trong khi Product B là chuỗi kho → nếu đa kho thì thiếu `warehouse_id` toàn hệ thống.
8. **G18-2** — thu hồi phiên Supabase bằng cách đụng schema `auth` cần spike.

## Câu hỏi chưa giải quyết
- Ai sở hữu migration dùng chung (`deviations`, `idempotency_keys`, `lot_status_events`, `locations`, `suppliers`) — epic F02 hay epic nền tảng? (ảnh hưởng thứ tự issue).
- Impact API của SCR-016 phụ thuộc bảng `route_versions` (F07, SCR-060/062) — cần xếp sau migration F07 hay stub đếm 0 khi chưa có tuyến?
