# Third-party notices

Bảng dưới ghi mọi thành phần bên thứ ba trong repo này (`Day11-SVM360-Fisheye-Lab-pilot`) và trong repo Student build
ra từ nó. Điều khoản gốc tại trang chủ của từng nguồn mới là căn cứ cuối cùng; bảng này chỉ tóm tắt.

## ADASIND (frame + box gốc)

- **Nguồn:** Zenodo, DOI phiên bản `10.5281/zenodo.7900965` (concept DOI `10.5281/zenodo.7851541`), tác giả Om Singh,
  Anupam Biswas, Rajdeep Paul (NIT Silchar).
- **Giấy phép:** CC BY 4.0 — https://creativecommons.org/licenses/by/4.0/legalcode.
- **Điều kiện lab giữ:** attribution đủ (`learner/ATTRIBUTION.txt`), ghi rõ đã sửa gì, không thêm điều kiện ngoài
  giấy phép gốc.
- **Trích dẫn:** Singh O., Biswas A., Paul R., ADASIND dataset, Zenodo, 2023.

## Teaching reference, polygon ignore, class map (do Lab Coach tạo)

- **Giấy phép:** CC BY 4.0, do Lab Coach tạo từ box gốc ADASIND.
- **Điều kiện:** ghi rõ là bản dẫn xuất, không phải "gold set" đã được nhiều người kiểm chứng; gọi đúng tên
  "teaching reference".

## Ultralytics / YOLO26m (pre-label đóng băng)

- **Giấy phép:** AGPL-3.0.
- **Điều kiện lab giữ:** chỉ commit output đã đóng băng (`assets/model-yolo26m.xml`), không commit trọng số
  `.pt`/`.onnx`; repo Student không `import ultralytics`; học viên không chạy model, chỉ đọc file XML tĩnh.
- **Trích dẫn model:** Ultralytics YOLO26m, 2026.

## CVAT

- **Phiên bản:** CVAT Community v2.74.1, dùng lại stack Day 2.
- **Giấy phép:** MIT.
- **Ghi chú:** quality report (accuracy/conflict) chạy trên bản self-hosted của lớp — đây không phải tính năng
  Enterprise, xem `learner/docs/09-support-stretch-vi.md`.

## Docker Desktop

- Miễn phí cho dùng cá nhân/giáo dục; đã cài từ Day 2.

## WoodScape (chỉ Lab Coach chiếu minh hoạ, không có trong lane học viên)

- **Điều khoản:** Valeo ToU cho phép giảng dạy, cấm thương mại, cấm vận hành xe, không cho phát lại. Không có pixel
  WoodScape trong repo pilot hay Student.

## Ảnh bãi đỗ Wikimedia Commons

- `learner/assets/parking/parking-lot-core.jpg`: [Parkinglot empty](https://commons.wikimedia.org/wiki/File:Parkinglot_empty.jpg), Öljylautta, tác giả công bố public domain; bản xem trước 960 px.
- `learner/assets/parking/parking-lot-contrast.png`: [Apartment Complex Parking Lot 1](https://commons.wikimedia.org/wiki/File:Apartment_Complex_Parking_Lot_1.png), TylerMascola, CC0 1.0; bản xem trước 960 px.
- Hai ảnh là mẫu luyện nhãn vạch trên ảnh bãi đỗ camera thường, không phải ảnh SVM hoặc ground truth fisheye.

## Không có trong repo này

- Không có script chấm điểm tự động hoặc ngưỡng đạt/trượt. Rubric 100 điểm cho bài Day 11 ở `learner/RUBRIC.md`; `make check` chỉ kiểm cấu trúc.
- Không có trọng số model (`.pt`, `.onnx`), không có token/`.env`/mật khẩu CVAT.
