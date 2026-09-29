import csv
import tempfile
import unittest
from pathlib import Path

from svm11.findings import HEADER, append_rows, read_rows, validate_rows


class FindingsTest(unittest.TestCase):
    def test_header_dedupe_and_validation(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "findings.csv"
            row = {"round": "r1_craft", "slice": "B1-edge", "frame": "f.jpg",
                   "object_ref": "L1", "cell": "L_only", "what": "SPURIOUS"}
            append_rows(path, [row, row])
            self.assertEqual(len(read_rows(path)), 1)
            self.assertEqual(path.read_bytes().splitlines(keepends=True)[0], (",".join(HEADER) + "\r\n").encode())
            self.assertEqual(validate_rows(read_rows(path)), [])
            broken = dict(row, why="bad", cell="wrong")
            self.assertTrue(validate_rows([broken]))

    def test_round_required_fields_reject_whitespace(self):
        base = {"slice": "B1-edge", "frame": "f.jpg", "object_ref": "L1",
                "cell": "L_only", "what": "SPURIOUS"}
        qa = dict(base, round="r2_qa", rule_id=" ", why="")
        self.assertTrue(any("rule_id" in error for error in validate_rows([qa])))
        diag = dict(base, round="r3_diag", why=" ", severity=" ", owner=" ", action=" ")
        errors = validate_rows([diag])
        for field in ("why", "severity", "owner", "action"):
            self.assertTrue(any("thiếu" in error and field in error for error in errors), errors)
        self.assertEqual(len(errors), 1, errors)
