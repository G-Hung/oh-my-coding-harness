"""Behavior tests for the copyable check examples."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import check_import_boundaries  # noqa: E402
import select_checks  # noqa: E402


class ImportBoundaryTests(unittest.TestCase):
    def test_relative_imports_in_package_initializers(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "src/example/domain/__init__.py"
            source.parent.mkdir(parents=True)
            for statement, forbidden in (
                ("from .. import adapters", "example.adapters"),
                ("from . import adapters", "example.domain.adapters"),
            ):
                with self.subTest(statement=statement):
                    source.write_text(statement + "\n", encoding="utf-8")
                    errors = check_import_boundaries.forbidden_imports(
                        source, root / "src", [forbidden]
                    )
                    self.assertEqual(1, len(errors), errors)
                    self.assertIn("forbidden import " + forbidden, errors[0])

    def test_absolute_relative_and_alias_imports(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "src" / "example" / "domain"
            source.mkdir(parents=True)
            (source / "ok.py").write_text("import example.adapters_extra\n", encoding="utf-8")
            (source / "bad.py").write_text(
                "import example.adapters.http\n"
                "from ..adapters import sql\n"
                "from example import adapters\n",
                encoding="utf-8",
            )
            config = root / "boundaries.toml"
            config.write_text(
                '[[boundaries]]\npackage_root = "src"\n'
                'source = "src/example/domain"\nforbidden = ["example.adapters"]\n',
                encoding="utf-8",
            )
            errors = check_import_boundaries.check(root, config)
            self.assertEqual(3, len(errors), errors)
            self.assertTrue(all("bad.py" in error for error in errors))

    def test_missing_scope_and_syntax_error_fail(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = root / "boundaries.toml"
            config.write_text(
                '[[boundaries]]\npackage_root = "src"\n'
                'source = "src/example/domain"\nforbidden = ["example.adapters"]\n',
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "missing source"):
                check_import_boundaries.check(root, config)
            source = root / "src/example/domain"
            source.mkdir(parents=True)
            with self.assertRaisesRegex(ValueError, "no Python files"):
                check_import_boundaries.check(root, config)
            (source / "broken.py").write_text("from (\n", encoding="utf-8")
            with self.assertRaises(SyntaxError):
                check_import_boundaries.check(root, config)

    def test_string_forbidden_list_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "src/example/domain"
            source.mkdir(parents=True)
            (source / "service.py").write_text("pass\n", encoding="utf-8")
            config = root / "boundaries.toml"
            config.write_text(
                '[[boundaries]]\npackage_root = "src"\n'
                'source = "src/example/domain"\nforbidden = "example.adapters"\n',
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "invalid forbidden"):
                check_import_boundaries.check(root, config)


class SelectionTests(unittest.TestCase):
    def git(self, root: Path, *args: str) -> None:
        subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)

    def test_rename_untracked_and_uncovered_paths(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.git(root, "init", "-q")
            self.git(root, "config", "user.name", "Fixture")
            self.git(root, "config", "user.email", "fixture@example.invalid")
            (root / "src").mkdir()
            (root / "src/old.py").write_text("pass\n", encoding="utf-8")
            self.git(root, "add", ".")
            self.git(root, "commit", "-qm", "initial")
            self.git(root, "mv", "src/old.py", "src/new.py")
            (root / "notes.md").write_text("note\n", encoding="utf-8")
            paths = select_checks.changed_paths(root, "HEAD")
            self.assertEqual(["notes.md", "src/new.py", "src/old.py"], paths)
            config = {
                "checks": [{"name": "python", "paths": ["src/*"], "command": ["true"]}],
                "selection": {"ignore": ["*.md"]},
            }
            self.assertEqual(
                ["src/new.py", "src/old.py"], select_checks.plan(paths, config)[0]["paths"]
            )
            config["selection"]["ignore"] = []
            with self.assertRaisesRegex(ValueError, "notes.md"):
                select_checks.plan(paths, config)

    def test_invalid_configuration_fails(self) -> None:
        with self.assertRaisesRegex(ValueError, "at least one"):
            select_checks.plan(["src/app.py"], {})
        with self.assertRaisesRegex(ValueError, "unique names"):
            select_checks.plan(
                ["src/app.py"],
                {
                    "checks": [
                        {"name": "same", "paths": ["src/*"], "command": ["true"]},
                        {"name": "same", "paths": ["*.py"], "command": ["true"]},
                    ]
                },
            )
        with self.assertRaisesRegex(ValueError, "path patterns"):
            select_checks.plan(
                ["src/app.py"],
                {"checks": [{"name": "python", "paths": "src/*", "command": ["true"]}]},
            )

    def test_staged_change_remains_selected_when_worktree_reverts_it(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.git(root, "init", "-q")
            self.git(root, "config", "user.name", "Fixture")
            self.git(root, "config", "user.email", "fixture@example.invalid")
            source = root / "app.py"
            source.write_text("old\n", encoding="utf-8")
            self.git(root, "add", ".")
            self.git(root, "commit", "-qm", "initial")
            source.write_text("new\n", encoding="utf-8")
            self.git(root, "add", ".")
            source.write_text("old\n", encoding="utf-8")
            self.assertEqual(["app.py"], select_checks.changed_paths(root, "HEAD"))

    def test_run_propagates_failure_and_missing_executable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.git(root, "init", "-q")
            self.git(root, "config", "user.name", "Fixture")
            self.git(root, "config", "user.email", "fixture@example.invalid")
            (root / "src").mkdir()
            (root / "src/app.py").write_text("pass\n", encoding="utf-8")
            self.git(root, "add", ".")
            self.git(root, "commit", "-qm", "initial")
            (root / "src/app.py").write_text("print('changed')\n", encoding="utf-8")
            config = root / "checks.toml"
            for command, expected in (("false", 1), ("missing-test-executable-xyz", 2)):
                config.write_text(
                    '[[checks]]\nname = "sample"\npaths = ["src/*"]\n'
                    f'command = ["{command}"]\n'
                    '[selection]\nignore = ["checks.toml"]\n',
                    encoding="utf-8",
                )
                with mock.patch.object(
                    sys,
                    "argv",
                    ["select_checks.py", "--root", str(root), "--config", "checks.toml", "--run"],
                ):
                    self.assertEqual(expected, select_checks.main())


if __name__ == "__main__":
    unittest.main()
