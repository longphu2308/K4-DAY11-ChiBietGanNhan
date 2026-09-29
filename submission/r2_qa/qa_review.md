# QA review · B2-dense

Mã khóa: 65FF-EB98

| frame | object_ref | rule_id | nhận xét |
|---|---|---|---|
| adasind_062370.jpg | B3 | R02, R05 | Bike ở mép phải kéo tới biên ảnh; giữ box theo phần nhìn thấy, kiểm lại `truncated=true` và `edge_zone=true`, không nắn theo hình đã undistort. |
| adasind_069450.jpg | B5-B7 | R01, R03 | Ba Pedestrian ở phía phải đều cao khoảng 55 px; kiểm từng người có tách được trên ảnh gốc và không gộp thành một cụm ignore. |
| adasind_117120.jpg | B0-B1 | R02, R05 | Hai ThreeWheeler ở vùng phải chồng hình; kiểm biên từng box trên phần nhìn thấy và đặt `occluded` theo vật che thực tế, không chỉ theo việc box giao nhau. |

Các dòng trên là quan sát QA mù từ ảnh và luật; chưa chẩn đoán nguyên nhân. Ghi finding r2_qa với `cell=L_only`, `rule_id` có giá trị và để trống `why`.
