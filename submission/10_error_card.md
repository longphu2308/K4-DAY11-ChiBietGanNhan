# Error analysis card

## Zone × block

| zone | block | what | count |
|---|---|---|---:|
| center | B2 | MISSING | 8 |
| center | B2 | SPURIOUS | 13 |
| center | C0 | MISSING | 3 |
| edge | B2 | MISSING | 1 |
| edge | B2 | SPURIOUS | 2 |
| edge | C0 | MISSING | 1 |
| mid | B2 | MISSING | 2 |
| mid | B2 | SPURIOUS | 9 |
| mid | C0 | MISSING | 2 |
| unknown | B2 | BOX_GEOMETRY | 3 |

## Top defects
- SPURIOUS: 24 (ví dụ frame adasind_117120.jpg)
- MISSING: 17 (ví dụ frame adasind_019560.jpg)
- BOX_GEOMETRY: 3 (ví dụ frame adasind_062370.jpg)

## Phân tích của bạn

Hai bảng trên do `python3 lab11.py card` tính từ `findings.csv`; chạy lại lệnh sẽ cập nhật bảng và giữ nguyên mục này. Viết cho lỗi nổi bật nhất, dẫn frame/`object_ref`.

- **Nguyên nhân khả dĩ (`why`) và vì sao bạn nghĩ vậy:**
  Lỗi nổi bật nhất là **SPURIOUS** (24 trường hợp, tập trung chủ yếu ở zone `center` và `mid`, điển hình tại frame `adasind_117120.jpg` với các box L1, L2, L8, L10, L11, L12). Nguyên nhân chính là do:
  1. Mật độ phương tiện và người đi lại rất đông đúc ở khu vực trung tâm (dense center), xuất hiện nhiều đối tượng ở khoảng cách xa gần tiệm cận ngưỡng chiều cao $H = 40\text{ px}$.
  2. Hiện tượng chồng lấn che khuất (occlusion) nghiêm trọng giữa hai xe `ThreeWheeler` (L1, L2) và giữa các người đi bộ (L11, L12). Khi quan sát trên ảnh 2D tĩnh, annotator có xu hướng vẽ bám theo từng cụm chi tiết nhìn thấy dẫn đến sinh nhiều box thừa so với ground truth của reference.
  3. Lỗi thuộc nhóm kết hợp giữa `E1_annotator_error` (chưa kiểm tra nghiêm ngặt thước đo chiều cao $H \ge 40\text{ px}$ trên ảnh gốc trước khi vẽ) và `E2_guideline_gap` (hướng dẫn hiện tại chưa có quy định định lượng cụ thể khi nào tách rời từng người đi bộ và khi nào gom thành polygon `ignore_region` với lý do `crowd_or_group`).

- **Cách sửa và ai nhận việc (`owner`):**
  - **`owner = guideline`:** Cập nhật tài liệu quy chuẩn gắn nhãn (`20_guideline_patch.md`), định nghĩa rõ ràng: nếu cụm người đi bộ ở xa đứng sát nhau với khoảng cách pixel $< 3\text{ px}$ hoặc bị che khuất $> 60\%$, bắt buộc khoanh vùng polygon `ignore_region` với `reason=crowd_or_group` thay vì vẽ box rời rạc từng người.
  - **`owner = annotator`:** Rà soát lại toàn bộ các đối tượng ở hậu cảnh xa trong frame `adasind_117120.jpg`, bật công cụ đo pixel của CVAT để loại bỏ các box có $H < 40\text{ px}$; điều chỉnh lại box cho các đối tượng chồng hình để đảm bảo box chỉ ôm trọn phần thân xe quan sát được.

- **Bằng chứng (ảnh trong `screenshots/`, dòng findings, rule):**
  - Ảnh minh chứng: `submission/screenshots/conflict_117120_threewheeler_overlap.png` (thể hiện rõ cụm xe ba bánh chồng hình và người đi bộ ở trung tâm).
  - Dòng findings liên quan: Các dòng 35–40 trong `submission/findings.csv` (round `r3_diag`, frame `adasind_117120.jpg`, đối tượng `L1`, `L2`, `L8`, `L10`, `L11`, `L12`).
  - Quy tắc vi phạm/liên quan: `R01` (ngưỡng chiều cao tối thiểu $H \ge 40\text{ px}$), `R03` (phân định Rider vs Pedestrian), `R05` (`truncated` vs `occluded`), và `R06` (áp dụng `ignore_region` cho nhóm đối tượng không thể phân tách).
