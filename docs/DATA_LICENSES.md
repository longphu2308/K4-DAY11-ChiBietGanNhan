# DATA_LICENSES.md

## ADASIND

- **Tác giả:** Om Singh, Anupam Biswas, Rajdeep Paul (NIT Silchar).
- **DOI phiên bản:** 10.5281/zenodo.7900965 (v1.0.0). **DOI concept:** 10.5281/zenodo.7851541.
- **Giấy phép:** CC BY 4.0 — https://creativecommons.org/licenses/by/4.0/legalcode.
- **Nghĩa vụ theo §3(a) của giấy phép:** ghi tên tác giả, tên dữ liệu, đường dẫn giấy phép, và **chỉ rõ đã sửa gì**
  so với bản gốc. Không thêm điều kiện nào ngoài giấy phép gốc lên phần dữ liệu gốc.

### Đã sửa gì (bản trong repo này khác bản gốc Zenodo)

1. Chọn tập con 48 frame từ toàn bộ dataset gốc.
2. Đổi định dạng CSV sang CVAT XML 1.1; ánh xạ lại nhãn theo bảng 6 class của lab (`docs/05-taxonomy-vi.md`).
3. Sửa tay box pre-label thành "teaching reference" — bản nháp dùng để dạy, **không phải** gold set.
4. Thêm polygon `ignore_region` (`ego_body`, `lens_border`, và các vùng không đọc được) không có trong bản gốc.
5. Làm mờ (blur) khuôn mặt và biển số xe trước khi đưa frame vào repo.
6. Thêm pre-label YOLO26m (Ultralytics, AGPL-3.0) — chỉ là output tĩnh đã đóng băng, không phải box gốc ADASIND.

### Trích dẫn

Singh O., Biswas A., Paul R., ADASIND dataset, Zenodo, 2023, doi:10.5281/zenodo.7900965.

## Nhãn do lab tạo (teaching reference, class map, polygon ignore)

- **Giấy phép:** CC BY 4.0, do Lab Coach tạo.
- Gọi đúng tên "teaching reference" trong mọi tài liệu và bài nộp — không gọi là "gold set" hay "ground truth".

## Pre-label YOLO26m

- **Giấy phép model:** AGPL-3.0 (Ultralytics). Output đóng băng thành `assets/model-yolo26m.xml`, không có trọng
  số `.pt`/`.onnx` nào trong repo. Repo Student không `import ultralytics`.

## Known issues (Lab Coach ghi trước khi phát lớp)

Danh sách box/polygon còn biết là chưa hoàn hảo trong teaching reference tại thời điểm phát lớp, ghi theo dạng
`frame, mô tả ngắn`. Không xoá mục cũ khi thêm mục mới — chỉ nối thêm dòng và ngày.

Chưa có danh sách vấn đề đã được xác nhận trong mục này. Điều đó **không** chứng minh teaching reference không có
lỗi; Lab Coach vẫn phải soát hàng đợi audit và ghi mọi ca còn mở trước khi dùng làm ví dụ trên lớp.

## Ảnh thực hành vạch ô đỗ

- `assets/parking/parking-lot-core.jpg`: ảnh xem trước 960×720 của [Parkinglot empty](https://commons.wikimedia.org/wiki/File:Parkinglot_empty.jpg), tác giả **Öljylautta**, tự công bố public domain. Bản trong repo được lấy từ thumbnail do Wikimedia Commons cung cấp; không sửa nội dung ảnh. Trang nguồn ghi ảnh gốc 4000×3000.
- `assets/parking/parking-lot-contrast.png`: ảnh xem trước 960×640 của [Apartment Complex Parking Lot 1](https://commons.wikimedia.org/wiki/File:Apartment_Complex_Parking_Lot_1.png), tác giả **TylerMascola**, **CC0 1.0**. Bản trong repo được lấy từ thumbnail do Wikimedia Commons cung cấp; không sửa nội dung ảnh. Trang nguồn ghi ảnh gốc 6000×4000.

Hai ảnh chỉ dùng cho bài nhận diện vạch trên ảnh bãi đỗ camera thường. Chúng không có nhãn chuẩn, thông số camera SVM, calibration hoặc thông tin độ sâu; kết quả vẽ là bằng chứng thực hành được người soát kiểm bằng mắt, không phải ground truth của một dataset tự lái.

## Sơ đồ bốn camera

`assets/diagrams/four-camera-seams.svg` là sơ đồ vector tự dựng cho bài học. Vùng màu và vị trí seam chỉ giải thích câu hỏi phối hợp camera; không biểu diễn góc nhìn, calibration, BEV hay dữ liệu đo từ một xe thật.
