# Thành viên và phân vai — Day11 SVM 360 Fisheye

## 1. Thông tin nhóm

- Khóa/lớp: K4
- Tên nhóm: ChiBietGanNhan
- Repo Public: https://github.com/longphu2308/K4-DAY11-ChiBietGanNhan
- Máy giữ hồ sơ chính / người quản lý: Trần Long Phú
- Slice chung lấy từ mode.json: B2-dense
- Tên định danh vai A dùng cho --self: B2-dense
- Kênh trao đổi nội bộ: Discord
- Đại diện nộp (vai C): Trần Long Phú - 2A202602313
- Commit chốt bài: [SHA hoặc URL commit]

## 2. Ba vai chính

| Vai | Họ và tên | MSSV | Tên định danh trong mode | Trách nhiệm | Bằng chứng đóng góp |
|---|---|---|---|---|---|
| A · Gán nhãn | Trần Đức Thọ | 2A202602324 | B2-dense | Parking/C0/slice, self-QC, lock, rework | [Link file/commit và mô tả phần đã làm] |
| B · QA độc lập | Nguyễn Văn Trọng | 2A202602276 | B3-edge | Review trước reference, finding QA, kiểm lại ca sửa | [Link file/commit và mô tả phần đã làm] |
| C · Chẩn đoán & điều phối | Trần Long Phú | 2A202602313 | B2-mid | Báo cáo, phân xử, kế hoạch, tích hợp, check và nộp | [Link file/commit và mô tả phần đã làm] |

Bảng này xác định vai của nhóm. Vòng QA tự sinh trong team.json thuộc quy trình nhiều hồ sơ của CLI; nhóm dùng một slice chung và quy trình A → B → C đã nêu trong hướng dẫn.

## 3. Bàn giao theo pha

| Mốc | Người giao → nhận | File / commit / mã khóa | Người nhận đã kiểm gì? | Trạng thái / vướng mắc |
|---|---|---|---|---|
| P0 · Chốt môi trường và vai | C → A, B | [mode.json, slice, phân vai] | [Điền] | [Điền] |
| P2 · Khóa bản đầu | A → B, C | [XML, lock.txt, slice, code, commit] | [Điền] | [Điền] |
| P3 · Chốt QA mù | B → C, A | [review, findings, ảnh, commit] | [Điền] | [Điền] |
| P4 · Quyết định sửa | C → A, B | [finding, decision log, commit] | [Điền] | [Điền] |
| P5 · Kiểm bản sửa | A → B → C | [v2, lock2, review kiểm lại, delta] | [Điền] | [Điền] |
| P6 · Chốt nộp | A, B → C | [manifest, commit chốt] | [Điền] | [Điền] |

## 4. Bất đồng và phối hợp

- Một ca đã phân xử: [Frame/object/rule; ý kiến A/B; bằng chứng; quyết định và link]
- Ca còn mở: [Nội dung, người theo dõi, phép kiểm tiếp theo; nếu không còn thì ghi rõ]
- Đóng góp của A/B/C vào kế hoạch và exit ticket: [Điền phần việc thực tế]
- Thay đổi phân công nếu có: [Thời điểm, lý do, người nhận; nếu không đổi thì ghi rõ]

## 5. Xác nhận trước khi nộp

- [ ] A xác nhận nhãn và export đúng phiên bản: [Tên / bằng chứng]
- [ ] B xác nhận đã QA độc lập trước reference và kiểm lại ca sửa: [Tên / bằng chứng]
- [ ] C xác nhận báo cáo đúng bản khóa, các file đầy đủ và check exit 0: [Tên / bằng chứng]
- [ ] manifest.json tại commit chốt có failed_gates rỗng.
- [ ] Repo nhóm Public, ảnh và các bằng chứng mở được.
- [ ] C đã push và gửi link repo nhóm + commit qua kênh lớp công bố.

Chỉ đánh dấu việc đã kiểm thật. Nhóm nộp một hồ sơ chung; check không tự chấm đóng góp từng người. Giữ nguyên header/các cột enum của findings.csv; tên người được ghi trong tài liệu này hoặc phần note thích hợp.
