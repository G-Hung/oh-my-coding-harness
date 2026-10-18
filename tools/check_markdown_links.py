"""Check repository-local Markdown links without requesting network resources."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

REPO_ROOT = Path(__file__).resolve().parents[1]
LINK_PATTERN = re.compile(r"!?\[[^\]]*]\(([^)\n]+)\)")
LOCATION_SUFFIX = re.compile(r":\d+(?::\d+)?$")


def git_paths(*args: str) -> list[str]:
    """Return NUL-delimited paths from a read-only Git query."""
    output = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    return [value for value in output.split("\0") if value]


def markdown_paths() -> list[str]:
    """Return visible tracked and untracked Markdown paths."""
    candidates = set(
        git_paths("ls-files", "-z", "--", "*.md")
        + git_paths("ls-files", "--others", "--exclude-standard", "-z", "--", "*.md")
    )
    return sorted(
        path
        for path in candidates
        if (REPO_ROOT / path).is_file()
        and not (REPO_ROOT / path).is_symlink()
        and REPO_ROOT in (REPO_ROOT / path).resolve().parents
    )


def local_targets(markdown: str) -> list[str]:
    """Extract local path targets while excluding anchors and external schemes."""
    targets: list[str] = []
    # Code examples describe a copied layout; they are not library navigation.
    markdown = re.sub(r"(?ms)^\s*(`{3,}|~{3,})[^\n]*\n.*?^\s*\1\s*$", "", markdown)
    markdown = re.sub(r"`[^`\n]+`", "", markdown)
    for raw in LINK_PATTERN.findall(markdown):
        without_title = re.sub(r"""\s+["'][^"']*["']$""", "", raw.strip())
        target = (
            without_title[1:-1]
            if without_title.startswith("<") and without_title.endswith(">")
            else without_title
        )
        parsed = urlsplit(target)
        if parsed.scheme or parsed.netloc:
            continue
        target = unquote(parsed.path)
        if not target:
            continue
        targets.append(LOCATION_SUFFIX.sub("", target))
    return targets


def main() -> int:
    """Report broken local Markdown paths."""
    failures: list[str] = []
    paths = markdown_paths()
    for markdown_path in paths:
        source = (REPO_ROOT / markdown_path).read_text(encoding="utf-8")
        for target in local_targets(source):
            resolved = (
                REPO_ROOT / target.lstrip("/")
                if target.startswith("/")
                else (REPO_ROOT / markdown_path).parent / target
            )
            resolved = resolved.resolve()
            if (
                resolved != REPO_ROOT and REPO_ROOT not in resolved.parents
            ) or not resolved.exists():
                failures.append(f"{markdown_path}: {target}")
    if failures:
        print("Broken local Markdown links:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1
    print(f"Markdown links: {len(paths)} file(s) checked.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
