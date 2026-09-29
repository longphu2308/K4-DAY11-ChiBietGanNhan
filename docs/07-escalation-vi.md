# 07 — Khi nào và cách viết escalation ticket

Escalation dùng cho vấn đề **không thuộc lỗi của annotator** — ví dụ lỗi ở chính teaching reference (`E0`), lỗi dữ
liệu (`E3`), hoặc khoảng trống trong luật (`E2`) mà bạn không có thẩm quyền tự quyết.

`submission/30_escalation_ticket.md` cần **≥1** vấn đề, đủ **5 trường** (slide p.41):

1. **Frame** — file ảnh cụ thể (vd `adasind_019560.jpg`), không nói chung chung "vài frame".
2. **Ảnh chụp** — đường dẫn tới screenshot minh hoạ trong `submission/screenshots/`.
3. **Expected impact** — nếu không sửa, ảnh hưởng gì tới bài học hoặc tới số liệu (ví dụ: một `E0` làm sai lệch mọi
   thống kê zone `edge` của slice này).
4. **Owner** — ai chịu trách nhiệm sửa: `annotator`, `guideline`, `data_ops`, `ai_team`, hoặc `qa` (cùng enum cột
   `owner` của `findings.csv`).
5. **Recommendation** — đề xuất cụ thể (sửa reference frame X, thêm rule mới, đổi ngưỡng H, ...), không chỉ nêu
   vấn đề.

Mỗi ticket escalate cũng cần một dòng tương ứng trong `findings.csv` (`action=escalate`) và một dòng trong
`40_decision_log.csv` (`status=escalated`).
