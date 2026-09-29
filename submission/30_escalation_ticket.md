# Escalation ticket

## Ticket 1

- **Frame:**
  `adasind_062370.jpg` (đối tượng tham chiếu: `R8` class `Truck` tại zone `center`)

- **Ảnh chụp:**
  `submission/screenshots/conflict_062370_r8_missing.png`

- **Expected impact:**
  Reference ghi nhận một box `Truck` (`R8`) ở cự ly xa phía trung tâm, tuy nhiên trên ảnh thực tế khu vực này có độ tương phản cực thấp, chi tiết bị mờ nhòe do nén JPEG và ánh sáng yếu. Cả người học (L) lẫn mô hình YOLO26m (M) đều không thể nhận diện được đối tượng này, dẫn đến Recall của class `Truck` bị tụt xuống $0.000$ trong báo cáo `local_quality.md`. Nếu giữ nguyên đánh giá này, nó sẽ tạo ra tín hiệu sai lệch nghiêm trọng về chất lượng mô hình cũng như năng lực của đội ngũ gán nhãn.

- **Owner:**
  `qa` (chủ trì, phối hợp với `guideline` và `ai_team`)

- **Recommendation:**
  1. Yêu cầu Lead QA và Data Ops truy xuất chuỗi frame video liên tục (temporal video context) trước và sau frame 062370 để xác minh xem đối tượng có chuyển động và có thực sự là phương tiện cơ giới `Truck` hay chỉ là mái che/vật kiến trúc tĩnh bên đường.
  2. Trong trường hợp không thể phân định dứt khoát trên ảnh tĩnh fisheye đơn lẻ, đề xuất phân loại ca này là `E0_reference_defect` kết hợp `E3_data_defect`, cập nhật lại Reference bằng cách chuyển vùng này thành `ignore_region` với `reason = unreadable` (theo quy tắc R06) thay vì coi là một box `Truck` chuẩn bắt buộc.
