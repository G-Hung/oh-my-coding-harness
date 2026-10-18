"""Explicitly enable this library's tracked hooks without replacing existing hooks."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOKS = ("pre-commit", "commit-msg", "pre-push")


def main() -> int:
    try:
        top = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], cwd=ROOT, text=True)
        if Path(top.strip()).resolve() != ROOT:
            raise ValueError("Run setup in this library's Git checkout")
        result = subprocess.run(
            ["git", "config", "--get", "core.hooksPath"], cwd=ROOT, text=True, capture_output=True
        )
        if result.returncode not in (0, 1):
            raise ValueError("Cannot inspect core.hooksPath")
        configured = result.stdout.strip()
        if configured and configured != ".githooks":
            raise ValueError(
                "Existing hooksPath: inspect and integrate it explicitly; not overwritten"
            )
        if not configured:
            directory = subprocess.check_output(
                ["git", "rev-parse", "--git-path", "hooks"], cwd=ROOT, text=True
            ).strip()
            active = [
                p.name
                for p in ((ROOT / directory).iterdir() if (ROOT / directory).exists() else [])
                if p.is_file() and not p.name.endswith(".sample") and os.access(p, os.X_OK)
            ]
            if active:
                raise ValueError("Existing active hooks: " + ", ".join(active))
        for name in HOOKS:
            if not os.access(ROOT / ".githooks" / name, os.X_OK):
                raise ValueError(f"Missing executable tracked hook: {name}")
        subprocess.run(
            ["git", "config", "--local", "core.hooksPath", ".githooks"], cwd=ROOT, check=True
        )
        print("Enabled .githooks: pre-commit, commit-msg, and pre-push for this checkout.")
        return 0
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"Hook setup blocked: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
