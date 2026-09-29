# `refs/` — teaching reference được mở có kiểm soát

Các file ZIP ở đây chứa teaching reference cho calibration C0 và từng slice fisheye. Chúng dùng để so sánh sau khi bạn đã tự làm và khóa export, **không phải đáp án để chép** và cũng không phải gold set đã được phê duyệt.

## Bạn cần làm gì?

- Không mở, giải nén, sửa, đổi tên hay upload các file ZIP này lên CVAT.
- Sau khi export của bạn đã khóa, dùng lệnh trong guide, ví dụ:

  ```bash
  python3 lab11.py reference r1_craft
  python3 lab11.py compare r1_craft
  ```

- Chương trình sẽ chọn đúng reference theo slice, chép tạm vào `data/_ref/` và ghi dấu đã mở trong `submission/<round>/reference.txt`.
- Đọc report/overlay để tìm ca cần đối chiếu với ảnh gốc và rules. Nếu nghi reference sai, ghi bằng chứng vào finding hoặc escalation; không sửa ZIP.

Trên Windows, thay `python3` ở đầu dòng bằng `py`. Chi tiết về thứ tự lock → reference → compare ở [GUIDE](../GUIDE.md).
