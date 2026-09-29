# Python kit

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
uv run --frozen --offline python tools/check_markdown_links.py
uv run --frozen --offline python tools/check_max_lines.py
uv run --frozen --offline python tools/check_max_lines.py --strict
```

README prompts require this kit to be at the Git repository root; an invalid revision fails. Staged mode works before the first commit. Worktree mode compares a commit (default `HEAD`) against the index and working tree and includes visible untracked files; both sides of renames and deletions are considered. A changed nearby README suppresses a prompt but does not prove documentation accuracy. Inspect the behavior yourself.

The link checker verifies local file targets in inline Markdown links, including images and URL-encoded paths. URL queries and fragments are ignored; encoded filename characters remain literal. Protocol-relative remote links are skipped. Root-relative targets are project-relative. It does not validate headings, network URLs, reference-style links, or full Markdown syntax; code examples containing inline link syntax are also checked. File discovery excludes configured directories and rejects links outside the project root. Keep examples self-contained. It requires at least one Markdown file.

The max-lines check counts physical source lines, including comments and blanks. Its default is a review prompt, not a mandate to split a cohesive module. Use `--strict` only after choosing an appropriate threshold. Missing source roots or an empty source inventory are errors. Slow-test output identifies investigation candidates; there is no universal time or coverage quota.

## Adapt and verify

Edit the commented `harness.toml` roots, suffixes, exclusions, and line threshold. Ruff, Pyright, and pytest retain their native settings in `pyproject.toml`; update their scope when adapting the project. Inspect the command list in `tools/check.py` and add only relevant offline checks. Keep `tools/harness.py` with the dependent helpers. After adoption, introduce a temporary broken link, type error, and failing assertion in a disposable checkout to verify failures reach the shell, then remove them.

## Optional hooks

Merge `.pre-commit-config.yaml` with existing hooks, then explicitly install:

```sh
uv run pre-commit install --hook-type pre-commit --hook-type pre-push
```

Pre-commit runs static checks; pre-push runs the complete gate. Neither modifies files or checks commit messages. Hooks require the already-synced environment and do not replace final review. Remove or narrow a hook if its latency makes local iteration impractical; preserve the equivalent final check.
