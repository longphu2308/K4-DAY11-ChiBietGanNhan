# `svm11/` — chương trình hỗ trợ lab

Thư mục này chứa mã Python đứng sau các lệnh `python3 lab11.py ...`. Nó giúp kiểm cấu trúc file, lưu export CVAT, tạo báo cáo và chỉ bước kế tiếp. **Bạn không cần đọc, sửa, đổi tên hoặc nộp riêng các file trong thư mục này.**

## Bạn dùng nó như thế nào?

Đứng ở thư mục gốc repo, nơi có `lab11.py`, rồi chạy lệnh theo [README chính](../README.md) hoặc [GUIDE](../GUIDE.md). Ví dụ:

```bash
python3 lab11.py status
python3 lab11.py check
```

Trên Windows, thay `python3` ở đầu dòng bằng `py`. Nếu lệnh báo lỗi, chụp **toàn bộ** dòng lỗi và báo Lab Coach; không sửa file trong `svm11/` để né lỗi.

## Mã này làm gì?

| Nhóm file | Vai trò |
|---|---|
| `cli.py` | Nhận lệnh từ `lab11.py` và gọi đúng bước của lab. |
| `workflow.py`, `gates.py`, `locking.py` | Chia slice, chỉ bước tiếp theo, kiểm hồ sơ và khóa export trước khi mở reference. |
| `cvat_xml.py`, `parking.py`, `qc.py` | Đọc export CVAT, kiểm task parking và hỗ trợ self-QC. |
| `local_quality.py`, `quality.py`, `report.py`, `match.py` | Tạo báo cáo so sánh offline và xung đột để bạn xem lại trên ảnh. |
| `findings.py`, `synthesis.py`, `zones.py` | Kiểm bảng findings, tổng hợp error card/rework và tính zone trên ảnh. |

Các báo cáo do chương trình tạo nằm trong `submission/`, không nằm ở đây. Số so sánh với teaching reference chỉ giúp tìm ca cần xem; chúng không tự chấm rubric và không chứng minh gold set.
