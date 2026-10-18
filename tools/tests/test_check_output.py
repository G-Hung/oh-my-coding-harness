"""Verify compact output retains diagnostics and failure semantics."""

from __future__ import annotations

import io
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from tools.check import run_checks


class CheckOutput(unittest.TestCase):
    def run_case(self, steps, root):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            result = run_checks(steps, root=root, log_parent=root)
        return result, out.getvalue(), err.getvalue()

    def test_success_suppresses_output_and_removes_logs(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            steps = [
                (
                    "unit tests",
                    root,
                    [sys.executable, "-c", "print('expected negative test error')"],
                )
            ]
            code, out, err = self.run_case(steps, root)
            self.assertEqual(code, 0)
            self.assertIn("CHECK unit tests ... PASS", out)
            self.assertNotIn("expected negative", out + err)
            self.assertEqual(list(root.iterdir()), [])

    def test_warnings_and_advisories_remain_visible_and_logged(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            script = (
                "print('warning: upgrade available'); print('REVIEW large.py: too long');"
                "print('  /tmp/file.py:1:1 - warning: deprecated');"
                "print('npm warn deprecated package')"
            )
            code, out, err = self.run_case([("types", root, [sys.executable, "-c", script])], root)
            self.assertEqual(code, 0)
            self.assertIn("4 warning(s)", out)
            self.assertIn("warning: deprecated", out)
            self.assertIn("1 more; see", out)
            self.assertIn("REVIEW large.py", out)
            self.assertIn("upgrade available", out)
            self.assertEqual(err, "")
            logs = list(root.glob("harness-check-*/*.log"))
            self.assertEqual(len(logs), 1)
            self.assertIn("warning: upgrade", logs[0].read_text())
            self.assertIn("npm warn deprecated", logs[0].read_text())

    def test_failure_stops_later_checks_and_retains_complete_log(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            script = "print('FIRST EVIDENCE'); print('x' * 20000); raise SystemExit(7)"
            marker = root / "should-not-run"
            steps = [
                ("tests", root, [sys.executable, "-c", script]),
                ("later", root, [sys.executable, "-c", f"open({str(marker)!r}, 'w').close()"]),
            ]
            code, out, err = self.run_case(steps, root)
            self.assertEqual(code, 1)
            self.assertIn("FAIL", out)
            self.assertIn("Rerun from project directory", err)
            self.assertLess(len(err), 14000)
            self.assertFalse(marker.exists())
            self.assertIn("FIRST EVIDENCE", next(root.glob("harness-check-*/*.log")).read_text())

    def test_missing_executable_is_blocked_with_persistent_log(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            code, out, err = self.run_case([("setup", root, ["not-installed-harness-tool"])], root)
            self.assertEqual(code, 2)
            self.assertIn("BLOCKED", out)
            self.assertIn("Logs retained:", err)
            self.assertIn(
                "Could not run check", next(root.glob("harness-check-*/*.log")).read_text()
            )


if __name__ == "__main__":
    unittest.main()
