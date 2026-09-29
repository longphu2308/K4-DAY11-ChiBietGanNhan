# Quan sát vạch ô đỗ

- Hai vạch `parking_line` đã vẽ (mô tả vị trí trong ảnh): 
  - Vạch 1: Đoạn vạch sơn màu vàng/trắng phân chia hai ô đỗ xe ở khu vực tiền cảnh bên trái (tọa độ pixel x khoảng 47 đến 247, y khoảng 535 đến 570 px). Vạch tạo ranh giới rõ ràng giữa hai khoang đỗ xe kế cận sát lề trái.
  - Vạch 2: Đoạn vạch sơn phân chia ô đỗ ở khu vực tiền cảnh trung tâm (tọa độ pixel x khoảng 246 đến 420, y khoảng 531 đến 554 px), giới hạn khoang đỗ kế tiếp liền kề về phía bên phải. Cả hai vạch đều bám sát phần sơn nhìn thấy trên mặt đường và dừng tại vị trí sơn bị mờ đứt đoạn hoặc mép nhìn thấy.

- Một vạch/dấu sơn hoặc biên **không** vẽ, và vì sao:
  - Không vẽ vệt mép vỉa hè / lề đường (curb edge) và các vạch kẻ phân làn lưu thông / mũi tên chỉ hướng đi chung giữa hai hàng xe.
  - Lý do: Theo quy tắc trong `docs/11-parking-lines-vi.md`, nhãn `parking_line` chỉ dành riêng cho đoạn sơn nhìn thấy tạo ranh giới cho một ô đỗ riêng lẻ (parking stall boundary). Mép đường, curb, hoặc vạch chỉ hướng lưu thông nội bộ bãi xe không phân chia ô đỗ nên không được gán nhãn `parking_line`.

- Polygon `free_space` dừng ở đâu; có phần bị che nào không:
  - Polygon `free_space` bao phần mặt đường nhựa trống nhìn thấy được của lối xe chạy chính giữa hai hàng ô đỗ (dải tọa độ ngang x từ 0 đến 960 px, y từ khoảng 520 đến 684 px).
  - Điểm dừng: Polygon dừng sát mép vạch đầu các ô đỗ xe và mép lề đường (curb); dừng lại tại mép vùng bị che khuất và rìa khung hình. Không vẽ xuyên qua xe đỗ, cột, cây cối hay vỉa hè.
  - Ghi chú: Vùng mặt đường trống này chỉ phản ánh quan sát 2D tại thời điểm chụp tĩnh, không đại diện cho vùng lái xe an toàn (drivable area) trong thực tế do thiếu thông tin độ sâu, cảm biến đo khoảng cách và động học xe.

- Ca chưa chắc cần hỏi người soát (nếu không có, ghi “không có”):
  - Các vạch sơn mờ đứt đoạn ở hậu cảnh xa phía góc phải (nơi góc nhìn camera bị nghiêng hẹp theo phối cảnh sâu) khó phân định rõ ràng là ranh giới ô đỗ hay vạch phân làn nội bộ; cần thống nhất với reviewer ngưỡng độ mờ và chiều dài vạch tối thiểu trước khi quyết định vẽ hoặc bỏ qua.
