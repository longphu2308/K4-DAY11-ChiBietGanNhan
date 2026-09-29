# 11 — Thực hành vạch ô đỗ trong bãi đỗ xe

## Bạn cần tạo gì?

Tạo một task CVAT trên **ảnh chụp bãi đỗ**, vẽ ít nhất hai `parking_line` bằng polyline và một vùng `free_space` nhìn thấy được bằng polygon. Nộp export CVAT và một ghi chú về vạch bạn **không** gán nhãn. Ảnh này là ảnh camera thường, không phải fisheye hay ảnh bốn camera SVM; bài dùng để học ranh giới nhãn trước khi áp dụng tư duy đó cho camera khác.

Ảnh lõi là `assets/parking/parking-lot-core.jpg`. Mở thêm `assets/parking/parking-lot-contrast.png` để so: vạch ô đỗ ở tiền cảnh và lối xe chạy trong bãi có vai trò khác nhau. Hai ảnh đã đi kèm repo, không cần tải thêm. Xem nguồn và giấy phép ở `docs/DATA_LICENSES.md`.

![Bãi đỗ lõi với các đoạn sơn chia ô ở tiền cảnh](../assets/parking/parking-lot-core.jpg)

*Ảnh core để gán nhãn: hãy kiểm từng đoạn sơn có thực sự tạo ranh giới ô đỗ không trước khi vẽ.*

![Bãi đỗ đối chiếu có vạch ô tiền cảnh và lối xe chạy ở giữa](../assets/parking/parking-lot-contrast.png)

*Ảnh đối chiếu để đọc vai trò của vạch; không nạp ảnh này vào task core.*

## Vạch nào là `parking_line`?

`parking_line` là **đoạn sơn nhìn thấy được tạo ranh giới một ô đỗ riêng lẻ**. Chỉ vẽ phần sơn quan sát được; polyline dừng tại chỗ bị che hoặc vạch kết thúc. Nếu một dải sơn dài chỉ dẫn lối xe chạy, là mép đường, mũi tên hoặc vạch qua đường, đừng gọi nó là `parking_line` chỉ vì nó nằm trong bãi. Khi không rõ vạch đang chia ô hay hướng xe chạy, ghi ca đó vào `parking/observations.md` thay vì đoán.

`free_space` trong bài này là **phần mặt đường trống nhìn thấy được của lối xe chạy trong bãi** tại thời điểm chụp. Polygon không đi xuyên xe đỗ, curb, cây, hay vùng bị che. Nó là nhận xét trên một ảnh tĩnh, không phải kết luận nơi xe tự hành có thể đi an toàn.

## Làm trong CVAT

1. Chạy `python3 lab11.py parking` để lấy đúng đường dẫn ảnh và `assets/parking/labels.json` (Windows: `py lab11.py parking`). Tạo task tên `Day11 · parking_line · public-sample`, nạp **chỉ** `parking-lot-core.jpg` và dán hai nhãn từ file JSON.
2. Vẽ ít nhất hai polyline `parking_line` ở hai vạch chia ô đỗ khác nhau. Vẽ một polygon `free_space` cho đoạn lối xe chạy thấy rõ. Soát lại hình học theo ảnh; không nối qua phần sơn khuất.
3. Export **CVAT for images 1.1** (không kèm ảnh). Chạy `python3 lab11.py parking --file <đường-dẫn-file-zip>`; chương trình lưu `submission/parking/annotations.xml` và kiểm loại hình cùng số lượng tối thiểu. Nó **không** phán xét vạch nào đúng; người soát sẽ xem trên ảnh.
4. Điền `submission/parking/observations.md`: nêu hai vạch đã chọn, một dấu sơn/biên đã loại, vị trí `free_space`, và lý do. Chụp màn hình nếu một ca khó cần giải thích.

**Xong khi:** export được nhận, ghi chú không còn `TODO`, và bạn có thể chỉ ra trên ảnh vì sao một vạch là ranh ô đỗ còn một vạch khác không phải. Nếu CVAT không nhận ảnh hoặc export, báo Lab Coach; đừng tạo XML rỗng để qua `python3 lab11.py check`.

Muốn theo trọn luồng Day 11 mà không mở nhiều file, quay về [README](../README.md) và [GUIDE](../GUIDE.md).
