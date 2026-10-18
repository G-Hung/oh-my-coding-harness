"""Require a Conventional Commit subject; leave the body unrestricted."""

from __future__ import annotations

import re
import sys
from pathlib import Path

TYPES = "feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert"
SUBJECT = re.compile(rf"(?:{TYPES})(?:\([a-zA-Z0-9][a-zA-Z0-9._/-]*\))?!?: [^\s].*")


def valid_subject(message: str) -> bool:
    lines = message.splitlines()
    return bool(lines and SUBJECT.fullmatch(lines[0]) and lines[0] == lines[0].rstrip())


def main(args: list[str] | None = None) -> int:
    args = sys.argv[1:] if args is None else args
    if len(args) != 1:
        print("Usage: python tools/check_commit_message.py MESSAGE_FILE", file=sys.stderr)
        return 2
    try:
        message = Path(args[0]).read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        print(f"Cannot read commit message: {exc}", file=sys.stderr)
        return 2
    if valid_subject(message):
        return 0
    print(
        "Commit blocked: use type(scope): description or type: description.\n"
        "Types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert.\n"
        "Examples: feat(hooks): validate staged changes; docs: explain adoption.\n"
        "An optional ! marks a breaking change. The description must be nonempty.\n"
        "Edit the subject and retry the commit; the message body is unrestricted.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
