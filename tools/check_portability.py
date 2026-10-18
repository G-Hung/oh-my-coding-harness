from __future__ import annotations

import re
import sys
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

TEXT_FILE_SUFFIXES = {
    ".md",
    ".txt",
    ".py",
    ".toml",
    ".yaml",
    ".yml",
    ".json",
    ".sh",
    ".js",
    ".cjs",
    ".mjs",
    ".ts",
    ".tsx",
    ".tla",
    ".cfg",
}

EXCLUDED_DIR_NAMES = {
    ".git",
    ".venv",
    "__pycache__",
    "node_modules",
}

ABSOLUTE_PATTERNS = (
    re.compile(r"/Users/[^\s)>\]}\"']+"),
    re.compile(r"/home/[^\s)>\]}\"']+"),
    re.compile(r"[A-Za-z]:\\[^\s)>\]}\"']+"),
    re.compile(r"file://[^\s)>\]}\"']+"),
)


def should_check(path: Path) -> bool:
    if not path.is_file():
        return False
    rel_path = path.relative_to(REPO_ROOT)
    if any(part in EXCLUDED_DIR_NAMES for part in rel_path.parts):
        return False
    return path.suffix in TEXT_FILE_SUFFIXES


def iter_repo_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=REPO_ROOT, check=True, capture_output=True, text=True,
    )
    paths = set()
    for name in result.stdout.split("\0"):
        if not name:
            continue
        candidate = REPO_ROOT / name
        if candidate.is_symlink() or not should_check(candidate):
            continue
        if not candidate.resolve().is_relative_to(REPO_ROOT.resolve()):
            raise ValueError(f"File escapes repository root: {name}")
        paths.add(candidate)
    return sorted(paths)


def find_violations(path: Path) -> list[tuple[int, str]]:
    violations: list[tuple[int, str]] = []
    rel_path = path.relative_to(REPO_ROOT)
    if rel_path == Path("tools/check_portability.py"):
        return []
    for lineno, line in enumerate(path.read_text().splitlines(), start=1):
        if "portability-check: ignore" in line:
            continue
        for pattern in ABSOLUTE_PATTERNS:
            match = pattern.search(line)
            if match:
                violations.append((lineno, match.group(0)))
                break
    return violations


def main() -> int:
    failures: list[str] = []
    for path in iter_repo_files():
        rel_path = path.relative_to(REPO_ROOT)
        for lineno, match in find_violations(path):
            failures.append(f"{rel_path}:{lineno}: machine-specific absolute path")

    if failures:
        print("Repo portability check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        print(
            "Use repo-relative paths instead, or add 'portability-check: ignore' for an intentional example.",
            file=sys.stderr,
        )
        return 1

    print("Repo portability check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
