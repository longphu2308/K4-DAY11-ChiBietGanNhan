# 04 — Tự soát 9 mục (thứ tự khai báo)

Soát theo **đúng thứ tự** này trên bản export nháp trước khi export bản cuối và khoá. `python3 lab11.py selfqc r1_craft` tự động kiểm được một phần; phần còn lại bạn tick tay
bằng `- [ ]` trong `selfqc.md` mà lệnh sinh ra.

1. **Phạm vi:** mọi vật cao ≥ `H` (40 px) trong vùng hợp lệ đều có box; vật thấp hơn `H` không box (không phải lỗi
   thiếu).
2. **`lens_border` và `ego_body`:** `lens_border` (đã import) phủ đúng vành đen ngoài vòng kính; `ego_body` (tự vẽ)
   phủ thân xe/gương/tay lái **khi nhìn thấy**. Không thêm ego vào hai frame ngoại lệ nêu ở R07.
3. **Class:** đúng bảng 6 class (`docs/02-rules-vi.md`); ThreeWheeler không bị gọi Bus/Truck; van chở người là Car.
4. **Rider:** người lái + xe hai bánh = một `Bike`; người dắt xe tách thành `Pedestrian` + `Bike`; người ngồi trong
   xe không box.
5. **Geometry:** box bám phần nhìn thấy trên **ảnh gốc**, không nắn thẳng vật cong ở rìa; không một box phủ cả dãy
   xe.
6. **Attribute:** vật bị vòng kính/khung cắt → `truncated`; bị vật khác che → `occluded` — không lẫn hai attribute
   này vào nhau.
7. **Thiếu/trùng:** không hai box cho một vật; không bỏ sót vật nhỏ ở rìa mà vẫn ≥ `H`.
8. **`ignore_region`:** cụm không tách được → `crowd_or_group`; vật không đọc được → `unreadable`; vùng riêng tư →
   `privacy_or_policy`; mỗi polygon có đúng một `reason`; không box nào nằm trong ignore region.
9. **Tên task và định dạng:** tên task có `raw_fisheye`; export đúng **CVAT for images 1.1**.

Bỏ sót một mục sau khi khoá: ghi vào `submission/40_decision_log.csv`, không mở khoá để sửa âm thầm.
