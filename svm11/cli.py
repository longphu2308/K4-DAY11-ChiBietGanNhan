"""Command-line entry point for the Day 11 lab."""
import argparse
import sys
from pathlib import Path

from . import LabError
from .common import ensure_late_templates, root
from .gates import check, doctor, triage
from .locking import lock_export, reveal_reference
from .local_quality import local_quality
from .parking import instructions as parking_instructions, save_export as save_parking_export
from .qc import fill, selfqc, stage_draft
from .quality import cvat_quality
from .report import compare, iou_sweep, model
from .synthesis import card, rework
from .workflow import cleanup, cvat, degrade, mode, qa, reset_task, status, worked


def parser():
    app = argparse.ArgumentParser(description="Day 11 · SVM/360 fisheye learner lab")
    sub = app.add_subparsers(dest="command", required=True)
    for name in ("doctor", "local-quality", "model", "triage", "rework", "card", "status", "check", "worked", "reset-task"):
        sub.add_parser(name)
    arg = sub.add_parser("mode"); arg.add_argument("--members", required=True); arg.add_argument("--self")
    arg = sub.add_parser("cvat"); arg.add_argument("slice"); arg.add_argument("--support", action="store_true")
    arg = sub.add_parser("draft"); arg.add_argument("file")
    arg = sub.add_parser("parking"); arg.add_argument("--file")
    arg = sub.add_parser("lock"); arg.add_argument("round", choices=("calib", "r1_craft", "rework"))
    arg.add_argument("file"); arg.add_argument("--relock", action="store_true")
    arg = sub.add_parser("reference"); arg.add_argument("round", choices=("calib", "r1_craft", "rework"))
    arg = sub.add_parser("compare"); arg.add_argument("round", choices=("calib", "r1_craft", "rework"))
    arg = sub.add_parser("cvat-quality"); arg.add_argument("--task-id", type=int)
    arg = sub.add_parser("iou-sweep"); arg.add_argument("--iou", required=True)
    arg = sub.add_parser("qa"); arg.add_argument("--slice", required=True)
    arg.add_argument("--file", required=True); arg.add_argument("--code", required=True)
    arg = sub.add_parser("fill"); arg.add_argument("round", choices=("calib", "r1_craft", "rework"), nargs="?", default="r1_craft")
    arg = sub.add_parser("selfqc"); arg.add_argument("round", choices=("calib", "r1_craft", "rework"))
    arg = sub.add_parser("degrade"); arg.add_argument("step")
    arg = sub.add_parser("cleanup"); arg.add_argument("--yes", action="store_true")
    return app


def run(argv=None, base=None):
    args = parser().parse_args(argv)
    base = root(base)
    announce_templates(base)
    try:
        return dispatch(args, base)
    finally:
        announce_templates(base)


def announce_templates(base):
    created = ensure_late_templates(base)
    if created:
        print("Đã tạo mẫu cho P4–P6: " + ", ".join("submission/" + name for name in created))


def dispatch(args, base):
    command = args.command
    if command == "doctor":
        messages = doctor(base)
        print("\n".join(messages))
        return 1 if any(line.startswith("✗") for line in messages) else 0
    if command == "mode":
        state = mode(base, args.members, args.self)
        print("Đã chia slice: " + ", ".join("%s → %s" % pair for pair in sorted(state["assignments"].items())))
        print("Slice của bạn (%s): %s" % (state["self"], state["slice"]))
    elif command == "cvat":
        print(cvat(base, args.slice, args.support))
    elif command == "draft":
        print("Đã lưu bản nháp để tự soát: " + str(stage_draft(base, args.file)))
    elif command == "parking":
        if args.file:
            path, counts = save_parking_export(base, args.file)
            print("Đã lưu %s (%d parking_line, %d free_space)" % (path, *counts))
        else:
            print(parking_instructions(base))
    elif command == "lock":
        print("Mã khóa: " + lock_export(base, args.round, Path(args.file), args.relock))
    elif command == "reference":
        print("Đã mở reference: " + str(reveal_reference(base, args.round)))
    elif command == "compare":
        compare(base, args.round); print("Đã ghi compare và findings")
    elif command == "cvat-quality":
        print(cvat_quality(base, args.task_id))
    elif command == "local-quality":
        print("Đã ghi báo cáo offline: " + str(local_quality(base)))
    elif command == "model":
        model(base); print("Đã ghi model_compare và findings")
    elif command == "iou-sweep":
        try:
            values = [float(v) for v in args.iou.split(",")]
        except ValueError as exc:
            raise LabError("IOU phải là danh sách số, ví dụ 0.3,0.5,0.7") from exc
        print(iou_sweep(base, values))
    elif command == "qa":
        print("Overlay: " + str(qa(base, args.slice, args.file, args.code)))
    elif command == "fill":
        print("Đã ghi: " + str(fill(base, args.round)))
    elif command == "selfqc":
        print("Đã ghi: " + str(selfqc(base, args.round)))
    elif command == "triage":
        errors = triage(base)
        print("\n".join(errors) if errors else "Findings hợp lệ")
        return 1 if errors else 0
    elif command == "rework":
        print("Đã ghi: " + str(rework(base)))
    elif command == "card":
        print("Đã ghi: " + str(card(base)))
    elif command == "degrade":
        print(degrade(base, args.step))
    elif command == "status":
        print(status(base))
    elif command == "check":
        errors = check(base)
        print("\n".join("✗ " + error for error in errors) if errors else "✓ Hồ sơ hình thức đầy đủ")
        return 1 if errors else 0
    elif command == "worked":
        print(worked(base))
    elif command == "cleanup":
        print(cleanup(base, args.yes))
    elif command == "reset-task":
        print(reset_task(base))
    return 0


def main():
    try:
        return run()
    except (LabError, OSError, ValueError) as exc:
        print("✗ " + str(exc), file=sys.stderr)
        return 1
