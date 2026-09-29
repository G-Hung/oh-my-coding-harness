"""Run offline checks through one stable, fail-fast entry point."""

from __future__ import annotations

import argparse
import subprocess
import sys

from harness import ROOT, config


def commands(*, static_only: bool = False, tests_only: bool = False) -> list[list[str]]:
    # TODO: adapt these commands to the existing project; preserve its test runner.
    result = []
    if not tests_only:
        result.extend(
            [
                ["uv", "lock", "--check", "--offline"],
                [sys.executable, "-m", "ruff", "format", "--check", "."],
                [sys.executable, "-m", "ruff", "check", "."],
                [sys.executable, "-m", "pyright"],
                [sys.executable, "tools/check_markdown_links.py"],
                [sys.executable, "tools/check_max_lines.py"],
            ]
        )
    if not static_only:
        result.append([sys.executable, "-m", "pytest"])
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--static-only", action="store_true")
    modes.add_argument("--tests-only", action="store_true")
    args = parser.parse_args()
    config()
    for command in commands(static_only=args.static_only, tests_only=args.tests_only):
        print(f"\n$ {' '.join(command)}", flush=True)
        result = subprocess.run(command, cwd=ROOT, check=False)
        if result.returncode:
            return result.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
