# Python kit

The README reminder selects the nearest existing README, including a fallback
to the root README. Review its relevance; a local README is not required per module.

Copy this directory's contents into a project root, including `tools/`, `harness.toml`, and hidden files. For an existing project, merge configuration into its existing `pyproject.toml` and preserve its package manager, dependencies, hooks, and test conventions. Copy first, then adapt; the example `src/example` and its test exist only to demonstrate working wiring.

Requires Python 3.12+, uv, and Git for changed-file README prompts. Install dependencies once with network access:

```sh
uv sync --locked
uv run --frozen --offline python tools/check.py
```

The checked-in lockfile makes this example reproducible. After merging dependencies into an existing project, run `uv lock` and `uv sync`, review the resulting dependency changes, then run the gate again. A missing dependency, invalid configuration, or failed command fails the gate. No tool fixes files during validation.

## Choose a layer

```sh
# Fast static checks: lock, formatting, lint, types, links, file length
uv run --frozen --offline python tools/check.py --static-only
# Tests; pytest prints the 15 slowest durations from pytest configuration
uv run --frozen --offline python tools/check.py --tests-only
# Focused iteration; retain your project's test selection conventions
uv run --frozen --offline pytest tests/test_harness.py -q
# Documentation prompts for staged or all current changes
uv run --frozen --offline python tools/check_readme_coverage.py --staged
uv run --frozen --offline python tools/check_readme_coverage.py --worktree --base HEAD
# Independent checks
uv run --frozen --offline python tools/check_markdown_commonmark_links.py
uv run --frozen --offline python tools/check_max_lines.py
uv run --frozen --offline python tools/check_max_lines.py --strict
```

README prompts require this kit to be at the Git repository root; an invalid revision fails. Staged mode and worktree mode without `--base` work before the first commit. Worktree mode unions separate index, worktree, and visible untracked changes. With `--base`, it also includes branch commits since the merge base, retaining both sides of renames and deletions. A changed nearby README remains a prompt to verify accuracy; file co-change does not establish correctness.

The link checker uses `markdown-it-py` in CommonMark mode to verify local inline and defined reference-style links, including images and URL-encoded paths. It skips fenced/indented code and inline code. Full, collapsed, and shortcut references use case-insensitive labels. Undefined references are plain text in Markdown, not file targets. URL queries and fragments are ignored; encoded filename characters remain literal. Protocol-relative remote links are skipped. Root-relative targets are project-relative. It does not validate headings, network URLs, raw HTML links, or Markdown extensions outside CommonMark. File discovery excludes configured directories and rejects links outside the project root. It requires at least one Markdown file.

The max-lines check counts physical source lines, including comments and blanks. Its default is a review prompt, not a mandate to split a cohesive module. Use `--strict` only after choosing an appropriate threshold. Missing source roots or an empty source inventory are errors. Slow-test output identifies investigation candidates; there is no universal time or coverage quota.

## Adapt and verify

Edit the commented `harness.toml` roots, suffixes, exclusions, and line threshold. Ruff, Pyright, and pytest retain their native settings in `pyproject.toml`; update their scope when adapting the project. Inspect the command list in `tools/check.py` and add only relevant offline checks. Keep `tools/harness.py` with the dependent helpers. If adopting the link checker alone, also add `markdown-it-py` to the target environment and lockfile; copying the script does not install its parser. After adoption, introduce a temporary broken link, type error, and failing assertion in a disposable checkout to verify failures reach the shell, then remove them.

## Pre-commit and pre-push

Copy [.pre-commit-config.yaml](.pre-commit-config.yaml), together with the check
runner, helpers, and project configuration. Activation is opt-in. Run these commands
from the target project's Git root.

1. Inspect existing hooks before installation:

   ```sh
   git config --show-origin --get core.hooksPath
   git rev-parse --git-path hooks
   ```

   No configured `core.hooksPath` is normal. Inspect the effective directory and
   any existing `.pre-commit-config.yaml`. Merge entries rather than overwrite
   them. If another manager owns the hooks, integrate the check commands there.
   `pre-commit install` refuses a configured `core.hooksPath`; do not unset it just
   to force installation. With existing unmanaged hooks, inspect the migration
   behavior and preserve their checks; do not use `--overwrite` blindly.

2. Sync dependencies and test both stages before activation:

   ```sh
   uv sync --locked
   uv run --frozen --offline pre-commit validate-config
   uv run --frozen --offline pre-commit run python-static --hook-stage pre-commit --all-files
   uv run --frozen --offline pre-commit run python-readme --hook-stage pre-commit --all-files
   uv run --frozen --offline pre-commit run python-full --hook-stage pre-push --all-files
   ```

   These commands run the checks without committing or pushing. In a disposable
   checkout, introduce a lint or type error and confirm `python-static` fails.
   Restore it, introduce a failing test, and confirm `python-full` fails. Restore
   the fixture and rerun both stages successfully.

3. With no conflicting hook manager or hooks path, install both hook types:

   ```sh
   uv run --frozen --offline pre-commit install --hook-type pre-commit --hook-type pre-push
   git rev-parse --git-path hooks/pre-commit
   git rev-parse --git-path hooks/pre-push
   ```

   Inspect both returned files: each must be executable and contain the generated
   `pre-commit` launcher. Keep the synced environment available and repeat this
   verification in each checkout. Reinstall after moving or recreating an
   environment if a launcher points to an obsolete interpreter.

Pre-commit runs static checks and a visible staged README reminder; pre-push adds
tests. The reminder is advisory and runs separately from the static gate because
it needs the kit at the Git project root. A required command failure
blocks the operation. The default file-size check remains advisory. Neither stage
modifies files or checks commit messages. The configured commands run offline
after dependency setup and inspect the current worktree, not an isolated index
snapshot or every pushed ref. Formal verification is not enabled by these hooks.

Hooks do not replace final review and can be bypassed. Mirror required checks in
CI for shared enforcement. If you narrow a hook to reduce latency, retain the
equivalent required check in the final gate.
