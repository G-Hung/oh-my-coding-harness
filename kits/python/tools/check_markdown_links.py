"""Check repository-local Markdown links without requesting network resources."""

from __future__ import annotations

import re
import sys
from urllib.parse import unquote, urlsplit

from harness import ROOT as REPO_ROOT
from harness import contained, files

LINK_PATTERN = re.compile(r"!?\[[^\]]*]\(([^)\n]+)\)")
LOCATION_SUFFIX = re.compile(r":\d+(?::\d+)?$")


def markdown_paths() -> list[str]:
    """Scan configured exclusions without requiring an initialized Git repository."""
    paths = [str(path.relative_to(REPO_ROOT)) for path in files() if path.suffix == ".md"]
    if not paths:
        raise ValueError("No Markdown files found")
    return paths


def local_targets(markdown: str) -> list[str]:
    """Extract local path targets while excluding anchors and external schemes."""
    targets: list[str] = []
    for raw in LINK_PATTERN.findall(markdown):
        without_title = re.sub(r"""\s+["'][^"']*["']$""", "", raw.strip())
        target = (
            without_title[1:-1]
            if without_title.startswith("<") and without_title.endswith(">")
            else without_title
        )
        parsed = urlsplit(target)
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        # Parse before decoding so encoded question/hash characters stay in filenames.
        targets.append(LOCATION_SUFFIX.sub("", unquote(parsed.path)))
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
            contained(resolved)
            if not resolved.exists():
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
