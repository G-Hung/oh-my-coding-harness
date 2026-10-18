"""Run checks against an exact Git tree in a disposable checkout."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

DEPENDENCIES = (".venv", "kits/python/.venv", "kits/typescript/node_modules")


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def check_tree(root: Path, tree: str, *, static_only: bool) -> int:
    env = os.environ.copy()
    for key in git(root, "rev-parse", "--local-env-vars").splitlines():
        env.pop(key, None)
    env.pop("VIRTUAL_ENV", None)
    with tempfile.TemporaryDirectory(prefix="harness-git-gate-") as temporary:
        parent = Path(temporary)
        snapshot = parent / "checkout"
        snapshot.mkdir()
        index_env = os.environ.copy()
        index_env["GIT_INDEX_FILE"] = str(parent / "index")
        subprocess.run(["git", "read-tree", tree], cwd=root, env=index_env, check=True)
        subprocess.run(
            ["git", "checkout-index", "--all", f"--prefix={snapshot}{os.sep}"],
            cwd=root,
            env=index_env,
            check=True,
        )
        subprocess.run(["git", "init", "-q", str(snapshot)], env=env, check=True)
        subprocess.run(["git", "add", "--force", "--all"], cwd=snapshot, env=env, check=True)
        for relative in DEPENDENCIES:
            source, dest = root / relative, snapshot / relative
            if source.exists():
                if dest.exists() or dest.is_symlink():
                    raise ValueError(f"Dependency path must not be tracked: {relative}")
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.symlink_to(source.resolve(), target_is_directory=True)
        command = [sys.executable, "tools/check.py"]
        if static_only:
            command.append("--static-only")
        print(f"Checking Git tree {tree}; local edits cannot mask failures.", flush=True)
        return subprocess.run(command, cwd=snapshot, env=env, check=False).returncode
