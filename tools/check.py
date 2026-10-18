"""Run the library's offline maintenance gate without fixing or staging files."""

from __future__ import annotations

import argparse
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def commands(*, static_only: bool = False) -> list[tuple[str, Path, list[str]]]:
    py = sys.executable
    root_checks = [
        ("root lockfile", ["uv", "lock", "--check", "--offline"]),
        ("Python format", [py, "-m", "ruff", "format", "--check", "tools", "examples"]),
        ("Python lint", [py, "-m", "ruff", "check", "tools", "examples"]),
        ("Python types", [py, "-m", "pyright", "--project", "pyproject.toml"]),
        ("library links and portability", [py, "tools/check_library.py"]),
        ("maintenance tests", [py, "-m", "unittest", "discover", "-s", "tools/tests"]),
        (
            "repository check tests",
            [py, "-m", "unittest", "discover", "-s", "examples/repository-checks/tests"],
        ),
        ("formal runner tests", [py, "-m", "unittest", "discover", "-s", "examples/formal/tests"]),
    ]
    if static_only:
        root_checks = root_checks[:5]
    result = [(name, ROOT, cmd) for name, cmd in root_checks]
    for path in sorted((ROOT / "examples").rglob("*.cjs")):
        result.append(
            (f"Node syntax: {path.relative_to(ROOT)}", ROOT, ["node", "--check", str(path)])
        )
    if static_only:
        result.append(
            (
                "Python kit static",
                ROOT / "kits/python",
                [
                    "uv",
                    "run",
                    "--frozen",
                    "--offline",
                    "--no-sync",
                    "python",
                    "tools/check.py",
                    "--static-only",
                ],
            )
        )
        for name in ("lint", "typecheck", "check:links", "check:loc"):
            result.append(
                (f"TypeScript kit {name}", ROOT / "kits/typescript", ["npm", "run", name])
            )
        return result
    node_tests = sorted((ROOT / "examples/git-checks/tests").glob("*.test.cjs"))
    node_tests += sorted((ROOT / "examples/ports/tests").glob("*.test.cjs"))
    result.extend(
        [
            ("standalone Node tests", ROOT, ["node", "--test", *map(str, node_tests)]),
            (
                "Python cache behavior",
                ROOT / "examples/formal/python",
                [py, "-m", "unittest", "-v", "test_cache"],
            ),
            (
                "TypeScript cache behavior",
                ROOT / "examples/formal/typescript",
                ["node", "--test", "cache.test.ts"],
            ),
            (
                "Python kit",
                ROOT / "kits/python",
                ["uv", "run", "--frozen", "--offline", "--no-sync", "python", "tools/check.py"],
            ),
            ("TypeScript kit", ROOT / "kits/typescript", ["npm", "run", "check"]),
        ]
    )
    return result


def run_checks(
    steps: list[tuple[str, Path, list[str]]],
    *,
    root: Path = ROOT,
    log_parent: Path | None = None,
) -> int:
    """Keep passing output compact; retain diagnostics outside disposable snapshots."""
    logs = Path(tempfile.mkdtemp(prefix="harness-check-", dir=log_parent))
    warning_count = 0
    env = os.environ.copy()
    env.pop("VIRTUAL_ENV", None)
    for index, (name, cwd, command) in enumerate(steps, 1):
        log = logs / f"{index:02d}.log"
        start = time.monotonic()
        print(f"CHECK {name} ... ", end="", flush=True)
        try:
            with log.open("w", encoding="utf-8") as output:
                output.write(f"cwd: {cwd}\n$ {shlex.join(command)}\n")
                output.flush()
                result = subprocess.run(
                    command,
                    env=env,
                    cwd=cwd,
                    check=False,
                    stdin=subprocess.DEVNULL,
                    stdout=output,
                    stderr=subprocess.STDOUT,
                )
        except OSError as exc:
            print("BLOCKED", flush=True)
            with log.open("a", encoding="utf-8") as output:
                output.write(f"\nCould not run check: {exc}\n")
            print(f"{exc}\nLogs retained: {logs}", file=sys.stderr)
            return 2
        elapsed = time.monotonic() - start
        warnings: list[str] = []
        tail: deque[str] = deque(maxlen=60)
        with log.open(encoding="utf-8", errors="replace") as output:
            next(output, None)  # Logged cwd, not tool output.
            next(output, None)  # Logged command, which may contain warning examples.
            for line in output:
                tail.append(line.rstrip())
                if re.search(
                    r"^\s*(?:WARN\b|REVIEW\b|npm\s+warn\b)|\bwarning:|\b[A-Za-z]+Warning:",
                    line,
                    re.IGNORECASE,
                ):
                    if line.strip() not in warnings:
                        warnings.append(line.strip())
        if result.returncode:
            print(f"FAIL ({elapsed:.1f}s)", flush=True)
            relative = cwd.relative_to(root)
            print(
                f"Rerun from project directory {relative}: {shlex.join(command)}\n"
                + "\n".join(tail)[-12000:]
                + f"\nLogs retained: {logs}",
                file=sys.stderr,
            )
            return 1
        print(f"PASS ({elapsed:.1f}s)", flush=True)
        warning_count += len(warnings)
        for warning in warnings[:3]:
            print(f"  WARN {warning[:240]}", flush=True)
        if len(warnings) > 3:
            print(f"  WARN {len(warnings) - 3} more; see {log}", flush=True)
    print(f"PASS: {len(steps)} checks; {warning_count} warning(s).", flush=True)
    if warning_count:
        print(f"Logs retained: {logs}", flush=True)
    else:
        shutil.rmtree(logs)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--static-only", action="store_true", help="fast pre-commit checks, without tests"
    )
    args = parser.parse_args()
    missing = [name for name in ("uv", "node", "npm") if shutil.which(name) is None]
    if missing:
        print("Missing tools: " + ", ".join(missing), file=sys.stderr)
        return 2
    return run_checks(commands(static_only=args.static_only))


if __name__ == "__main__":
    raise SystemExit(main())
