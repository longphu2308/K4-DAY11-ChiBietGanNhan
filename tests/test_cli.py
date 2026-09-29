import subprocess
import sys
import unittest
from pathlib import Path


class CliTest(unittest.TestCase):
    def test_help_lists_all_commands(self):
        root = Path(__file__).resolve().parents[1]
        result = subprocess.run([sys.executable, str(root / "lab11.py"), "--help"],
                                cwd=str(root), capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        for name in ("doctor", "mode", "cvat", "lock", "reference", "compare",
                     "local-quality", "cvat-quality", "model", "iou-sweep", "qa", "fill", "selfqc",
                     "triage", "rework", "card", "degrade", "status", "check",
                     "worked", "cleanup", "reset-task"):
            self.assertIn(name, result.stdout)
