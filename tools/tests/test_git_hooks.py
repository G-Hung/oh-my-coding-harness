"""Exercise real Git hook dispatch in isolated repositories; never push this repo."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class GitHooks(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="harness-hook-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "repo"
        self.root.mkdir()
        (self.root / "tools").mkdir()
        for name in ("git_gate", "pre_commit", "pre_push", "install_hooks", "check_commit_message"):
            shutil.copy2(ROOT / "tools" / f"{name}.py", self.root / "tools")
        shutil.copytree(ROOT / ".githooks", self.root / ".githooks")
        for name in ("pyproject.toml", "uv.lock", ".gitignore"):
            shutil.copy2(ROOT / name, self.root / name)
        (self.root / ".venv").symlink_to(Path(sys.prefix), target_is_directory=True)
        # A small gate isolates Git dispatch/snapshot behavior from the full suite
        # that is running this test. Production never offers a gate override.
        (self.root / "tools/check.py").write_text(
            "import pathlib, sys\n"
            "value = pathlib.Path('payload.txt').read_text().strip()\n"
            "bad = value == 'bad-static' or (value == 'bad-tests' "
            "and '--static-only' not in sys.argv)\n"
            "print('fixture gate failed' if bad else 'fixture gate passed')\n"
            "raise SystemExit(1 if bad else 0)\n"
        )
        (self.root / "payload.txt").write_text("good\n")
        self.env = os.environ.copy()
        self.env.pop("VIRTUAL_ENV", None)
        self.git("init", "-q")
        self.git("config", "user.name", "Harness Test")
        self.git("config", "user.email", "test@example.invalid")
        self.git("config", "commit.gpgsign", "false")
        self.git("add", ".")
        installed = self.run_script("install_hooks")
        self.assertEqual(installed.returncode, 0, installed.stderr)
        result = self.git("commit", "-qm", "chore: fixture baseline", check=False)
        self.assertEqual(result.returncode, 0, result.stderr)

    def git(self, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *args],
            cwd=self.root,
            env=self.env,
            text=True,
            capture_output=True,
            check=check,
        )

    def run_script(self, name: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, f"tools/{name}.py"],
            cwd=self.root,
            env=self.env,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_staged_failure_cannot_be_hidden_by_unstaged_fix(self) -> None:
        before = self.git("rev-parse", "HEAD").stdout
        (self.root / "payload.txt").write_text("bad-static\n")
        self.git("add", "payload.txt")
        staged = self.git("write-tree").stdout
        (self.root / "payload.txt").write_text("good\n")
        result = self.git("commit", "-qm", "fix(scope): intended fix", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Commit blocked", result.stderr)
        self.assertEqual(self.git("rev-parse", "HEAD").stdout, before)
        self.assertEqual(self.git("write-tree").stdout, staged)
        self.assertEqual((self.root / "payload.txt").read_text(), "good\n")
        self.git("add", "payload.txt")
        good = self.git("commit", "--allow-empty", "-qm", "fix(scope): staged fix", check=False)
        self.assertEqual(good.returncode, 0, good.stderr)

    def test_message_hook_blocks_bad_subject_and_allows_scope(self) -> None:
        before = self.git("rev-parse", "HEAD").stdout
        bad = self.git("commit", "--allow-empty", "-qm", "updated stuff", check=False)
        self.assertNotEqual(bad.returncode, 0)
        self.assertIn("Commit blocked: use type", bad.stderr)
        self.assertEqual(self.git("rev-parse", "HEAD").stdout, before)
        for message in ("feat(xyz): add hooks", "docs: 更新說明", "fix(api)!: change contract"):
            good = self.git("commit", "--allow-empty", "-qm", message, check=False)
            self.assertEqual(good.returncode, 0, good.stderr)

    def test_pre_push_checks_pushed_commit_not_worktree(self) -> None:
        remote = Path(self.temp.name) / "remote.git"
        self.git("init", "--bare", "-q", str(remote))
        self.git("remote", "add", "fixture", str(remote))
        (self.root / "payload.txt").write_text("bad-tests\n")
        self.git("add", "payload.txt")
        self.git("commit", "-qm", "test: expose failing suite")  # Static gate passes.
        (self.root / "payload.txt").write_text("good\n")
        bad = self.git("push", "fixture", "HEAD:refs/heads/trial", check=False)
        self.assertNotEqual(bad.returncode, 0)
        self.assertIn("Push blocked", bad.stderr)
        self.assertEqual(self.git("ls-remote", "fixture").stdout, "")
        self.git("add", "payload.txt")
        self.git("commit", "-qm", "fix: repair suite")
        good = self.git("push", "fixture", "HEAD:refs/heads/trial", check=False)
        self.assertEqual(good.returncode, 0, good.stderr)
        self.assertIn("refs/heads/trial", self.git("ls-remote", "fixture").stdout)

    def test_installation_preserves_existing_hook_owner(self) -> None:
        self.git("config", "core.hooksPath", "custom-hooks")
        result = self.run_script("install_hooks")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.git("config", "core.hooksPath").stdout.strip(), "custom-hooks")
        self.git("config", "--unset", "core.hooksPath")
        existing = self.root / ".git/hooks/pre-commit"
        existing.write_text("#!/bin/sh\nexit 0\n")
        existing.chmod(0o755)
        result = self.run_script("install_hooks")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Existing active hooks", result.stderr)

    def test_missing_gate_blocks_commit(self) -> None:
        (self.root / "tools/check.py").unlink()
        self.git("add", "tools/check.py")
        result = self.git("commit", "-qm", "chore: remove gate", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Commit blocked", result.stderr)


if __name__ == "__main__":
    unittest.main()
