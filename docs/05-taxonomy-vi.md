# 05 — Đọc trục phân loại (taxonomy)

## Zone bán kính — bin chẩn đoán, không phải chuẩn ngành

`r/R` = khoảng cách từ tâm box tới tâm vòng kính, chia cho bán kính vòng kính của frame đó.

- `center`: r/R < 0.35
- `mid`: 0.35 ≤ r/R < 0.6
- `edge`: r/R ≥ 0.6

Hai ngưỡng 0.35 và 0.6 là **bin chẩn đoán** chọn từ phân bố pre-label của lab này, để so sánh trong buổi học. Đây
**không** phải ngưỡng chuẩn ngành cho hệ thống 360°/SVM thật.

## 6 class là tập con

ADASIND gốc và slide Ngày 11 nói tới nhiều class hơn (kể cả vật tĩnh như cone/pole/obstacle). Lab này chỉ dùng
**6 class động** (`docs/02-rules-vi.md`) — không có class tĩnh nào. Khi viết `20_guideline_patch.md` hay
`30_escalation_ticket.md`, nói rõ đây là tập con, không phải toàn bộ taxonomy gốc.

## Cột `cell` trong `findings.csv`

`cell` mô tả ba nguồn nào "thấy" cùng một vật: **L** = nhãn của bạn, **R** = teaching reference, **M** = model
(YOLO26m đóng băng).

| `cell` | Nghĩa |
|---|---|
| `LRM` | Cả ba đều thấy |
| `LR_noM` | Bạn + reference thấy, model bỏ sót |
| `LM_noR` | Bạn + model thấy, reference không có (nghi ngờ reference thiếu — E0) |
| `L_only` | Chỉ bạn thấy |
| `RM_noL` | Reference + model thấy, bạn bỏ sót |
| `R_only` | Chỉ reference có |
| `M_only` | Chỉ model có |
| `na` | Không áp dụng (dòng không so 3 nguồn, ví dụ `STRUCTURE`) |

## Cột `what` — công cụ gán tự động

`MISSING`, `SPURIOUS`, `WRONG_CLASS`, `BOX_GEOMETRY`, `DUPLICATE`, `ATTRIBUTE`, `IGNORE_SCOPE`, `STRUCTURE`. Chi
tiết luật ghép nằm trong `python3 lab11.py compare <round>`; bạn không tự gán cột này.

## Cột `why` — bạn tự phán đoán

- `E0_reference_defect` — **teaching reference sai**, không phải bạn sai. Đây là hạng mục **hợp pháp**: reference
  là bản nháp Lab Coach sửa tay, chưa phải "gold set" đã kiểm bởi nhiều người. Ghi rõ frame + lý do khi dùng `E0`.
- `E1_annotator_error` — bạn sai (hoặc người soát trước bạn sai).
- `E2_guideline_gap` — luật hiện tại (`docs/02`) không đủ để phân xử ca này.
- `E3_data_defect` — lỗi ở chính dữ liệu ảnh (mờ, cắt, blur đè lên vật).
- `E4_model_domain` — model sai vì lệch miền dữ liệu (model gốc huấn luyện trên ảnh phẳng, không biết `ego_body`,
  gãy ở vùng méo cạnh rìa). Đây là **giả thuyết** cần bằng chứng từ nhiều ca hoặc phép so sánh, không kết luận chỉ từ
  một box lệch.
- `E5_unresolved` — chưa đủ bằng chứng tách lỗi người gán nhãn, reference, dữ liệu và model. Ghi rõ còn cần ảnh,
  rule hoặc thử nghiệm gì; không ép mọi ca vào một nguyên nhân đoán mò.

## Vì sao `python3 lab11.py local-quality` và `python3 lab11.py compare` cho số khác nhau

Hai lệnh đều loại box ở `ignore_region` của teaching reference. `python3 lab11.py compare` ghép box **cùng class** trước để
phân loại `WHAT`; `python3 lab11.py local-quality` ghép **hình học trước** (IoU ≥ 0.5), rồi kiểm class để lập ma trận nhầm và
tính TP/FP/FN. Một cặp trùng vị trí nhưng sai class vì thế có thể hiện khác nhau ở hai báo cáo. Xem ảnh, overlay
và luật nhãn trước khi kết luận. Báo cáo local chỉ tính rectangle có chiều cao ≥40 px, không chấm polygon hay track.

`python3 lab11.py local-quality` đọc export đã khóa và teaching reference đã mở. Nó ghi `local_quality.md`, JSON, CSV xung đột
và ma trận. Một cặp đúng hình và class là TP; sai class là một FP của class vẽ và một FN của class tham chiếu. Box
chỉ có ở bên vẽ là FP, chỉ có ở tham chiếu là FN. Với tổng TP/FP/FN: `precision=TP/(TP+FP)`,
`recall=TP/(TP+FN)`, `Jaccard=TP/(TP+FP+FN)`, `Dice=2TP/(2TP+FP+FN)`. Accuracy micro là TP chia số lần đối
chiếu hình học (cặp đúng, cặp sai class, box đơn lẻ). Accuracy theo class thêm true negative từ các lần đối chiếu
không liên quan class đó. Macro là trung bình theo class có mẫu; worst là class thấp nhất. Khi không có mẫu, ghi
`N/A`, không biến thành 0 hay 100%; nếu một class có nhãn ở một phía nhưng mẫu số precision hoặc recall bằng 0,
chỉ số đó là 0 theo quy tắc CVAT. Mean IoU chỉ tính cặp TP. Đây là phép tính mô tả **theo quy tắc lab**, không
khẳng định trùng số với CVAT Premium vì cấu hình ghép, filter, attribute và cách lấy validation set có thể khác.
Các tên chỉ số và công thức mục tiêu tham khảo [tài liệu CVAT Quality Control](https://docs.cvat.ai/docs/qa-analytics/auto-qa/).

## Fill ratio (K12) — số đo riêng của lab

`python3 lab11.py fill` tính diện tích polygon / diện tích box cho 4 đối tượng bạn vẽ polygon viền thấy được. Không có thuật
ngữ chuẩn "fill ratio" trong tài liệu ngành; đây là số đo tự đặt để minh hoạ box trục thẳng lỏng bao nhiêu ở vùng
rìa cong so với vùng trung tâm.
