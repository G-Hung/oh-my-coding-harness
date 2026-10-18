"""Check staged content without changing the user's index or worktree."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from git_gate import check_tree, git


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    try:
        if Path(git(root, "rev-parse", "--show-toplevel")).resolve() != root:
            raise ValueError("Run the hook from this library's Git checkout")
        tree = git(root, "write-tree")
        if check_tree(root, tree, static_only=True):
            print("Commit blocked. Fix failures, stage the fixes, and retry.", file=sys.stderr)
            return 1
        if git(root, "write-tree") != tree:
            raise ValueError("Index changed during checks; inspect staged changes and retry")
        return 0
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"Pre-commit blocked: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
