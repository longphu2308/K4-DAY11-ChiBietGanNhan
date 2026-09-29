# 06 — 6 card ngộ nhận (clinic P1)

Mỗi card có ba lựa chọn: **đúng**, **sai**, **mơ hồ**. Đọc lý do trước khi quyết định ca thật của mình.

## Card 1 — Bảng class

*"ThreeWheeler chỉ là một dạng phụ của Truck, gọi Truck cũng được."*

- **Sai.** ThreeWheeler là class riêng (`docs/02` R04) vì hình học và cách di chuyển khác Truck rõ rệt trên
  fisheye. Gọi Truck làm mất tín hiệu mà bài học cần đo.

## Card 2 — Rider

*"Người lái xe máy chở thêm một người thì vẽ hai box: một Bike, một Pedestrian cho người ngồi sau."*

- **Sai.** Luật R03: xe hai bánh + (mọi) người trên xe = **một** box `Bike`, dù chở một hay hai người. Chỉ người
  **dắt** xe (đứng ngoài, không ngồi lên) mới tách thành `Pedestrian` + `Bike`.

## Card 3 — ThreeWheeler

*"Xe ba bánh chở hàng (không chở người) thì không tính là ThreeWheeler, vì ThreeWheeler chỉ chở khách."*

- **Mơ hồ, quy ước lab chọn rõ:** R04 gộp cả ba bánh chở người **và** chở hàng vào `ThreeWheeler` (auto-rickshaw,
  e-rickshaw, xích lô). Không tách theo mục đích chở.

## Card 4 — `ego_body`

*"`ego_body` chỉ cần vẽ ở frame nào nhìn rõ tay lái, frame nào không thấy gương thì bỏ qua."*

- **Sai vì phải nhìn ảnh trước khi quyết định.** R07: vẽ `ego_body` khi thực sự thấy thân xe/gương/tay lái. Hai
  frame `adasind_006840.jpg` và `adasind_271039.jpg` trong pack không có vùng ego cần vẽ; thêm polygon ở đó là thừa.

## Card 5 — `lens_border`

*"Vẽ lại `lens_border` bằng tay cho chuẩn hơn bản import, vì import có thể lệch."*

- **Mơ hồ → hành động rõ:** không vẽ **mới**. `lens_border` được sinh từ vòng kính đo trước và import sẵn (R08);
  bạn chỉ **soát và sửa điểm lệch** nếu có, không xoá vẽ lại từ đầu — vẽ tay polygon thuần hình học này không dạy
  phán đoán gì, chỉ tốn thời gian.

## Card 6 — `crowd_or_group`

*"Một hàng 5 xe máy đậu sát nhau, đếm được từng cái, thì vẽ 5 box `Bike` bình thường, không cần ignore."*

- **Đúng, nếu đếm được từng cái.** `crowd_or_group` (R06) chỉ dùng khi vật lý không tách được ranh giới từng đối
  tượng (chồng lấn quá nhiều để vẽ box riêng biệt có nghĩa). Đếm được thì vẽ box thường, không ignore.
