# `submission/` — thư mục bài nộp của bạn

Đây là nơi lưu bằng chứng cho toàn bộ Day 11. Bạn điền các file mẫu có `TODO`, thêm ảnh chụp và để các lệnh `python3 lab11.py ...` tạo các file kỹ thuật cần thiết. **Giữ nguyên tên thư mục và tên file** để `python3 lab11.py check` nhận ra bài nộp.

## Cách dùng an toàn

1. Làm theo [README chính](../README.md) và [GUIDE](../GUIDE.md) theo thứ tự P0–P6.
2. Điền nội dung của bạn thay cho `TODO`; đừng xóa tiêu đề, cột CSV hoặc file mẫu.
3. Export từ CVAT rồi dùng lệnh hướng dẫn để lưu/khóa file. Không chép XML reference trong `refs/` vào đây.
4. Trước khi push repo cá nhân **Public**, chạy `python3 lab11.py check`, đọc từng lỗi và sửa bằng chứng thật.

## Bạn sẽ thấy gì trong đây?

| Vị trí | Bạn làm gì ở đó? |
|---|---|
| `00_setup/` | Lưu kết quả kiểm môi trường, slice được giao và sensor context. |
| `parking/` | Lưu export task vạch ô đỗ và quan sát của bạn. |
| `p1_calib/` | Lưu calibration C0 sau khi khóa, mở reference và so sánh. |
| `r1_craft/` | Lưu bản fisheye cuối, mã khóa và self-QC của chính bạn. |
| `r2_qa/` | Lưu review mù export đã khóa của bạn khác hoặc cold review. |
| `r3_diag/` | Lưu local quality, model comparison, conflict và zone table. |
| `rework/` | Lưu export sau sửa, mã khóa mới và delta trước/sau. |
| `screenshots/` | Thêm ít nhất hai ảnh minh chứng cho finding hoặc escalation. |
| File ở gốc thư mục | Lúc đầu: findings, decision log, sampling plan và gold-set plan. Sau `python3 lab11.py reference r1_craft` có thêm guideline patch, escalation ticket, review plan và exit ticket; `python3 lab11.py card` tạo error card. |

Một số file/chỗ trống chỉ xuất hiện sau khi bạn chạy lệnh tương ứng; bảng số trong `zone_table.md` và error card do lệnh tính, bạn chỉ viết phần nhận xét. Ví dụ, `r1_craft/annotations.xml` chỉ có sau khi bạn export CVAT và khóa `r1_craft`. Điều đó bình thường; đừng tạo file rỗng để cho đủ danh sách.

`python3 lab11.py check` chỉ kiểm cấu trúc và độ đầy đủ. Người chấm đọc nhãn, ảnh và lập luận theo [rubric 100 điểm](../RUBRIC.md).
