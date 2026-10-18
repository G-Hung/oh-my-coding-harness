"""Exercise path-check behavior independently of the library's current content."""

import importlib.util
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest.mock import patch


def load(name: str) -> Any:
    spec = importlib.util.spec_from_file_location(
        name, Path(__file__).resolve().parents[1] / (name + ".py")
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


links = load("check_markdown_links")
portability = load("check_portability")


class LibraryChecks(unittest.TestCase):
    def test_links_ignore_code_external_urls_and_decode_paths(self):
        source = """[guide](docs/guide.md#section)
[spaces](<docs/a%20b.md>)
[web](https://example.com/page)
[web-relative](//example.com/page)
[query](docs/guide.md?plain=1#section)
[encoded](docs/hash%23question%3F.md)
`[snippet](missing.md)`
```md
[example](not-real.md)
```
"""
        self.assertEqual(
            links.local_targets(source),
            ["docs/guide.md", "docs/a b.md", "docs/guide.md", "docs/hash#question?.md"],
        )

    def test_link_check_rejects_missing_and_outside_targets(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            old_root, old_paths = links.REPO_ROOT, links.markdown_paths
            try:
                links.REPO_ROOT = root
                links.markdown_paths = lambda: ["README.md"]
                (root / "README.md").write_text("[exists](file.md)")
                (root / "file.md").write_text("a real target")
                self.assertEqual(links.main(), 0)
                (root / "README.md").write_text("[missing](missing.md)")
                self.assertEqual(links.main(), 1)
                (root / "README.md").write_text("[outside](../)")
                self.assertEqual(links.main(), 1)
            finally:
                links.REPO_ROOT, links.markdown_paths = old_root, old_paths

    def test_machine_paths_and_intentional_example(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            old_root = portability.REPO_ROOT
            try:
                portability.REPO_ROOT = root
                file = root / "sample.md"
                file.write_text("/" + "Users/example/project\n")
                self.assertEqual(len(portability.find_violations(file)), 1)
                file.write_text("C:" + "\\" + "example\\project\n")
                self.assertEqual(len(portability.find_violations(file)), 1)
                file.write_text("C:" + "\\\\" + "example\\\\project\n")
                self.assertEqual(len(portability.find_violations(file)), 1)
                file.write_text("/" + "Users/example/project # portability-check: ignore\n")
                self.assertEqual(portability.find_violations(file), [])
            finally:
                portability.REPO_ROOT = old_root

    def test_formal_sources_receive_the_same_portability_checks(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            old_root = portability.REPO_ROOT
            try:
                portability.REPO_ROOT = root
                for suffix in (".tla", ".cfg"):
                    source = root / ("Model" + suffix)
                    source.write_text("/" + "Users/example/private-model\n")
                    self.assertTrue(portability.should_check(source))
                    self.assertEqual(len(portability.find_violations(source)), 1)
            finally:
                portability.REPO_ROOT = old_root

    def test_portability_rejects_ancestor_symlink_before_reading(self):
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary).resolve()
            root, outside = parent / "repo", parent / "outside"
            root.mkdir()
            outside.mkdir()
            (outside / "file.md").write_text("must not read")
            (root / "docs").symlink_to(outside, target_is_directory=True)
            old_root = portability.REPO_ROOT
            try:
                portability.REPO_ROOT = root
                with patch.object(
                    portability.subprocess,
                    "run",
                    return_value=SimpleNamespace(stdout="docs/file.md\0"),
                ):
                    with self.assertRaisesRegex(ValueError, "escapes repository root"):
                        portability.iter_repo_files()
            finally:
                portability.REPO_ROOT = old_root


if __name__ == "__main__":
    unittest.main()
