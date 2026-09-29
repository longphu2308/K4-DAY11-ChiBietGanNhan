# 09 — Hỗ trợ (support) và làm thêm (stretch)

## Cần hỗ trợ ở P2 (frame 2 cũng import sẵn)

Nếu cảm thấy quá tải với việc vẽ trắng cả frame 2 và 3: `python3 lab11.py cvat <slice> --support` import sẵn thêm nửa
box cho **frame 2** (giống frame 1), chỉ còn frame 3 vẽ trắng hoàn toàn. Đây không phải "làm ít hơn" — mọi mục
tiêu học tập (O1–O6) vẫn áp dụng, chỉ giảm khối lượng vẽ tay.

## Stretch — chỉ làm nếu còn thời gian ở P6

Thư mục `submission/stretch/` để **rỗng** nếu không làm phần này — không bị trừ gì. Nếu làm:

- Phân tích thêm một giả thuyết vì sao lỗi model khác nhau giữa `center` và `edge`, và đề xuất phép thử phân biệt
  méo fisheye với lỗi reference. Ghi vào `submission/stretch/model-domain-note.md` nếu làm.
- **Tự chạy YOLO26m** — tuỳ chọn, không bắt buộc. Nếu bạn có sẵn môi trường Ultralytics (ngoài repo lab, vì repo
  Student không import `ultralytics`), có thể tự chạy lại pre-label trên slice của mình để so với
  `model-yolo26m.xml` đã đóng băng. **Không commit** file trọng số `.pt`/`.onnx` nào vào repo — `python3 lab11.py check` sẽ
  báo lỗi nếu thấy.

**Sampling 200 frame và gold-set plan theo bốn camera là bài lõi**, điền `submission/45_sampling_plan.csv` và
`submission/46_gold_set_plan.md`. Không để hai file này trong stretch.

## Không có trong bài lab này

- **WoodScape** không nằm trong lane học viên (giấy phép Valeo không cho phát lại). Nếu Lab Coach chiếu minh hoạ
  free-space/parking-line/curb, đó chỉ là hình ảnh trình chiếu, không có trong repo và không có bài tập nào dùng
  tới. Báo cáo `python3 lab11.py local-quality` là phép tính offline trong repo; giao diện CVAT Quality Control trên bản
  Community của lớp yêu cầu gói trả phí, nên không phụ thuộc vào giao diện đó.
