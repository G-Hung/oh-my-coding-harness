"""Shared editable configuration and bounded file discovery."""

from __future__ import annotations

import os
import tomllib
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def config(root: Path = ROOT) -> dict[str, Any]:
    with (root / "harness.toml").open("rb") as stream:
        value = tomllib.load(stream)
    for key in ("roots", "exclude", "source_suffixes", "behavior_suffixes"):
        if not isinstance(value.get(key), list) or not all(
            isinstance(item, str) and item for item in value[key]
        ):
            raise ValueError(f"harness.toml: {key} must be a list of nonempty strings")
    if not value["roots"] or not value["source_suffixes"]:
        raise ValueError("harness.toml: roots and source_suffixes cannot be empty")
    if type(value.get("max_lines")) is not int or value["max_lines"] < 1:
        raise ValueError("harness.toml: max_lines must be a positive integer")
    for name in value["roots"]:
        candidate = contained(root / name, root)
        if not candidate.is_dir():
            raise ValueError(f"Missing configured directory: {name}")
    return value


def contained(path: Path, root: Path = ROOT) -> Path:
    resolved = path.resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise ValueError(f"Path escapes project root: {path}")
    return resolved


def files(root: Path = ROOT, *, source_only: bool = False) -> list[Path]:
    settings = config(root)
    starts = [root / name for name in settings["roots"]] if source_only else [root]
    found: set[Path] = set()
    for start in starts:
        for directory, dirs, names in os.walk(start, followlinks=False):
            dirs[:] = [name for name in dirs if name not in settings["exclude"]]
            for name in dirs:
                contained(Path(directory) / name, root)
            for name in names:
                path = Path(directory) / name
                contained(path, root)
                if source_only and path.suffix not in settings["source_suffixes"]:
                    continue
                if path.is_file():
                    found.add(path)
    return sorted(found)
