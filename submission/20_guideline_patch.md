# Guideline patch

- **Rule mới đề xuất:**
  **R12 — Tiêu chí định lượng cho cụm đối tượng ở xa và chồng lấn (Distant Crowd & Severe Occlusion):**
  Đối với các đối tượng thuộc class `Pedestrian` hoặc `ThreeWheeler` ở khoảng cách xa (nằm trong zone `center` hoặc `mid`):
  1. Nếu khoảng cách biên nhìn thấy giữa hai đối tượng liền kề $< 3\text{ px}$, hoặc một đối tượng bị che khuất $> 50\%$ diện tích bởi đối tượng khác cùng loại khiến không thể xác định điểm tiếp đất chính xác: **nghiêm cấm** vẽ bounding box đơn lẻ cho từng đối tượng.
  2. Bắt buộc vẽ một polygon `ignore_region` bao trùm toàn bộ nhóm đối tượng đó và gán thuộc tính `reason = crowd_or_group`.
  3. Chỉ vẽ box riêng lẻ khi đối tượng thỏa mãn đồng thời: $H \ge 40\text{ px}$, diện tích nhìn thấy $> 50\%$, và có ranh giới rõ ràng tách biệt với các đối tượng xung quanh.

- **Áp dụng cho:**
  Class `Pedestrian`, `ThreeWheeler`, nhãn `ignore_region` (attribute `reason = crowd_or_group`), áp dụng cho tất cả các zone trên ảnh fisheye gốc (đặc biệt là zone `center` và `mid`).

- **Vì sao luật hiện tại (`docs/02-rules-vi.md`) không đủ:**
  Quy chuẩn hiện tại (v1.0.0, điều R01 và R06) chỉ nêu ngưỡng chung $H \ge 40\text{ px}$ và liệt kê `crowd_or_group` như một nhãn hợp lệ, nhưng không cung cấp tiêu chí định lượng về khoảng cách pixel tối thiểu hay mức độ che khuất để kích hoạt vùng ignore. Do thiếu định lượng, annotator đã cố gắng bắt từng người đi bộ ở xa tại frame `adasind_117120.jpg` sinh ra hàng loạt box `SPURIOUS` (L10, L11, L12) gây sai lệch nghiêm trọng chỉ số Precision và bất đồng lớn với reference.

- **`rules_version` mới:**
  `v1.1.0` (nâng cấp từ `v1.0.0`)

- **Hiệu lực từ:**
  Áp dụng chính thức từ round `rework` và làm chuẩn đánh giá cho toàn bộ các tập dữ liệu mở rộng sau này.
