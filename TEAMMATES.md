# Thành viên và phân vai — Day11 SVM 360 Fisheye

## 1. Thông tin nhóm

- Khóa/lớp: K4
- Tên nhóm: ChiBietGanNhan
- Repo Public: https://github.com/longphu2308/K4-DAY11-TranLongPhu-2A202602313
- Máy giữ hồ sơ chính / người quản lý: Trần Long Phú
- Slice chung lấy từ mode.json: B2-dense
- Tên định danh vai A dùng cho --self: tho
- Kênh trao đổi nội bộ: Discord
- Đại diện nộp (vai C): Trần Long Phú - 2A202602313
- Commit chốt bài: bcaf04a

## 2. Ba vai chính

| Vai | Họ và tên | MSSV | Tên định danh trong mode | Trách nhiệm | Bằng chứng đóng góp |
|---|---|---|---|---|---|
| A · Gán nhãn | Trần Đức Thọ | 2A202602324 | tho | Parking/C0/slice, self-QC, lock, rework | Thực hiện gán nhãn parking, C0, slice B2-dense; hoàn thành selfqc và khóa r1_craft mã C553-0060, rework v2 |
| B · QA độc lập | Nguyễn Văn Trọng | 2A202602276 | trong | Review trước reference, finding QA, kiểm lại ca sửa | QA mù trên slice B2-dense, tạo qa_review.md và 3 finding r2_qa |
| C · Chẩn đoán & điều phối | Trần Long Phú | 2A202602313 | phu | Báo cáo, phân xử, kế hoạch, tích hợp, check và nộp | Chạy local-quality, model, iou-sweep, điền decision log, error card, guideline patch, escalation ticket, review plan, exit ticket và nộp bài |

Bảng này xác định vai của nhóm. Vòng QA tự sinh trong team.json thuộc quy trình nhiều hồ sơ của CLI; nhóm dùng một slice chung và quy trình A → B → C đã nêu trong hướng dẫn.

## 3. Bàn giao theo pha

| Mốc | Người giao → nhận | File / commit / mã khóa | Người nhận đã kiểm gì? | Trạng thái / vướng mắc |
|---|---|---|---|---|
| P0 · Chốt môi trường và vai | C → A, B | `mode.json`, `team.json`, `sensor_context.md`, `parking/` | Kiểm tra mode đúng slice B2-dense, parking annotations hợp lệ | Hoàn thành, không vướng mắc |
| P2 · Khóa bản đầu | A → B, C | `r1_craft/annotations.xml`, mã khóa `C553-0060` | B kiểm tra export CVAT 1.1, đủ 24 box và 9 polygon | Hoàn thành, bàn giao QA mù |
| P3 · Chốt QA mù | B → C, A | `qa_review.md`, 3 finding `r2_qa`, mã khóa `65FF-EB98` | C đối chiếu nhận xét B với ảnh gốc trước khi mở reference | Hoàn thành, không lộ reference |
| P4 · Quyết định sửa | C → A, B | `local_quality.md`, `zone_table.md`, `findings.csv` | A và B thảo luận nguyên nhân, thống nhất giữ box ThreeWheeler và escalate ca Truck | Hoàn thành, chốt decision log |
| P5 · Kiểm bản sửa | A → B → C | `annotations-v2.xml`, `lock2.txt`, `delta.md` | B và C kiểm số trước/sau trên delta.md | Hoàn thành, số đối chứng ổn định |
| P6 · Chốt nộp | A, B → C | `10_error_card.md`, ticket, `manifest.json` | C chạy `lab11.py check`, exit 0, failed_gates rỗng | Sẵn sàng nộp bài |

## 4. Bất đồng và phối hợp

- Một ca đã phân xử: Tại frame `adasind_117120.jpg`, hai xe ba bánh chồng hình `L1` và `L2`. A vẽ 2 box; B lưu ý kiểm tra occlusion; C phân tích reference chỉ có 1 box. Nhóm quyết định giữ cả hai box (`action=keep_with_reason`, Decision `D03`) vì cả 2 xe đều nhìn thấy cấu trúc đặc trưng và đạt chiều cao $H \ge 40$ px, tránh lỗi bỏ sót phương tiện.
- Ca còn mở: Ca xe tải `R8` (`Truck`) trong reference của `adasind_062370.jpg` mà cả L và M đều không thấy do thiếu tương phản/mờ nhòe. Đã lập escalation ticket `30_escalation_ticket.md` và giao Lead QA kiểm tra temporal video context.
- Đóng góp của A/B/C vào kế hoạch và exit ticket: A đóng góp ý kiến về kỹ thuật vẽ polygon trên ảnh méo fisheye và ego body; B đóng góp tiêu chí review chéo và đồng bộ temporal; C tổng hợp kế hoạch 200 frame sampling, gold set 4 camera và soạn thảo exit ticket.
- Thay đổi phân công nếu có: Giữ nguyên phân công ban đầu, không thay đổi.

## 5. Xác nhận trước khi nộp

- [x] A xác nhận nhãn và export đúng phiên bản: Trần Đức Thọ
- [x] B xác nhận đã QA độc lập trước reference và kiểm lại ca sửa: Nguyễn Văn Trọng
- [x] C xác nhận báo cáo đúng bản khóa, các file đầy đủ và check exit 0: Trần Long Phú
- [x] manifest.json tại commit chốt có failed_gates rỗng.
- [x] Repo nhóm Public, ảnh và các bằng chứng mở được.
- [x] C đã push và gửi link repo nhóm + commit qua kênh lớp công bố.

Chỉ đánh dấu việc đã kiểm thật. Nhóm nộp một hồ sơ chung; check không tự chấm đóng góp từng người. Giữ nguyên header/các cột enum của findings.csv; tên người được ghi trong tài liệu này hoặc phần note thích hợp.
