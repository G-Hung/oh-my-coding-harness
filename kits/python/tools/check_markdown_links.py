"""Check repository-local Markdown links without requesting network resources."""

from __future__ import annotations

import re
import sys
from urllib.parse import unquote, urlsplit

from harness import ROOT as REPO_ROOT
from harness import contained, files
from markdown_it import MarkdownIt

LOCATION_SUFFIX = re.compile(r":\d+(?::\d+)?$")


def markdown_paths() -> list[str]:
    """Scan configured exclusions without requiring an initialized Git repository."""
    paths = [str(path.relative_to(REPO_ROOT)) for path in files() if path.suffix == ".md"]
    if not paths:
        raise ValueError("No Markdown files found")
    return paths


def local_targets(markdown: str) -> list[str]:
    """Extract rendered Markdown links and images, excluding code and remote URLs."""
    targets: list[str] = []
    for block in MarkdownIt("commonmark").parse(markdown):
        for token in block.children or []:
            if token.type == "link_open":
                target = token.attrGet("href")
            elif token.type == "image":
                target = token.attrGet("src")
            else:
                continue
            if target is None:
                continue
            if not isinstance(target, str):
                raise ValueError("Markdown link destination must be text")
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
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
