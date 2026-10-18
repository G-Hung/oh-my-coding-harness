# Repository check examples

These two Python 3.11+ standard-library tools are optional examples. Copy this
directory to `tools/repository-checks/` in a Git project. Keep its tests with
the scripts. Edit both example TOML files to match that project's paths and
commands. No hook or CI configuration is installed.

`check_import_boundaries.py` reads Python files with `ast`. Each boundary rule
names a source directory, its import root (for example, `src` containing
top-level packages), and forbidden dotted import prefixes.
The check handles absolute and relative imports. A prefix matches one module or
its children, so `example.adapters` does not match `example.adapters_extra`.
Missing source directories, invalid syntax, and invalid config fail the check.
Rules should cover each architecture layer that needs a boundary; this tool
does not infer the intended dependency graph.

`select_checks.py` reads the Git merge-base diff, separate index/worktree diffs,
and visible untracked files. It retains both paths of renames. Each changed path
must match at least one check or an explicit ignore pattern. The default action
prints a JSON plan. `--run` executes the selected command arrays from the repo
root and stops on the first failure. Commands are trusted project configuration;
review them before enabling `--run` in a hook. This is a change selector, not a
complete release gate. Run all required checks separately before release.

From the target repository root, after editing the examples:

```sh
uv run --no-project python tools/repository-checks/check_import_boundaries.py \
  --config tools/repository-checks/boundaries.example.toml
uv run --no-project python tools/repository-checks/select_checks.py \
  --config tools/repository-checks/checks.example.toml --base HEAD
uv run --no-project python tools/repository-checks/select_checks.py \
  --config tools/repository-checks/checks.example.toml --base main --run
uv run --no-project python -m unittest discover \
  -s tools/repository-checks/tests -v
```

From the library root, before copying, run its tests with:

```sh
uv run --no-project python -m unittest discover -s examples/repository-checks/tests -v
```

Use an existing local Git ref for `--base`. `HEAD` selects current staged,
unstaged, and untracked changes; a branch also includes commits since their
merge base. Git ignored files are excluded. The example commands assume `uv`
and a Python test suite. The documentation command also assumes a
`tools/check_markdown_links.py` helper. Copy that helper from the library or
replace the command with the target project's existing documentation check.
For an existing virtual environment, use the project's own `uv run` options.

The import check reports each offending file and line and exits 1 for boundary
violations. Configuration or source errors exit 2. The selector exits 2 for
invalid configuration, unknown changes, or Git errors. A selected command's
failure exit code reaches the shell.
