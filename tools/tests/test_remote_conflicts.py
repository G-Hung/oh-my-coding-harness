"""Exercise fresh remote and PR comparisons using local objects and mocked gh."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import patch


def load() -> Any:
    spec = importlib.util.spec_from_file_location(
        "remote_conflicts", Path(__file__).resolve().parents[1] / "check_remote_conflicts.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


checker = load()


class RemoteConflicts(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="harness-peer-test-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name) / "source"
        self.root.mkdir()
        self.remote = Path(temporary.name) / "remote.git"
        self.git("init", "-q", "--initial-branch=main")
        self.git("config", "user.name", "Harness Test")
        self.git("config", "user.email", "test@example.invalid")
        self.git("config", "commit.gpgsign", "false")
        (self.root / "file.txt").write_text("one\ntwo\nthree\nfour\nfive\n")
        self.git("add", ".")
        self.git("commit", "-qm", "baseline")
        self.base = self.git("rev-parse", "HEAD")
        self.git("init", "--bare", "-q", str(self.remote))
        self.git("push", str(self.remote), "HEAD:refs/heads/main")
        self.git("--git-dir", str(self.remote), "symbolic-ref", "HEAD", "refs/heads/main")
        self.real_run = subprocess.run

    def git(self, *args: str) -> str:
        return subprocess.check_output(
            ["git", "-C", str(self.root), *args], text=True, stderr=subprocess.DEVNULL
        ).strip()

    def commit(self, branch: str, content: str) -> str:
        self.git("checkout", "-q", "-B", branch, self.base)
        (self.root / "file.txt").write_text(content)
        self.git("add", ".")
        self.git("commit", "-qm", branch)
        return self.git("rev-parse", "HEAD")

    def pull(
        self, number: int, sha: str, branch: str = "peer", source: str = "fork/project"
    ) -> dict:
        self.git("push", str(self.remote), f"{sha}:refs/pull/{number}/head")
        return {
            "number": number,
            "base": {"ref": "main"},
            "head": {"ref": branch, "sha": sha, "repo": {"full_name": source}},
            "draft": True,
            "user": {"type": "Bot"},
        }

    def gh(self, pages: list, *, status: int = 0):
        def run(command, *args, **kwargs):
            if command[0] == "gh":
                self.assertIn("--paginate", command)
                self.assertIn("--slurp", command)
                self.assertIn(
                    "repos/owner/project/pulls?state=open&base=main&per_page=100", command
                )
                self.assertEqual(kwargs["timeout"], 120)
                return subprocess.CompletedProcess(command, status, json.dumps(pages), "")
            return self.real_run(command, *args, **kwargs)

        return patch.object(checker.subprocess, "run", side_effect=run)

    def check(self, target: str, branch: str = "local", **kwargs) -> str:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            checker.check_remote_conflicts(
                self.root, str(self.remote), [(target, f"refs/heads/{branch}")], **kwargs
            )
        return output.getvalue()

    def test_url_identity_and_enterprise_override(self) -> None:
        for remote in (
            "https://github.com/owner/project.git",
            "ssh://git@github.com/owner/project.git",
            "git@github.com:owner/project.git",
        ):
            self.assertEqual(checker.github_repository(remote), ("github.com", "owner/project"))
        self.assertIsNone(checker.github_repository("https://gitlab.com/owner/project"))
        self.assertEqual(
            checker.explicit_repository("git.example/owner/project"),
            ("git.example", "owner/project"),
        )

    def test_explicit_repository_normalizes_before_query(self) -> None:
        for value in ("owner/project.git", "owner/project/", "/owner/project"):
            with self.subTest(value=value):
                self.assertEqual(
                    checker.explicit_repository(value), ("github.com", "owner/project")
                )
        self.assertEqual(
            checker.explicit_repository("/git.example/owner/project.git/"),
            ("git.example", "owner/project"),
        )
        for value in ("owner", "owner//project", "owner/.git"):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "--github-repo"):
                checker.explicit_repository(value)
        with self.gh([[]]):
            self.check(self.base, github_repo="/owner/project.git/")

    def test_paginated_draft_bot_fork_conflict_blocks_without_mutating_refs(self) -> None:
        target = self.commit("local", "local\ntwo\nthree\nfour\nfive\n")
        peer = self.commit("peer", "peer\ntwo\nthree\nfour\nfive\n")
        pull = self.pull(12, peer)
        before = self.git("show-ref")
        with self.gh([[], [pull]]), self.assertRaisesRegex(ValueError, r"PR #12.*"):
            self.check(target, github_repo="owner/project")
        self.assertEqual(self.git("show-ref"), before)

    def test_nonconflicting_same_file_is_informational(self) -> None:
        target = self.commit("local", "local\ntwo\nthree\nfour\nfive\n")
        peer = self.commit("peer", "one\ntwo\nthree\nfour\npeer\n")
        with self.gh([[self.pull(3, peer)]]):
            output = self.check(target, github_repo="owner/project")
        self.assertIn("INFO:", output)
        self.assertIn("file.txt", output)
        self.assertIn("Remote merge check passed", output)

    def test_self_exclusion_uses_destination_and_source_repo(self) -> None:
        target = self.commit("local", "local\ntwo\nthree\nfour\nfive\n")
        peer = self.commit("peer", "peer\ntwo\nthree\nfour\nfive\n")
        own = self.pull(4, peer, branch="destination", source="owner/project")
        with self.gh([[own]]):
            self.check(target, branch="destination", github_repo="owner/project")
        fork = self.pull(5, peer, branch="destination")
        with self.gh([[own, fork]]), self.assertRaisesRegex(ValueError, "PR #5"):
            self.check(target, branch="destination", github_repo="owner/project")

    def test_explicit_peer_conflict_without_gh(self) -> None:
        target = self.commit("local", "local\ntwo\nthree\nfour\nfive\n")
        peer = self.commit("peer", "peer\ntwo\nthree\nfour\nfive\n")
        self.git("push", str(self.remote), f"{peer}:refs/heads/peer")
        with patch.object(checker, "open_pull_requests", side_effect=AssertionError("no gh")):
            with self.assertRaisesRegex(ValueError, "branch refs/heads/peer"):
                self.check(target, peers=["peer"])

    def test_multi_ref_push_compares_proposed_pr_heads(self) -> None:
        first = self.commit("first", "first\ntwo\nthree\nfour\nfive\n")
        conflicting = self.commit("second", "second\ntwo\nthree\nfour\nfive\n")
        pulls = [
            self.pull(21, self.base, branch="first", source="owner/project"),
            self.pull(22, self.base, branch="second", source="owner/project"),
        ]
        with self.gh([pulls]), self.assertRaisesRegex(ValueError, "proposed PR #"):
            checker.check_remote_conflicts(
                self.root,
                str(self.remote),
                [(first, "refs/heads/first"), (conflicting, "refs/heads/second")],
                github_repo="owner/project",
            )
        compatible = self.commit("second", "one\ntwo\nthree\nfour\nsecond\n")
        with self.gh([pulls]), contextlib.redirect_stdout(io.StringIO()):
            checker.check_remote_conflicts(
                self.root,
                str(self.remote),
                [(first, "refs/heads/first"), (compatible, "refs/heads/second")],
                github_repo="owner/project",
            )

    def test_multi_ref_push_does_not_replace_fork_pr_head(self) -> None:
        first = self.commit("first", "first\ntwo\nthree\nfour\nfive\n")
        compatible = self.commit("second", "one\ntwo\nthree\nfour\nsecond\n")
        fork = self.commit("fork", "fork\ntwo\nthree\nfour\nfive\n")
        with self.gh([[self.pull(23, fork, branch="second")]]):
            with self.assertRaisesRegex(ValueError, "PR #23"):
                checker.check_remote_conflicts(
                    self.root,
                    str(self.remote),
                    [(first, "refs/heads/first"), (compatible, "refs/heads/second")],
                    github_repo="owner/project",
                )

    def test_incomplete_query_and_unfetchable_peer_block(self) -> None:
        with self.gh([], status=1), self.assertRaisesRegex(ValueError, "query failed"):
            self.check(self.base, github_repo="owner/project")
        with self.gh([[{"number": 1}]]), self.assertRaisesRegex(ValueError, "incomplete"):
            self.check(self.base, github_repo="owner/project")
        pull = {
            "number": 99,
            "base": {"ref": "main"},
            "head": {"ref": "gone", "sha": self.base, "repo": None},
        }
        with self.gh([[pull]]), self.assertRaisesRegex(ValueError, "Cannot fetch PR #99"):
            self.check(self.base, github_repo="owner/project")

    def test_pr_changed_after_query_blocks(self) -> None:
        target = self.commit("local", "local\ntwo\nthree\nfour\nfive\n")
        pull = self.pull(8, target)
        pull["head"]["sha"] = self.base
        with self.gh([[pull]]), self.assertRaisesRegex(ValueError, "changed during"):
            self.check(target, github_repo="owner/project")

    def test_public_push_url_discovers_prs_with_transport_rewrite(self) -> None:
        url = "https://github.com/owner/project.git"
        self.git("config", f"url.{self.remote}.insteadOf", url)
        with self.gh([[]]):
            checker.check_remote_conflicts(self.root, url, [(self.base, "refs/heads/local")])

    def test_query_and_fetch_timeouts_identify_stage(self) -> None:
        def run(command, *args, **kwargs):
            if command[0] == "gh":
                raise subprocess.TimeoutExpired(command, 120)
            return self.real_run(command, *args, **kwargs)

        with patch.object(checker.subprocess, "run", side_effect=run):
            with self.assertRaisesRegex(ValueError, "Open PR query timed out after 120 seconds"):
                self.check(self.base, github_repo="owner/project")

        def fetch_timeout(command, *args, **kwargs):
            if "fetch" in command:
                raise subprocess.TimeoutExpired(command, 120)
            return self.real_run(command, *args, **kwargs)

        with patch.object(checker.subprocess, "run", side_effect=fetch_timeout):
            with self.assertRaisesRegex(
                ValueError, "Fetch for refs/heads/main timed out after 120"
            ):
                self.check(self.base)


if __name__ == "__main__":
    unittest.main()
