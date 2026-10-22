"""Select repository checks from committed, worktree, and untracked changes."""

from __future__ import annotations

import argparse
import fnmatch
import json
import subprocess
import sys
import tomllib
from pathlib import Path


def git(root: Path, *args: str) -> bytes:
    return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True).stdout


def name_status_paths(payload: bytes) -> set[str]:
    """Keep both sides of a rename or copy in NUL-delimited Git output."""
    parts = [part.decode("utf-8", "surrogateescape") for part in payload.split(b"\0") if part]
    paths: set[str] = set()
    index = 0
    while index < len(parts):
        status = parts[index]
        count = 2 if status.startswith(("R", "C")) else 1
        if not status or status[0] not in "ACDMRTUXB" or index + count >= len(parts):
            raise ValueError("unexpected Git name-status output")
        paths.update(parts[index + 1 : index + count + 1])
        index += count + 1
    return paths


def changed_paths(root: Path, base: str) -> list[str]:
    """Inspect commits since the merge base plus local changes."""
    merge_base = git(root, "merge-base", base, "HEAD").decode().strip()
    committed = git(root, "diff", "--name-status", "-z", "-M", f"{merge_base}..HEAD")
    staged = git(root, "diff", "--cached", "--name-status", "-z", "-M")
    unstaged = git(root, "diff", "--name-status", "-z", "-M")
    untracked = git(root, "ls-files", "--others", "--exclude-standard", "-z")
    paths = name_status_paths(committed) | name_status_paths(staged) | name_status_paths(unstaged)
    paths.update(part.decode("utf-8", "surrogateescape") for part in untracked.split(b"\0") if part)
    return sorted(paths)


def plan(paths: list[str], config: dict) -> list[dict]:
    rules = config.get("checks", [])
    if not rules:
        raise ValueError("configuration needs at least one [[checks]] rule")
    names: set[str] = set()
    selected: list[dict] = []
    for rule in rules:
        name, patterns, command = rule["name"], rule["paths"], rule["command"]
        if (
            not isinstance(name, str)
            or not isinstance(patterns, list)
            or not isinstance(command, list)
            or name in names
            or not patterns
            or not command
            or not all(isinstance(item, str) and item for item in [name, *patterns, *command])
        ):
            raise ValueError("checks need unique names, path patterns, and command arguments")
        names.add(name)
        matched = [
            path
            for path in paths
            if any(fnmatch.fnmatchcase(path, pattern) for pattern in patterns)
        ]
        selected.append(
            {"name": name, "paths": matched, "command": command, "selected": bool(matched)}
        )
    selection = config.get("selection", {})
    if not isinstance(selection, dict):
        raise ValueError("selection must be a table")
    ignored = selection.get("ignore", [])
    if not isinstance(ignored, list) or any(
        not isinstance(item, str) or not item for item in ignored
    ):
        raise ValueError("selection.ignore must be a list of nonempty patterns")
    uncovered = [
        path
        for path in paths
        if not any(rule["selected"] and path in rule["paths"] for rule in selected)
        and not any(fnmatch.fnmatchcase(path, pattern) for pattern in ignored)
    ]
    if uncovered:
        raise ValueError("changed paths have no check: " + ", ".join(uncovered))
    return selected


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--base", default="HEAD", help="Git ref used as the change baseline")
    parser.add_argument("--run", action="store_true", help="execute selected commands")
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        if not (root / ".git").exists():
            raise ValueError("root must be a Git repository")
        config_path = (root / args.config).resolve()
        if not config_path.is_relative_to(root):
            raise ValueError("configuration must be inside the repository")
        config = tomllib.loads(config_path.read_text(encoding="utf-8"))
        paths = changed_paths(root, args.base)
        checks = plan(paths, config)
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as exc:
        print(f"Check selection failed: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"changed_paths": paths, "checks": checks}, indent=2))
    if args.run:
        for check in checks:
            if check["selected"]:
                try:
                    result = subprocess.run(check["command"], cwd=root, check=False)
                except OSError as exc:
                    print(f"Check {check['name']} could not start: {exc}", file=sys.stderr)
                    return 2
                if result.returncode:
                    return result.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
