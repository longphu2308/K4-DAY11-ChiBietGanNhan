# Glossary

| Thuật ngữ | Nghĩa |
|---|---|
| `ADASIND` | Dataset fisheye gốc (Zenodo, CC BY 4.0) dùng làm nguồn ảnh và box pre-label của lab này |
| `teaching reference` | Bản nhãn do Lab Coach sửa tay từ pre-label, dùng để dạy; **không phải** gold set đã kiểm bởi nhiều người |
| `pre-label` | Box do model (YOLOv5 gốc ADASIND, hoặc YOLO26m đóng băng) sinh sẵn, không phải nhãn đúng |
| `lens_border` | Polygon `ignore_region` phủ vành đen ngoài vòng kính fisheye, sinh sẵn từ `frames.csv`, học viên chỉ soát |
| `ego_body` | Polygon `ignore_region` phủ thân xe/gương/tay lái của xe gắn camera, học viên tự vẽ ở mọi frame thấy thân xe ego (46/48 frame) |
| `zone` (`center`/`mid`/`edge`) | Bin bán kính r/R quanh tâm vòng kính, dùng để chẩn đoán, không phải chuẩn ngành (`docs/05`) |
| `slice` | 3 frame của một `block` (`B1..B4`) và một `zone_focus`, ví dụ `B1-edge` |
| `C0` | Frame hiệu chuẩn dùng chung ở P1, không thuộc slice nào của P2 |
| `H` | Ngưỡng chiều cao box (40 px) để một vật nằm trong phạm vi gán nhãn |
| `fill ratio` | Diện tích polygon K12 / diện tích box cùng đối tượng — số đo riêng của lab, không phải thuật ngữ chuẩn |
| `don't-care` | Box nằm ≥50% trong một `ignore_region` — matcher bỏ qua, không tính TP cũng không tính FP (K13) |
| `cell` | Cột `findings.csv` ghi ba nguồn nào thấy cùng một vật: L (bạn), R (reference), M (model) |
| `WHY` (`E0`–`E4`) | Phán đoán nguyên nhân của một khác biệt: reference sai, annotator sai, lỗ hổng luật, lỗi dữ liệu, hay lệch miền model |
| `lock` | Khoá một vòng export (ghi hash, mã `XXXX-XXXX`); bắt buộc trước khi mở reference |
| `rules_version` | Số phiên bản của `docs/02-rules-vi.md`, tăng khi bạn đề xuất luật mới ở `20_guideline_patch.md` |
