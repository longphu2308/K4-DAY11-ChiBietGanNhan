# 02 — Luật gán nhãn (rules v1.0.0)

Luật này là **quy ước của khoá học**, không phải chuẩn ngành. Mọi rule có `id` để trích trong `findings.csv` cột
`rule_id` và trong `20_guideline_patch.md` khi bạn đề xuất luật mới (bump `rules_version`).

## Phạm vi

- **R01 — Ngưỡng chiều cao:** vật cao ≥ 40 px (`H=40`, đo trên ảnh gốc) trong vùng hợp lệ phải có box. Vật thấp
  hơn không box — đây không tính là lỗi thiếu.
- **R02 — Vẽ trên ảnh gốc:** box/polygon bám phần **nhìn thấy trên ảnh fisheye gốc**. Không tưởng tượng ảnh đã
  undistort, không "nắn thẳng" vật cong ở rìa.

## 6 class

| Class | Gồm |
|---|---|
| `Car` | Ô tô con, xe bán tải nhẹ chở người, **van chở người** (R04) |
| `Bus` | Xe buýt, **minibus** (R04) |
| `Truck` | Xe tải, pickup/xe tải nhỏ, **máy kéo** (R04) |
| `ThreeWheeler` | Xe ba bánh chở người/hàng: auto-rickshaw, e-rickshaw, xích lô (R04) |
| `Bike` | Xe hai bánh (có hoặc không người lái, xem R03 luật rider) |
| `Pedestrian` | Người đi bộ, người dắt xe (R03) |

- **R03 — Rider:** người lái + xe hai bánh = **một** box `Bike` duy nhất. Người **dắt** xe (không ngồi lên) = một
  box `Pedestrian` **và** một box `Bike` tách riêng. Người ngồi **trong** một phương tiện khác (ô tô, xe buýt)
  **không** box riêng.
- **R04 — Ánh xạ phương tiện đặc biệt:** xe ba bánh chở người/hàng → `ThreeWheeler`; van chở người → `Car`; minibus
  → `Bus`; xe bán tải nhỏ hoặc máy kéo → `Truck`. Không gọi ThreeWheeler là Bus/Truck.

## Attribute

- **R05 — `truncated` vs `occluded`:** `truncated` = vật bị cắt bởi vòng kính hoặc biên khung hình (hình học, suy
  được từ vòng kính). `occluded` = vật bị **vật khác** che (phán đoán bằng mắt). Một vật có thể vừa truncated vừa
  occluded — hai attribute độc lập, không lẫn vào nhau.

## `ignore_region`

- **R06 — Lý do (`reason`) hợp lệ:** `ego_body` (thân xe/gương/tay lái của xe gắn camera), `lens_border` (vành đen
  ngoài vòng kính), `crowd_or_group` (cụm vật không tách được từng cái), `unreadable` (vật không đọc được vì mờ/che
  gần hết), `privacy_or_policy`. Mỗi polygon ignore phải có đúng một `reason`.
- **R07 — `ego_body`:** học viên tự vẽ polygon `ego_body` ở **mọi frame có thân xe ego** mình phụ trách — thân xe ego thấy
  được ở 46/48 frame ADASIND. Frame không thấy thân xe (ví dụ 006840, 271039) thì **không vẽ**: polygon thừa cũng là lỗi.
- **R08 — `lens_border`:** công cụ đã **import sẵn** 2 polygon mỗi frame từ vòng kính đo trước. Học viên chỉ
  **soát lại** (không tự vẽ mới), sửa nếu polygon lệch vòng kính thật.
- **R09 — Không box trong ignore:** không có box nào được nằm ≥50% trong một polygon `ignore_region` (matcher coi
  đó là don't-care, không tính TP cũng không tính FP — xem `docs/05-taxonomy-vi.md`).

## Mức ưu tiên soát của bài học (P0–P3)

Đây là thứ tự **xử lý bài lab**, không phải mức rủi ro an toàn hay quy tắc sản xuất. `center/mid/edge` chỉ là vị trí
trên ảnh; **không** cho biết vật gần hay xa xe.

- **R10 — P0:** sai phạm vi dữ liệu (ví dụ `ego_body`, `lens_border`, hoặc ignore che nhầm vùng) khiến phép so sánh
  và việc chọn đối tượng cần gán nhãn không còn đáng tin.
- **P1:** thiếu/thừa/sai class hoặc hình học của đối tượng trong phạm vi, cần sửa để đáp ứng rule hiện hành.
- **P2:** attribute hoặc khác biệt nhỏ cần soát lại; giải thích vì sao nó không đổi quyết định gán nhãn chính.
- **P3:** lỗi trình bày hay ghi chép bằng chứng, không đổi nhãn; sửa trước khi nộp.

Nếu chưa đủ bằng chứng để xếp mức, ghi lý do và hỏi người soát; không suy mức từ zone bán kính.

## Không thuộc phạm vi so sánh

- **R11 — `occluded` và `ignore_region.reason` không so với reference** khi chấm khác biệt — cả hai đều là phán
  đoán, chỉ dùng để soát chéo giữa người với người (vai QA), không dùng để tính đúng/sai với reference.

Đề xuất sửa luật này: viết vào `20_guideline_patch.md`, bump số `rules_version` (vd `v1.0.0` → `v1.1.0`), không tự
ý sửa file này.
