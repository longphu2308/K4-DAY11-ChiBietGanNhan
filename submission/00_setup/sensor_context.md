# Sensor context

- **Rig (quan sát từ ảnh, không có tài liệu rig/calibration chính thức):**
  ADASIND cung cấp ảnh từ **một camera fisheye duy nhất**. Dữ liệu không kèm thông số nội tại (focal length, distortion coefficients) hay ngoại tại (vị trí/góc gắn chính xác trên xe). Từ quan sát ảnh: camera được gắn trên một phương tiện hai bánh (xe máy/scooter), hướng nhìn chủ yếu về phía trước và hơi lệch sang trái so với hướng di chuyển. Bối cảnh giao thông Ấn Độ (đường phố, biển hiệu chữ Bengal, auto-rickshaw), xe đi bên trái đường. Không có ảnh từ camera thứ hai (rear/left/right), không có thông tin calibration liên camera hay đồng bộ thời gian giữa nhiều camera.

- **`ego_body` nhìn thấy trong frame:**
  Ở 46/48 frame, phần thân xe ego xuất hiện tại góc dưới-trái của vòng kính. Các chi tiết nhìn thấy bao gồm: tay lái (grip), bàn tay/cánh tay của người lái nắm tay lái, phần vỏ/chắn bùn phía trước xe, và bóng xe trên mặt đường. Diện tích ego body thay đổi tuỳ frame — có frame thấy nhiều (cánh tay + yếm xe), có frame chỉ thấy một mảng nhỏ vỏ xe hoặc bóng. Hai frame `adasind_006840` và `adasind_271039` không có thân xe ego nhìn thấy trong vòng kính, nên không vẽ polygon `ego_body` cho hai frame đó.

- **Vòng kính (lens circle):**
  Vòng kính fisheye tạo thành hình tròn rõ ràng trên ảnh 1080 × 1920 px (portrait). Tâm vòng kính nằm gần giữa chiều ngang ảnh, nhưng lệch lên phía trên so với giữa chiều dọc (tâm vòng kính ở khoảng nửa trên của ảnh). Đường kính vòng kính chiếm gần hết chiều ngang ảnh (≈ 1000–1050 px, tức khoảng 93–97% chiều rộng). Bên ngoài vòng kính là vành đen không chứa thông tin cảnh — vành đen này rộng hơn ở các góc trên và dưới do ảnh portrait dài hơn đường kính vòng tròn. Các vật ở gần rìa vòng kính bị méo barrel distortion mạnh (đường thẳng cong, tỷ lệ kéo giãn). Giá trị chính xác của đường kính và toạ độ tâm cần đo pixel trên ảnh hoặc lấy từ calibration file — dữ liệu ADASIND trong repo không cung cấp file này.

- **Giới hạn của dữ liệu một camera:**
  Chỉ có một camera nên không thể xác minh chéo (cross-camera) vật thể ở vùng chồng (seam), không có bird's-eye view thực, không có thông tin về phía sau/trái/phải xe. Vị trí gần–xa của vật trong cảnh không suy được từ zone bán kính trên ảnh (center/mid/edge chỉ là vị trí pixel, không phải khoảng cách thực). Không có ground truth free-space, depth hay tracking cross-camera trong dữ liệu này.
