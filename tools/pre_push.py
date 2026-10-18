"""Run the full gate for each proposed pushed commit; never contact a remote."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from git_gate import check_tree, git


def pushed_commits(payload: str) -> list[str]:
    commits: list[str] = []
    for line in payload.splitlines():
        fields = line.split()
        if len(fields) != 4:
            raise ValueError("Malformed pre-push ref input")
        local_ref, local_sha, _remote_ref, remote_sha = fields
        if not all(
            re.fullmatch(r"[a-fA-F0-9]{40}|[a-fA-F0-9]{64}", sha) for sha in (local_sha, remote_sha)
        ):
            raise ValueError("Malformed pre-push object ID")
        if local_ref in ("delete", "(delete)") or set(local_sha) == {"0"}:
            continue
        if local_sha not in commits:
            commits.append(local_sha)
    return commits


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    try:
        payload = sys.stdin.read()
        commits = pushed_commits(payload) if payload.strip() else [git(root, "rev-parse", "HEAD")]
        for commit in commits:
            tree = git(root, "rev-parse", "--verify", "--end-of-options", f"{commit}^{{tree}}")
            if check_tree(root, tree, static_only=False):
                print(
                    f"Push blocked for {commit}. Fix and commit changes, then retry.",
                    file=sys.stderr,
                )
                return 1
        return 0
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"Pre-push blocked: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
