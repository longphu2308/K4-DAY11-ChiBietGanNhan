# 01 — Thao tác CVAT cho Day 11

Tên nút và phím tắt theo CVAT v2.74.1 — bản bạn đã cài ở Day 2. Đây là lần thứ hai bạn dùng lại đúng stack đó,
**không cài CVAT mới**.

## Chạy lệnh trên mọi máy có Python

Không cần cài `make`. Làm theo [GUIDE.md](../GUIDE.md#bắt-đầu-nếu-bạn-chưa-từng-dùng-terminal) để mở Terminal đúng thư mục rồi dùng `python3 lab11.py` (Windows: thay `python3` bằng `py`).

| Việc cần làm | Lệnh |
|---|---|
| Kiểm môi trường | `python3 lab11.py doctor` |
| Tạo task cho slice `B1-edge` | `python3 lab11.py cvat B1-edge` |
| Lưu export nháp | `python3 lab11.py draft <zip>` |
| Khóa export cuối | `python3 lab11.py lock r1_craft <zip>` |
| Mở teaching reference sau lock | `python3 lab11.py reference r1_craft` |

## 1. Bật lại stack Day 2

1. Mở Docker Desktop, chờ Engine chạy xong.
2. Trong thư mục CVAT của bạn (ví dụ `cvat-day2`): `docker compose start` (báo không có container: `docker compose
   up -d`).
3. Quay lại thư mục repo lab, chạy `python3 lab11.py doctor` — dòng CVAT phải in `✓ CVAT 2.74.x tại http://localhost:8080`.
4. Đăng nhập bằng tài khoản CVAT đã tạo từ Day 2.

Xong buổi: `docker compose stop` trong thư mục CVAT. **Không bao giờ** `docker compose down -v` — cờ `-v` xoá cả
task và nhãn đã lưu.

## 2. Tạo task cho một slice

`python3 lab11.py cvat <id>` in sẵn mọi thứ cần dán/chọn bên dưới. Làm theo đúng thứ tự:

1. Trang **Tasks** → nút **+** → **Create a new task**.
2. **Name:** đúng như lệnh in ra, dạng `Day11 · ADASIND · <slice> · raw_fisheye`.
3. **Labels** → tab **Raw** → xoá nội dung có sẵn → dán **toàn bộ** nội dung `assets/labels.json` mà lệnh in đường
   dẫn → **Save**. Sang tab **Constructor** kiểm: 6 class (Bus, Bike, Car, Pedestrian, Truck, ThreeWheeler) + label
   `ignore_region` có attribute `reason`.
4. **Select files** → **My computer** → chọn đúng 3 ảnh lệnh in ra (`assets/images/adasind_*.jpg`).
5. **Submit & Open** → bấm vào **Job #…** để mở màn hình gắn nhãn.

## 3. Nạp sẵn (prefill) trước khi vẽ tay

Lệnh in tên file XML cần nạp (`assets/prefill/<slice>.xml`), gồm nửa box frame 1 (completion problem) và 2 polygon
`lens_border` mỗi frame (sinh sẵn từ vòng kính, bạn chỉ soát lại, không vẽ tay).

1. Trong trang task: **Actions** → **Upload annotations**.
2. Chọn định dạng **CVAT 1.1**, chọn đúng file `.xml` lệnh in ra → xác nhận ghi đè.
3. Mở job, kiểm object import có hiện đúng số box + polygon `lens_border` lệnh in ra.

Sửa một box import (kéo điểm, đổi label) sẽ tự đổi `source` từ `file` sang `manual` — `python3 lab11.py lock` đếm việc này để
tách "giữ nguyên / đã sửa / vẽ mới".

## 4. Vẽ box, polygon ignore, polygon K12

| Việc | Cách làm |
|---|---|
| Vẽ box | **Draw new rectangle** → chọn Label → **Shape** → click góc trên trái rồi góc dưới phải |
| Vẽ polygon (`ego_body`, `ignore_region`, K12) | **Draw new polygon** → chọn Label → click từng điểm, ≥3 điểm, xong bấm **N** hoặc **Done** |
| Vẽ tiếp object cùng loại | **N** |
| Gán attribute (`truncated`, `occluded`, `reason`) | Sidebar phải → tab **Objects** → mở object → chọn giá trị |
| Xoá / sửa | Chọn object → **Del**; kéo điểm hoặc cạnh để sửa hình |
| Hoàn tác | **Ctrl+Z** |
| Sang frame kế / trước | **F** / **D** |

**Nhóm box + polygon K12 (cùng một đối tượng):** chọn cả box và polygon (Ctrl+click lần lượt) rồi bấm **G** để gán
cùng `group_id`. `python3 lab11.py fill` cần group này để ghép polygon với đúng box khi tính fill ratio.

Lưu thường xuyên: **Ctrl+S**. Export chỉ lấy bản đã lưu.

## 5. Export và khoá

Riêng **P2**, export một bản nháp trước: `python3 lab11.py draft <đường dẫn ZIP nháp>` → `python3 lab11.py fill` →
`python3 lab11.py selfqc r1_craft` → sửa trong CVAT. Sau đó thực hiện các bước dưới đây với **bản cuối**; chỉ bản cuối
được khoá và dùng cho QA. Bài vạch ô đỗ dùng task riêng, xem `docs/11-parking-lines-vi.md`.

1. **Ctrl+S**.
2. Trong job: **Menu** (góc trên trái) → **Export job dataset**.
3. Định dạng: **CVAT for images 1.1**. **Save images: tắt.**
4. Tải file zip khi CVAT báo xong (thông báo hoặc trang **Requests**).
5. `python3 lab11.py lock <vòng> <đường dẫn zip>` → lệnh in **mã khoá** `XXXX-XXXX`. Nhóm: đọc to mã này cho người
   soát mình.

## 6. Khi lệnh báo lỗi

| Thông báo | Làm gì |
|---|---|
| `CVAT chưa chạy ở http://localhost:8080` | Mở Docker Desktop, `docker compose start` trong thư mục CVAT, chạy `python3 lab11.py doctor` lại |
| `python3: command not found` hoặc `py` không chạy | Làm theo [GUIDE](../GUIDE.md#bắt-đầu-nếu-bạn-chưa-từng-dùng-terminal) và báo Lab Coach để cài Python 3.9 trở lên. |
| `đã khoá với file khác` | Ghi lý do vào `40_decision_log.csv`, rồi chạy lại `python3 lab11.py lock <vòng> <zip-mới> --relock` |
| `file đã đổi sau khi khoá` | Chạy lại `python3 lab11.py lock <vòng> <zip-vừa-export>` với đúng file vừa export |
| `Chưa khoá … trước khi mở reference` | Chạy `python3 lab11.py lock <vòng> <zip>` trước, rồi `python3 lab11.py reference <vòng>` sau |
| Import lỗi / prefill không lên | Kiểm task, tên ba ảnh, labels Raw và đúng file `assets/prefill/<slice>.xml`; báo Lab Coach. Nếu cần vẽ trắng từ ảnh gốc, ghi sự cố vào decision log. Không mở worked overlay trước khi xong QA mù P3. |

Kẹt quá 3 phút: gọi Lab Coach.
