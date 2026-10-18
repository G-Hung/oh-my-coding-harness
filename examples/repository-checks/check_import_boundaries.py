"""Reject Python imports that cross configured package boundaries."""

from __future__ import annotations

import argparse
import ast
import sys
import tomllib
from pathlib import Path


def inside(root: Path, value: str) -> Path:
    root = root.resolve()
    path = (root / value).resolve()
    if not path.is_relative_to(root):
        raise ValueError(f"configured path escapes repository: {value}")
    return path


def forbidden_imports(path: Path, package_root: Path, forbidden: list[str]) -> list[str]:
    """Return diagnostics for absolute and relative imports in one source file."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    parts = list(path.relative_to(package_root).with_suffix("").parts)
    context = parts[:-1]
    found: list[str] = []

    def inspect(name: str, line: int) -> bool:
        blocked = any(name == prefix or name.startswith(prefix + ".") for prefix in forbidden)
        if blocked:
            found.append(f"{path}:{line}: forbidden import {name}")
        return blocked

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                inspect(alias.name, node.lineno)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                if node.level > len(context):
                    found.append(f"{path}:{node.lineno}: relative import escapes package")
                    continue
                base = context[: len(context) - node.level + 1]
                base.extend((node.module or "").split(".") if node.module else [])
                module = ".".join(base)
            else:
                module = node.module or ""
            if not inspect(module, node.lineno):
                for alias in node.names:
                    if alias.name != "*":
                        inspect(f"{module}.{alias.name}" if module else alias.name, node.lineno)
    return found


def check(root: Path, config: Path) -> list[str]:
    root = root.resolve()
    data = tomllib.loads(config.read_text(encoding="utf-8"))
    rules = data.get("boundaries", [])
    if not rules:
        raise ValueError("configuration needs at least one [[boundaries]] rule")
    errors: list[str] = []
    for rule in rules:
        package_root = inside(root, rule["package_root"])
        source = inside(root, rule["source"])
        forbidden = rule["forbidden"]
        if not source.is_dir() or not source.is_relative_to(package_root):
            raise ValueError(f"missing source or outside package root: {rule['source']}")
        if not isinstance(forbidden, list) or not forbidden or any(
            not isinstance(item, str) or not item for item in forbidden
        ):
            raise ValueError(f"invalid forbidden imports for {rule['source']}")
        paths = sorted(source.rglob("*.py"))
        if not paths:
            raise ValueError(f"no Python files in source: {rule['source']}")
        for path in paths:
            if not path.resolve().is_relative_to(root):
                raise ValueError(f"source file escapes repository: {path}")
            errors.extend(forbidden_imports(path, package_root, forbidden))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        config = inside(root, str(args.config))
        errors = check(root, config)
    except (OSError, ValueError, KeyError, TypeError, SyntaxError) as exc:
        print(f"Import boundary check failed: {exc}", file=sys.stderr)
        return 2
    for error in errors:
        print(error, file=sys.stderr)
    if errors:
        return 1
    print("Import boundaries passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
