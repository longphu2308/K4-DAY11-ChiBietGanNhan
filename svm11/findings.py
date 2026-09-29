"""Append-only learner findings CSV."""
import csv

HEADER = "round,slice,frame,object_ref,cell,what,why,severity,owner,rule_id,evidence,action,rules_version,note".split(",")
ENUMS = {
    "round": {"calib", "r1_craft", "r2_qa", "r3_diag", "rework"},
    "cell": {"LRM", "LR_noM", "LM_noR", "L_only", "RM_noL", "R_only", "M_only", "na"},
    "what": {"MISSING", "SPURIOUS", "WRONG_CLASS", "BOX_GEOMETRY", "DUPLICATE", "ATTRIBUTE", "IGNORE_SCOPE", "STRUCTURE"},
    "why": {"E0_reference_defect", "E1_annotator_error", "E2_guideline_gap", "E3_data_defect", "E4_model_domain", "E5_unresolved"},
    "severity": {"P0", "P1", "P2", "P3"},
    "owner": {"annotator", "guideline", "data_ops", "ai_team", "qa"},
    "action": {"rework", "keep_with_reason", "escalate"},
}


def read_rows(path):
    if not path.is_file():
        return []
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return [row for row in csv.DictReader(stream) if any((v or "").strip() for v in row.values())]


def append_rows(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = read_rows(path)
    keys = {(r.get("round"), r.get("frame"), r.get("object_ref"), r.get("what")) for r in existing}
    if not path.is_file():
        with path.open("w", encoding="utf-8", newline="") as stream:
            csv.writer(stream, lineterminator="\r\n").writerow(HEADER)
    with path.open("a", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, HEADER, extrasaction="ignore", lineterminator="\r\n")
        for row in rows:
            key = tuple(row.get(k) for k in ("round", "frame", "object_ref", "what"))
            if key not in keys:
                writer.writerow({name: row.get(name, "") for name in HEADER})
                keys.add(key)


def validate_rows(rows):
    errors = []
    for number, row in enumerate(rows, 2):
        values = {field: (row.get(field) or "").strip() for field in HEADER}
        for field, allowed in ENUMS.items():
            value = values[field]
            if value and value not in allowed:
                errors.append("Dòng %d: %s không hợp lệ: %s" % (number, field, value))
        for field in ("round", "slice", "frame", "object_ref", "cell", "what"):
            if not values[field]:
                errors.append("Dòng %d: thiếu %s" % (number, field))
        if values["round"] == "r2_qa":
            if not values["rule_id"]:
                errors.append("Dòng %d: r2_qa thiếu rule_id" % number)
            if values["why"]:
                errors.append("Dòng %d: r2_qa cần để trống why" % number)
        if values["round"] == "r3_diag":
            missing = [f for f in ("why", "severity", "owner", "action") if not values[f]]
            if missing:
                errors.append("Dòng %d: r3_diag thiếu %s" % (number, ", ".join(missing)))
    return errors
