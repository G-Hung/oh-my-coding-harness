"""Report large source files; count physical lines, including comments and blanks."""

from __future__ import annotations

import argparse

from harness import ROOT, config, files


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true", help="Fail when a file exceeds the limit")
    args = parser.parse_args()
    limit = config()["max_lines"]
    paths = files(source_only=True)
    if not paths:
        raise ValueError("No source files found; review harness.toml roots and suffixes")
    oversized = []
    for path in paths:
        count = len(path.read_text(encoding="utf-8").splitlines())
        if count > limit:
            oversized.append((path.relative_to(ROOT), count))
    for path, count in oversized:
        print(
            f"REVIEW {path}: {count} lines (limit {limit}); "
            "assess responsibilities before splitting"
        )
    print(
        f"Max lines: {len(paths)} files, {len(oversized)} above {limit}; "
        f"{'strict' if args.strict else 'advisory'}"
    )
    return int(args.strict and bool(oversized))


if __name__ == "__main__":
    raise SystemExit(main())
