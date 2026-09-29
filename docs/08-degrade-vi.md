# 08 — Time-box và thứ tự cắt giảm (degrade)

Lệch tiến độ 5 phút ở bất kỳ pha nào: xem thứ tự cắt giảm dưới đây và báo Lab Coach. Mỗi lần cắt, chạy
`python3 lab11.py degrade <tên-bước>` để ghi lại quyết định. Chỉ `findings` thay đổi cổng kiểm tự động;
các bước khác cần người soát xem lý do và chất lượng bằng chứng. `python3 lab11.py local-quality` chạy offline, không cần
dịch vụ CVAT Quality Control trả phí.

## Thứ tự cắt (từ trước tới sau)

1. **`stretch`** — bỏ toàn bộ phần stretch (`docs/09-support-stretch-vi.md`). `python3 lab11.py degrade stretch`.
2. **`k12`** — bỏ vẽ polygon K12 (đối chứng fill ratio). `python3 lab11.py degrade k12`.
3. **`frame3`** — bỏ frame thứ ba của slice, chỉ làm 2 frame. `python3 lab11.py degrade frame3`.
4. **`findings`** — hạ ngưỡng `findings.csv` từ 12 xuống 8 dòng (vẫn phải ≥4 giá trị `cell` khác `na`, ≥5 dòng có
   `M`, và ≥2 dòng mỗi vai `r1_craft`, `r2_qa`, `r3_diag`).
   `python3 lab11.py degrade findings`.
5. **`rework`** — rework chỉ còn 1 dòng mức P0. `python3 lab11.py degrade rework`.

## Không bao giờ bỏ

- `python3 lab11.py lock <round> <file-export>` mỗi vòng.
- `python3 lab11.py reference <round>` (mở sau khi đã khoá).
- `python3 lab11.py local-quality` sau khi mở teaching reference; không biến chỉ số thành điểm đạt.
- Ít nhất 1 dòng `findings.csv` mỗi vai (`r1_craft`, `r2_qa`, `r3_diag`).
- `delta.md` (phải có số trước/sau, dù rework chỉ 1 dòng).
- `python3 lab11.py check` chạy tới cùng, exit 0.
- Bài vạch ô đỗ, `45_sampling_plan.csv` và `46_gold_set_plan.md` của bốn camera.

`mode.json` ghi lại mọi bước đã `degrade`; đây là tín hiệu tiến độ, không phải bị trừ điểm.
