# 10 — Đọc 10 phút: từ một camera tới hệ 360°/SVM

Bài gán nhãn object dùng **một** camera fisheye ADASIND. Bài vạch ô đỗ dùng ảnh bãi đỗ camera thường. Phần
`45_sampling_plan.csv` và `46_gold_set_plan.md` buộc bạn thiết kế cho hệ **Surround View Monitoring (SVM)** bốn
camera (trước, sau, trái, phải) trong một tình huống giả lập; không giả vờ rằng ADASIND có bốn camera. Đọc phần
này trước khi lập kế hoạch và trả lời `50_exit_ticket.md`.

## 4 camera và vùng chồng (seam)

Bốn camera fisheye gắn quanh xe có vùng nhìn chồng lên nhau ở góc xe (seam). Một vật ở vùng seam có thể xuất hiện
**đồng thời** trên hai camera, với hai hộp khác nhau, hai zone bán kính khác nhau (có thể là `edge` ở camera này,
`mid` ở camera kia). Hệ thống thật phải quyết định: giữ box nào, hợp nhất ra sao, hay giữ cả hai và để tầng sau xử
lý. Đây là bài toán không có trong lab một-camera của chúng ta.

## Bird's-eye view (BEV)

SVM thường hợp nhất 4 ảnh fisheye thành một ảnh nhìn từ trên xuống (bird's-eye view) để hiển thị cho tài xế hoặc
làm đầu vào cho một mô hình khác. Việc "tight" trên ảnh gốc (bài lab của bạn) và "tight" sau khi ảnh bị biến đổi
phối cảnh sang BEV là hai câu hỏi khác nhau — một box đúng trên ảnh gốc có thể méo lệch trên BEV, và ngược lại.

## Free-space và parking line

Ở `docs/11-parking-lines-vi.md`, bạn vẽ `parking_line` bằng polyline và vùng `free_space` nhìn thấy được bằng
polygon trên một ảnh bãi đỗ thật có quyền dùng rõ ràng. Phân biệt vạch chia ô với vạch làn/lối xe chạy trước khi
áp dụng rule lên ảnh fisheye. Ảnh bãi đỗ **không** cung cấp calibration, độ sâu hay ground truth an toàn; không
được suy rằng polygon vừa vẽ là vùng đi được của xe tự hành. Nếu Lab Coach chiếu WoodScape, ảnh đó chỉ là minh hoạ,
không nằm trong repo.

## Vì sao ADASIND không thực hành được cả bộ

ADASIND chỉ có **một** camera, không có track xuyên bốn camera hay nhãn free-space/parking-line. Trong bài object,
zone bán kính × block thời gian là cách chẩn đoán lỗi **trên camera này**. Trong bài SVM, bạn dùng `camera_id`
thực sự trong kịch bản giả lập và ghi riêng vùng khó của từng camera; không coi zone là camera thứ hai.

## Tracking và đối chiếu qua camera

Một track qua nhiều frame phải giữ identity khi cùng vật còn quan sát được; thay đổi hình học lớn cần keyframe,
vật ra khỏi trường nhìn cần trạng thái Outside theo guideline của task. Hai camera có thể thấy cùng một vật ở vùng
chồng, nhưng không tự ghép track hoặc xoá một box: cần timestamp, calibration và policy về output đích. Trong
`46_gold_set_plan.md`, nêu một ca cần người soát quyết định trước khi đánh giá cross-camera.

## Câu hỏi để tự kiểm sau khi đọc

Nếu một vật xuất hiện ở vùng seam của hai camera thật với hai box khác nhau, việc gán nhãn "một vật — hai box" đó
nên tính là lỗi `DUPLICATE` hay là một trường hợp hợp lệ cần một quy tắc riêng? Không có đáp án chuẩn ở đây — câu
hỏi này dùng cho câu cross-camera trong `50_exit_ticket.md`.
