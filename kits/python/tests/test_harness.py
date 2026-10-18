"""Exercise failure behavior and Git edge cases without application dependencies."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import check
import check_markdown_links as links
import check_readme_coverage as readmes
import pytest
from harness import ROOT, config, contained, files

from example import unique_names


def test_example_behavior() -> None:
    assert unique_names([" Ada ", "", "Ada", "Lin", "  "]) == ["Ada", "Lin"]


@pytest.fixture
def project(tmp_path: Path) -> Path:
    shutil.copy(ROOT / "harness.toml", tmp_path)
    for name in ("src", "tools", "tests"):
        (tmp_path / name).mkdir()
    (tmp_path / "src" / "example.py").write_text("value = 1\n")
    return tmp_path


def test_config_rejects_missing_roots(project: Path) -> None:
    (project / "tests").rmdir()
    with pytest.raises(ValueError, match="Missing configured"):
        config(project)


def test_walk_prunes_excluded_and_rejects_escape(project: Path, tmp_path: Path) -> None:
    ignored = project / "src" / ".venv"
    ignored.mkdir()
    (ignored / "hidden.py").write_text("pass\n")
    assert len(files(project, source_only=True)) == 1
    outside = tmp_path.parent / (tmp_path.name + "-outside.py")
    outside.write_text("private\n")
    try:
        (project / "src" / "escape.py").symlink_to(outside)
        with pytest.raises(ValueError, match="escapes"):
            files(project, source_only=True)
    finally:
        outside.unlink()


def test_link_targets_handle_titles_anchors_and_encoding() -> None:
    assert links.local_targets(
        '[one](<some%20file.md#section> "title") [web](https://example.org) [anchor](#top)'
    ) == ["some file.md"]


def test_links_fail_for_missing_and_escaping_targets(project: Path, monkeypatch) -> None:
    monkeypatch.setattr(links, "REPO_ROOT", project)
    monkeypatch.setattr(links, "markdown_paths", lambda: ["README.md"])
    monkeypatch.setattr(links, "contained", lambda path: contained(path, project))
    (project / "README.md").write_text("[missing](missing.md)")
    assert links.main() == 1
    (project / "README.md").write_text("[source](src/example.py)")
    assert links.main() == 0
    (project / "README.md").write_text("[escape](../outside.md)")
    with pytest.raises(ValueError, match="escapes"):
        links.main()


def test_name_status_preserves_renames_and_newlines() -> None:
    assert readmes.parse_name_status("R100\0old name.py\0new\nname.py\0D\0gone.py\0") == [
        "old name.py",
        "new\nname.py",
        "gone.py",
    ]


def test_git_staged_paths_and_invalid_base(project: Path, monkeypatch) -> None:
    monkeypatch.setattr(readmes, "REPO_ROOT", project)
    subprocess.run(["git", "init", "-q", str(project)], check=True)
    path = project / "src" / "space\nname.py"
    path.write_text("pass\n")
    subprocess.run(["git", "add", "src"], cwd=project, check=True)
    assert "src/space\nname.py" in readmes.changed_paths(worktree=False, base=None)
    with pytest.raises(subprocess.CalledProcessError):
        readmes.changed_paths(worktree=True, base="missing-revision")


def test_missing_readme_is_advisory(project: Path, monkeypatch, capsys) -> None:
    monkeypatch.setattr(readmes, "REPO_ROOT", project)
    monkeypatch.setattr(readmes, "contained", lambda path: path)
    readmes.report(["src/example.py"])
    assert "No README found" in capsys.readouterr().out


def test_check_modes() -> None:
    assert check.commands(tests_only=True) == [[check.sys.executable, "-m", "pytest"]]
    assert all("pytest" not in command for command in check.commands(static_only=True))


def test_max_lines_strict_and_empty_inventory(project: Path, monkeypatch) -> None:
    import check_max_lines as limits

    monkeypatch.setattr(limits, "ROOT", project)
    monkeypatch.setattr(limits, "config", lambda: {"max_lines": 1})
    path = project / "src" / "example.py"
    path.write_text("one\ntwo\n")
    monkeypatch.setattr(limits, "files", lambda **kwargs: [path])
    monkeypatch.setattr(
        limits.argparse.ArgumentParser,
        "parse_args",
        lambda self: type("Args", (), {"strict": True})(),
    )
    assert limits.main() == 1
    monkeypatch.setattr(limits, "files", lambda **kwargs: [])
    with pytest.raises(ValueError, match="No source files"):
        limits.main()


def test_links_parse_urls_before_decoding_files(project: Path, monkeypatch) -> None:
    monkeypatch.setattr(links, "REPO_ROOT", project)
    monkeypatch.setattr(links, "markdown_paths", lambda: ["README.md"])
    monkeypatch.setattr(links, "contained", lambda path: contained(path, project))
    for name in ("some file.md", "literal#name.md", "literal?name.md"):
        (project / name).write_text("target\n")
    (project / "README.md").write_text(
        "[remote](//example.org/docs)\n"
        "[query](README.md?plain=1#section)\n"
        "[space](some%20file.md)\n"
        "[hash](literal%23name.md)\n"
        "[question](literal%3Fname.md?plain=1#section)\n"
    )
    assert links.main() == 0
    (project / "literal?name.md").unlink()
    assert links.main() == 1


def test_links_skip_code_and_follow_used_references() -> None:
    source = """[full][Target] ![picture][image] [Collapsed][] [shortcut]

[Target]: <some%20file.md#section> "title"
[image]: image.png
[Collapsed]: collapsed.md
[shortcut]: shortcut.md
[unused]: unused.md

````md
[bad](missing.md)
```
[bad][Target]
````
~~~md
[bad](also-missing.md)
~~~
`[bad](inline.md)` and ``[bad](more-inline.md)``

    [bad](indented.md)
[real](guide.md) [remote](https://example.org)
"""
    assert links.local_targets(source) == [
        "some file.md",
        "image.png",
        "collapsed.md",
        "shortcut.md",
        "guide.md",
    ]


def test_reference_link_missing_target_fails(project: Path, monkeypatch) -> None:
    monkeypatch.setattr(links, "REPO_ROOT", project)
    monkeypatch.setattr(links, "markdown_paths", lambda: ["README.md"])
    monkeypatch.setattr(links, "contained", lambda path: contained(path, project))
    (project / "README.md").write_text("[guide][ref]\n\n[ref]: missing.md\n")
    assert links.main() == 1
    (project / "missing.md").write_text("# Guide")
    assert links.main() == 0


def git_fixture(root: Path, *args: str) -> str:
    return subprocess.run(
        [
            "git",
            "-c",
            "user.name=Harness Test",
            "-c",
            "user.email=test@example.invalid",
            "-c",
            "commit.gpgsign=false",
            *args,
        ],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def test_readme_local_changes_before_first_commit(project: Path, monkeypatch) -> None:
    monkeypatch.setattr(readmes, "REPO_ROOT", project)
    git_fixture(project, "init", "-q")
    git_fixture(project, "add", "src/example.py")
    (project / "src/untracked.py").write_text("value = 3\n")
    paths = readmes.changed_paths(worktree=True, base=None)
    assert {"src/example.py", "src/untracked.py"}.issubset(paths)
    assert readmes.changed_paths(worktree=False, base=None) == ["src/example.py"]


def test_readme_keeps_staged_change_cancelled_by_worktree(project: Path, monkeypatch) -> None:
    monkeypatch.setattr(readmes, "REPO_ROOT", project)
    git_fixture(project, "init", "-q")
    git_fixture(project, "add", ".")
    git_fixture(project, "commit", "-qm", "baseline")
    path = project / "src/example.py"
    original = path.read_text()
    path.write_text("value = 2\n")
    git_fixture(project, "add", "src/example.py")
    path.write_text(original)
    assert "src/example.py" in readmes.changed_paths(worktree=True, base=None)
    assert "src/example.py" in readmes.changed_paths(worktree=True, base="HEAD")


def test_readme_branch_merge_base_renames_and_deletions(project: Path, monkeypatch) -> None:
    monkeypatch.setattr(readmes, "REPO_ROOT", project)
    git_fixture(project, "init", "-q")
    git_fixture(project, "add", ".")
    git_fixture(project, "commit", "-qm", "baseline")
    baseline = git_fixture(project, "rev-parse", "HEAD")
    git_fixture(project, "checkout", "-qb", "base")
    (project / "src/base_only.py").write_text("value = 0\n")
    git_fixture(project, "add", ".")
    git_fixture(project, "commit", "-qm", "base update")
    git_fixture(project, "checkout", "-qb", "feature", baseline)
    git_fixture(project, "mv", "src/example.py", "src/renamed.py")
    git_fixture(project, "commit", "-qm", "rename")
    (project / "src/renamed.py").unlink()
    paths = readmes.changed_paths(worktree=True, base="base")
    assert {"src/example.py", "src/renamed.py"}.issubset(paths)
    assert "src/base_only.py" not in paths


def test_changed_readme_still_prompts_for_accuracy(project: Path, monkeypatch, capsys) -> None:
    monkeypatch.setattr(readmes, "REPO_ROOT", project)
    monkeypatch.setattr(readmes, "contained", lambda path: path)
    (project / "README.md").write_text("# Changed but potentially stale")
    readmes.report(["src/example.py", "README.md"])
    result = capsys.readouterr().out
    assert "README.md" in result and "verify accuracy" in result and "src/example.py" in result


def test_links_distinguish_nested_content_from_code() -> None:
    assert links.local_targets("- Parent\n    - [broken](missing.md)\n") == ["missing.md"]
    assert links.local_targets("Paragraph continues\n    [guide](guide.md)\n") == ["guide.md"]
    assert links.local_targets("    [example](not-a-link.md)\n") == []
    assert links.local_targets(
        "> ```md\n> [example](not-a-link.md)\n> ```\n> [real](guide.md)\n"
    ) == ["guide.md"]
    assert links.local_targets("[nested](path(with(parens)).md) [code `label`](real.md)") == [
        "path(with(parens)).md",
        "real.md",
    ]
