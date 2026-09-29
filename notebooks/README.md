# Notebook hỗ trợ Day 11

[day11-svm360-colab.ipynb](day11-svm360-colab.ipynb) là công cụ **tùy chọn** để thử phương án lấy mẫu 200 frame và đề xuất gold set cho tình huống **giả lập** bốn camera. Dữ liệu 50.000 frame trong notebook do bài tập đặt ra; đó không phải thống kê của ADASIND hay bộ ảnh trong repo. Bài gán nhãn chính vẫn làm trong CVAT theo [README](../README.md) và [GUIDE](../GUIDE.md).

## Mở trong Google Colab

1. Tải file `.ipynb` ở trên về máy. Vào [Google Colab](https://colab.research.google.com/) → **File → Upload notebook** → chọn file đó.
2. Chạy các ô theo thứ tự. Ở ô `ALLOCATION`, thay `None` bằng số frame bạn đề xuất cho từng camera và hai lát cắt `normal`/`hard`. Ô kiểm tra dùng cùng cấu trúc tám dòng với `submission/45_sampling_plan.csv`; nó báo nếu tổng khác 200, vượt số frame giả lập hoặc thiếu một ô.
3. Chuyển số sang `submission/45_sampling_plan.csv`, tự điền rủi ro và lý do cho từng dòng. Viết kế hoạch review vào `45_review_plan.md`, kế hoạch gold set vào `46_gold_set_plan.md`. Không cần nộp notebook hoặc ảnh/ZIP trên Colab. Hoàn tất các bước CVAT, export và `python3 lab11.py check` theo hướng dẫn lab.

Ô cuối chỉ đọc **file CVAT XML hoặc ZIP của chính bạn** nếu bạn tự chọn file và điền đường dẫn. Nó mặc định bỏ qua, không tự tải repo, ảnh, file export hay gọi API. Nếu dùng Colab, chỉ upload dữ liệu được phép đưa lên dịch vụ ngoài; không đưa token, mật khẩu, `.env`, dữ liệu cá nhân hay dữ liệu bị hạn chế. Có thể chạy notebook trên Jupyter/Python cục bộ để giữ file ở máy. Số đếm từ XML chỉ giúp kiểm cấu trúc, không phải điểm chất lượng hoặc gold set.
