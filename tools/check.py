"""Run the library's offline maintenance gate without fixing or staging files."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
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
    for name, cwd, command in commands(static_only=args.static_only):
        print(f"\nCHECK {name} ({cwd.relative_to(ROOT)})\n$ {' '.join(command)}", flush=True)
        try:
            result = subprocess.run(command, cwd=cwd, check=False)
        except OSError as exc:
            print(f"BLOCKED {name}: {exc}", file=sys.stderr)
            return 2
        if result.returncode:
            print(
                f"FAIL {name}. Fix the cause, rerun this command, then retry the commit.",
                file=sys.stderr,
            )
            return 1
    print("All library maintenance checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
