# Kế hoạch review từ lỗi quan sát được

Từ `findings.csv` và `zone_table.md`, chọn **hai lát cắt của bài ADASIND một camera** cần review trước. Bảng này
giải thích dữ liệu thật bạn vừa làm; nó không thay cho kế hoạch bốn camera giả lập ở `45_sampling_plan.csv`.

| Lát cắt / frame | Số ca và loại lỗi | Vì sao review trước | Bằng chứng cần giữ |
|---|---|---|---|
| `B2-dense / adasind_117120.jpg` (zone `center` & `mid`) | 6 ca `SPURIOUS` (xe ba bánh chồng lấn `L1`, `L2`; xe khách `L10`; người đi bộ ở xa `L11`, `L12`) | Mật độ giao thông cao nhất trong slice; chiếm toàn bộ số lỗi `SPURIOUS` của người học; cần giải quyết xung đột ranh giới che khuất và tiêu chí tách/gộp đám đông | Ảnh `submission/screenshots/conflict_117120_threewheeler_overlap.png`, tọa độ các box `L1`, `L2`, `L10`, `L11`, `L12`, ma trận nhầm lẫn `local_quality_confusion.csv` |
| `B2-dense / adasind_062370.jpg` (zone `center` & `edge`) | 2 ca `MISSING` (`R7` ThreeWheeler, `R8` Truck) và 1 ca `BOX_GEOMETRY` (`B3` Bike sát biên) | Chứa toàn bộ các ca bỏ sót (`MISSING`) dẫn đến Recall class `Truck` bị tụt về $0.000$; kiểm tra ranh giới cắt viền và độ méo thấu kính fisheye ở rìa ảnh | Ảnh `submission/screenshots/conflict_062370_r8_missing.png`, tọa độ tham chiếu `R7`, `R8`, thuộc tính `truncated=true` và `edge_zone=true` của box Bike |

- **Giới hạn của kết luận từ ba frame ADASIND:**
  Bộ dữ liệu thực hành chỉ gồm 3 frame tĩnh từ **một camera fisheye duy nhất**:
  1. *Thiếu tính khái quát về môi trường:* Không bao phủ được các điều kiện thời tiết khắc nghiệt (mưa, sương mù), ban đêm, hay các kiểu hạ tầng giao thông khác nhau.
  2. *Thiếu góc nhìn toàn cảnh:* Không có camera sau và hai bên sườn, hoàn toàn không có vùng chồng ảnh (seam) để kiểm chứng tính nhất quán khi ghép ảnh toàn cảnh SVM (Surround View Monitoring) hay tracking đa camera.
  3. *Kích thước mẫu quá nhỏ:* 3 frame không có ý nghĩa thống kê; các chỉ số như Precision $75\%$ hay Recall $90\%$ chỉ phản ánh hành vi trên vài đối tượng cụ thể, không đại diện cho hiệu năng của toàn bộ hệ thống perception.

## Chuyển sang kế hoạch bốn camera giả lập

- **Cách soát độ phủ của 200 frame ở `45_sampling_plan.csv`:**
  1. *Tránh lấy mẫu thiên lệch (burst sampling):* Không chọn các frame liên tiếp trong cùng một chuỗi video vài giây. Cần đặt khoảng cách thời gian tối thiểu giữa các frame được chọn (ví dụ: cách nhau $\ge 5$ giây hoặc tối thiểu 50 mét di chuyển) để đảm bảo mỗi frame mang một bối cảnh độc lập.
  2. *Độ phủ phân tầng đa chiều (multi-dimensional stratified coverage):* 200 frame phải được phân bổ đều cho 4 camera (`front`, `rear`, `left`, `right`) với cả hai nhóm `normal` và `hard`, trải rộng qua các kịch bản: bãi đỗ xe ngầm, đường hẹp đô thị, ngã tư có xe máy tạt đầu, và vùng chuyển tiếp ánh sáng (ra/vào hầm).

- **Vì sao kế hoạch đó chỉ giúp tìm ca cần soi, chưa đo được tỷ lệ lỗi:**
  Kế hoạch 200 frame là phương pháp **lấy mẫu có chủ đích dựa trên rủi ro (risk-based targeted sampling)** nhằm săn tìm các trường hợp biên nguy hiểm (edge cases, lỗi seam, méo thấu kính cực đại, chói lóa). Do các trường hợp khó (`hard`) được cố tình tăng tỷ trọng cao hơn nhiều so với tần suất xuất hiện tự nhiên trong 50.000 frame thông thường, tỷ lệ lỗi đo được trên tập 200 frame này sẽ cao hơn thực tế và không đại diện cho tỷ lệ lỗi tổng thể (true operational error rate) của sản phẩm. Tập dữ liệu này phục vụ kiểm tra sức chịu đựng (stress test) và vá lỗi thuật toán, không dùng để công bố KPI nghiệm thu.
