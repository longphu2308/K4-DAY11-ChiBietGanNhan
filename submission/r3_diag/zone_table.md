# Zone table (slice của bạn)

Lệnh `python3 lab11.py model` tự ghi bảng số (cùng cách đếm với `r1_craft/compare.md` và `model_compare.md`); chạy lại lệnh sẽ cập nhật bảng và giữ nguyên phần nhận xét. Bạn chỉ viết mục Nhận xét.

| Zone | n_ref | L missing | L spurious | M missing (`LR_noM` + `R_only`) | M thừa (`LM_noR` + `M_only`) | Lỗi L chính (`what`) |
|---|---:|---:|---:|---:|---:|---|
| center | 13 | 2 | 3 | 6 | 7 | SPURIOUS (3) |
| mid | 5 | 0 | 3 | 2 | 3 | SPURIOUS (3) |
| edge | 2 | 0 | 0 | 1 | 2 | — |

## Nhận xét

- Zone center gãy nhiều nhất cho cả learner và model: L có 2 missing và 3 spurious, còn M có 6 missing và 7 thừa; mid đứng sau với L 0/3 và M 2/3. Edge chỉ có 2 box reference nên số liệu ít.
- Giả thuyết: center/mid có nhiều vật chồng và vật nhỏ gần ngưỡng H=40, nên model dễ bỏ sót hoặc sinh box thừa; méo fisheye và vùng biên có thể làm IoU thay đổi. Đây chỉ là slice 3 frame, không đủ đại diện cho mọi camera, điều kiện sáng, thời gian hay tracking; teaching reference cũng không phải gold set.
