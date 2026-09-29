# Exit ticket

Đọc `docs/10-svm360-reading-vi.md` trước khi trả lời câu 1–2. Các câu về zone, `why`, rework, parking và sampling
đã nằm trong file tương ứng nên không hỏi lại ở đây.

1. **Một vật ở vùng seam giữa hai camera thật xuất hiện với hai box khác nhau: đó là lỗi `DUPLICATE` hay cần một quy tắc riêng? Vì sao?**
   - **Trả lời:** Đây **không phải là lỗi `DUPLICATE`** ở tầng gán nhãn 2D đơn camera, mà **bắt buộc cần một quy tắc riêng (cross-camera policy)**.
   - **Vì sao:** Trong hệ thống Surround View Monitoring (SVM) bốn camera, vùng giáp ranh (seam) được nhìn bởi hai thấu kính fisheye khác nhau (ví dụ: camera trước và camera trái). Do vị trí đặt camera và góc nhìn khác biệt, vật thể sẽ có hình dạng, độ méo thấu kính (barrel distortion) và tỷ lệ co giãn pixel hoàn toàn khác nhau (có thể là `edge` ở camera trước nhưng là `mid` ở camera trái). Trên không gian ảnh gốc 2D, mỗi camera phải gán nhãn đầy đủ cho đối tượng nằm trong FOV của mình để phục vụ huấn luyện mô hình perception độc lập; nếu tự ý xóa một box vì nghĩ là trùng lặp thì perception của camera đó sẽ bị lỗi bỏ sót (FN). Việc hợp nhất (deduplication/fusion) hai box thành một đối tượng duy nhất phải được thực hiện ở tầng xử lý đa cảm biến (sensor fusion trên không gian BEV/3D world coordinates) dựa trên thông số calibration và timestamp đồng bộ.

2. **Một vật đi qua nhiều frame trên cùng camera: khi nào giữ cùng track ID, khi nào thêm keyframe hoặc trạng thái Outside? Nêu bằng chứng sẽ cần trước khi nối track qua hai camera.**
   - **Giữ cùng track ID:** Khi vật thể liên tục xuất hiện và duy trì được danh tính (identity) qua chuỗi frame, kể cả khi có biến dạng nhỏ do chuyển động hoặc bị che khuất thoáng qua trong thời gian rất ngắn.
   - **Thêm keyframe:** Khi đối tượng có sự thay đổi đột ngột về hình học, hướng di chuyển (ví dụ xe rẽ góc 90 độ), thay đổi đáng kể về trạng thái che khuất (từ `occluded` sang nhìn rõ toàn bộ), hoặc đổi từ tư thế bình thường sang biến dạng mạnh ở rìa thấu kính.
   - **Trạng thái Outside:** Gán trạng thái `Outside` (kết thúc track) khi đối tượng hoàn toàn rời khỏi trường nhìn (FOV) của camera, bị che khuất hoàn toàn trong thời gian dài vượt ngưỡng quy định, hoặc lọt hoàn toàn vào vùng vành kính đen `lens_border`.
   - **Bằng chứng cần trước khi nối track qua 2 camera:**
     1. Đồng bộ thời gian phần cứng (hardware timestamp sync) giữa 2 luồng camera với độ trễ cho phép $< 10\text{ ms}$.
     2. Ma trận calibration ngoại tại chính xác (extrinsic relative pose) để chiếu bounding box từ 2 camera lên cùng mặt phẳng thế giới / BEV.
     3. Tính liên tục và hợp lý về động học (quỹ đạo vị trí, hướng vận tốc) và độ tương đồng đặc trưng nhận diện ngoại quan (Re-ID visual feature embedding) tại vùng giao thoa seam.

3. **Nhìn lại cả buổi: một chỗ bạn tin nhãn mình đúng nhưng reference hoặc người soát nghĩ khác (dẫn frame/`object_ref`), bạn đã xử lý thế nào, và nếu làm lại slice này bạn sẽ đổi gì trong cách làm?**
   - **Chỗ bất đồng thực tế:** Tại frame `adasind_117120.jpg` với hai xe ba bánh `ThreeWheeler` (`L1` và `L2`) ở khu vực trung tâm. Quan sát kỹ ảnh gốc thấy có 2 xe đỗ so le chồng lấn hình ảnh; nhóm học viên đã vẽ 2 box riêng biệt và đánh dấu thuộc tính `occluded = true` cho xe bị che khuất. Tuy nhiên Reference chỉ có 1 box (coi là 1 xe hoặc bỏ qua xe sau), dẫn đến việc công cụ đối chiếu báo `SPURIOUS` cho box của nhóm.
   - **Cách nhóm xử lý:** Nhóm không vội vàng xóa box để làm đẹp số liệu khớp với reference. Thay vào đó, nhóm bảo vệ quan điểm an toàn cho hệ thống lái xe tự hành (không được phép bỏ qua một phương tiện cơ giới thật trên đường), ghi nhận ca này vào `submission/findings.csv` với hành động `action = keep_with_reason` / `escalate`, và lập quyết định trong `40_decision_log.csv` (entry `D03`) kèm lập luận hình học cụ thể.
   - **Nếu làm lại slice này:** Nhóm sẽ bật thước đo pixel trên CVAT để kiểm tra nghiêm ngặt ngưỡng chiều cao $H \ge 40\text{ px}$ trước khi vẽ các đối tượng ở hậu cảnh xa; đồng thời chủ động gom các cụm người đi bộ ở xa không thể tách rời thành polygon `ignore_region` với lý do `crowd_or_group` ngay từ đầu (theo tinh thần của Rule `R12` đề xuất) để tránh sinh ra nhiều box thừa ngoài tầm kiểm soát.
