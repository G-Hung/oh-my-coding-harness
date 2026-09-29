"""Provide an advisory README review prompt for changed behavior."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from harness import ROOT as REPO_ROOT
from harness import config, contained

SETTINGS = config()
SOURCE_SUFFIXES = set(SETTINGS["behavior_suffixes"])
IGNORED_PARTS = set(SETTINGS["exclude"])


def git_output(*args: str) -> str:
    """Run a read-only Git query and return stdout."""
    return subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def parse_name_status(output: str) -> list[str]:
    """Extract old and new paths from NUL-delimited name-status output."""
    parts = [part for part in output.split("\0") if part]
    paths: list[str] = []
    index = 0
    while index < len(parts):
        status = parts[index]
        path_count = 2 if status.startswith(("C", "R")) else 1
        paths.extend(parts[index + 1 : index + 1 + path_count])
        index += path_count + 1
    return paths


def untracked_paths() -> list[str]:
    """Return visible untracked paths."""
    return [
        path
        for path in git_output("ls-files", "--others", "--exclude-standard", "-z").split("\0")
        if path
    ]


def changed_paths(*, worktree: bool, base: str | None) -> list[str]:
    """Return staged paths or all branch/worktree paths relative to a base."""
    if not worktree:
        output = git_output("diff", "--cached", "--name-status", "-z", "--diff-filter=ACMRD")
        return sorted(set(parse_name_status(output)))
    comparison = base or "HEAD"
    comparison = git_output(
        "rev-parse", "--verify", "--end-of-options", comparison + "^{commit}"
    ).strip()
    output = git_output(
        "diff",
        "--name-status",
        "-z",
        "--diff-filter=ACMRD",
        comparison,
        "--",
    )
    return sorted(set(parse_name_status(output) + untracked_paths()))


def is_readme(path: str) -> bool:
    """Return whether a path names a README file."""
    return Path(path).name.casefold() == "readme.md"


def is_behavior_source(path: str) -> bool:
    """Return whether a changed path should prompt documentation review."""
    candidate = Path(path)
    return (
        candidate.suffix in SOURCE_SUFFIXES
        and not any(part in IGNORED_PARTS for part in candidate.parts)
        and candidate.name != ".pre-commit-config.yaml"
    )


def nearest_readme(path: str) -> str | None:
    """Find the nearest visible README, falling back to the repository root."""
    contained(REPO_ROOT / path)
    directory = Path(path).parent
    while directory != Path():
        candidate = directory / "README.md"
        if (REPO_ROOT / candidate).is_file():
            return candidate.as_posix()
        directory = directory.parent
    return "README.md" if (REPO_ROOT / "README.md").is_file() else None


def report(paths: list[str]) -> None:
    """Print warning-only README prompts grouped by nearest documentation owner."""
    changed_readmes = {path for path in paths if is_readme(path)}
    groups: dict[str, list[str]] = {}
    for source in filter(is_behavior_source, paths):
        readme = nearest_readme(source)
        if readme is None:
            groups.setdefault("No README found: create or identify documentation", []).append(
                source
            )
        elif readme not in changed_readmes:
            groups.setdefault(readme, []).append(source)
    if not groups:
        print("README coverage: no nearby documentation review prompts.")
        return
    print("README coverage review recommended (advisory):")
    for readme, sources in sorted(groups.items()):
        print(f"  {readme}")
        for source in sorted(sources):
            print(f"    - {source}")
    print("Confirm each prompt against behavior; this command never blocks a commit.")


def main() -> None:
    """Parse change selection and print the advisory report."""
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--staged", action="store_true", help="Review staged changes (default).")
    mode.add_argument(
        "--worktree",
        action="store_true",
        help="Review branch, tracked worktree, and visible untracked changes.",
    )
    parser.add_argument(
        "--base",
        help="Git revision to compare for --worktree (default: HEAD).",
    )
    args = parser.parse_args()
    if args.base and not args.worktree:
        parser.error("--base requires --worktree")
    git_root = Path(git_output("rev-parse", "--show-toplevel").strip()).resolve()
    if git_root != REPO_ROOT:
        parser.error("Copy this kit to a Git project root before using README change checks")
    report(changed_paths(worktree=args.worktree, base=args.base))


if __name__ == "__main__":
    main()
