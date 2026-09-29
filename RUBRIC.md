# Rubric Day 11 — 100 điểm

Rubric này chấm **bằng chứng trong repo bài làm và lập luận gắn với ảnh**, không chấm tốc độ bấm CVAT hay số lượng box vẽ thêm. Toàn bộ phần vạch ô đỗ, fisheye và kế hoạch SVM bốn camera giả lập đều thuộc buổi lab Day 11 kéo dài 240 phút. [README](README.md) cho biết việc cần làm; [GUIDE](GUIDE.md) chỉ thao tác.

`python3 lab11.py check` kiểm file, định dạng và một số điều kiện tối thiểu. Nó **không** cho điểm, xác nhận vạch đỗ đúng, xác nhận teaching reference là gold set, hoặc thay người đọc bài. Mỗi tiêu chí dưới đây có điểm tối đa; điểm phần chỉ trao khi bằng chứng có thể truy về đúng ảnh, frame, quy tắc hoặc số liệu. Repo chưa đặt ngưỡng đạt/trượt.

## Bảng điểm

| Tiêu chí | Cách phân điểm và bằng chứng | Tối đa |
|---|---|---:|
| **1. Object trên ảnh fisheye** | Đúng phạm vi và sáu class, kể cả rider/xe ba bánh: **8**. Box bám phần nhìn thấy trên ảnh gốc, áp ngưỡng H=40, xử lý mép méo: **6**. `truncated` và `occluded` dùng đúng nghĩa: **4**. Xem `submission/r1_craft/annotations.xml`, `selfqc.md` và ảnh tương ứng. | **18** |
| **2. Vùng loại trừ** | `ego_body` có ở frame nhìn thấy thân xe và vắng ở frame không thấy: **3**. Soát hai `lens_border` mỗi frame theo vòng kính thật: **3**. `ignore_region.reason` hợp lệ, không box vật chủ yếu nằm trong vùng ignore: **2**. Xem XML và self-QC. | **8** |
| **3. Vạch ô đỗ và free-space** | Hai polyline theo phần sơn thật sự chia ô đỗ, không lấy vạch lối xe chạy làm `parking_line`: **4**. Polygon `free_space` bám vùng trống nhìn thấy, không xuyên xe/curb/vật cản: **3**. `submission/parking/observations.md` chỉ ra vạch đã chọn, một vạch/biên đã loại và lý do: **3**. | **10** |
| **4. Tự soát, QA và sửa nhãn** | `r1_craft/selfqc.md` có chín mục soát trên ảnh, nêu cảnh báo đã xử lý; `reference.txt` ghi bản cuối đã khóa trước khi mở reference: **4**. `r2_qa/qa_review.md` nêu ca cụ thể theo luật, không suy nguyên nhân khi chưa đủ bằng chứng: **4**. `rework/delta.md` ghi thay đổi trước/sau, chỉ sửa ca có căn cứ: **4**. | **12** |
| **5. Đọc báo cáo chất lượng** | `r3_diag/local_quality.md` và confusion CSV: phân biệt TP/FP/FN và truy được ít nhất một xung đột về ảnh: **4**. Đọc micro, một class yếu và IoU của cặp ghép đúng: **3**. Nêu giới hạn của vài frame, ngưỡng IoU và teaching reference; không biến số đo thành điểm đạt: **3**. | **10** |
| **6. Chẩn đoán lỗi** | `findings.csv` và mục phân tích của `10_error_card.md` phân biệt *WHAT* theo ảnh/frame, đủ ca mỗi vai: **4**. Giả thuyết *WHY* có chứng cứ; dùng `E5_unresolved` khi chưa rõ và nêu phép kiểm tiếp: **3**. Severity, owner và action phù hợp với nguyên nhân, không mặc định lỗi thuộc người gán nhãn: **3**. | **10** |
| **7. Sampling bốn camera** | `45_sampling_plan.csv` có front/rear/left/right × normal/hard, số nguyên dương và tổng 200: **4**. Cột `risk`/`rationale` của `45_sampling_plan.csv` và `45_review_plan.md` giải thích phân bổ theo rủi ro mỗi camera, không lấy một camera ADASIND thay bốn camera: **3**. Nêu ca hard, cách soát độ phủ và giới hạn tập giả lập: **3**. | **10** |
| **8. Kế hoạch gold set** | `46_gold_set_plan.md` có ca normal/hard cần review riêng cho từng camera: **3**. Cách chọn mẫu, người rà độc lập và giải quyết bất đồng trước khi gọi là gold: **3**. Nêu calibration/timestamp và một ca seam cần policy cross-camera: **2**. Có điều kiện refresh khi camera/guideline đổi và giới hạn của reference hiện tại: **2**. | **10** |
| **9. Tracking và liên camera** | `50_exit_ticket.md` giải thích identity, keyframe/Outside trong một camera: **2**. Phân biệt hai box hợp lệ ở seam với lỗi trùng; chỉ đề xuất nối track khi có timestamp, calibration và policy output: **3**. | **5** |
| **10. Bàn giao quyết định** | `20_guideline_patch.md` sửa một khoảng trống rule có ví dụ: **2**. `30_escalation_ticket.md` nêu ảnh/frame, tác động và người nhận: **2**. `40_decision_log.csv` truy được quyết định với bằng chứng: **2**. `50_exit_ticket.md` hoàn tất, câu tự nhìn lại dẫn đúng một ca trong bài: **1**. | **7** |
| **Tổng** | | **100** |

## Cách đọc điểm cho công bằng

- **Có file chưa có nghĩa là có điểm tối đa.** Tool có thể thấy hai polyline nhưng không biết chúng có thực sự chia ô đỗ. Người chấm mở ảnh và XML để kiểm ranh giới nhãn.
- **Bất đồng với reference không tự động là lỗi học viên.** Ghi frame, đối tượng, rule và bằng chứng trong `findings.csv` hoặc escalation; người chấm xét lập luận và khả năng reference sai.
- **Mã khóa chỉ chứng minh tính toàn vẹn của file được khóa.** Repo không chứng minh được bằng đồng hồ rằng học viên đã tự soát trước khi nhìn reference; người chấm đọc nội dung self-QC và hỏi lại thứ tự khi cần.
- **Chỉ số thấp không tự động kéo điểm bài xuống cùng tỷ lệ.** `local-quality` đo độ khớp với teaching reference trên ít frame. Điểm ở mục 5–6 đến từ cách đọc, truy lỗi và quyết định có căn cứ.
- **Notebook Colab và bài stretch không cộng điểm chỉ vì đã mở hoặc làm thêm.** Tám ô sampling và kế hoạch gold trong `submission/` mới là bằng chứng của mục 7–8.
- **Không đặt ngưỡng qua môn ở đây.** Bảng điểm là phân bổ 100 điểm của bài Day 11; việc công bố kết quả và quy chế chung nằm ngoài repo.

## Tự kiểm trước khi nộp

1. Mọi nhận định quan trọng dẫn tới ảnh/frame, rule, số đo hoặc file có thể mở lại.
2. Vạch chia ô đỗ được nhận theo **vai trò chia ô**, không chỉ theo màu sơn. `free_space` là vùng nhìn thấy trên ảnh tĩnh, không phải tuyên bố an toàn tự hành.
3. `ego_body` chỉ có khi thân xe xuất hiện; `lens_border` được soát theo vòng kính. Hai frame ngoại lệ không bị ép vẽ ego.
4. Tập 200 frame là bài thiết kế bốn camera **giả lập**; ba frame ADASIND không đại diện bốn camera.
5. `python3 lab11.py check` qua, repo bài làm ở chế độ Public, và file nộp trên GitHub trùng file đã dùng để giải thích.
