# Asset catalog

Use these examples to understand the problems and compare your project's approach.
Borrow useful ideas in its ecosystem; read each reused tool with its helpers.

## Detailed agent instructions

Under `docs/agent-guidelines/` are detailed instructions on **how and what to do**.
Copy only relevant documents or sections. General guides stand alone; use the
[dependency bundles](adoption.md#skill-bundles-to-copy) for modular skills.

Use the [topic index](agent-guidelines/README.md) to select compact engineering
guides for design/reuse, contracts/naming, composition/patterns, state/recovery,
debugging, and testing. They include practical examples; agents
do not need to load the whole catalog. Keep only adopted links when copying an index.

| File | What it tells the agent to do |
| --- | --- |
| [Workflow](../docs/agent-guidelines/workflow.md) | Establish the task, finish the approved scope, integrate changes, resolve review findings, and report the actual Git state. |
| [Verification](../docs/agent-guidelines/verification.md) | Choose checks for the changed behavior, inspect failures and skipped tests, maintain hooks/worktrees, and manage local servers. |
| [Code style](../docs/agent-guidelines/code-style.md) | Follow coding conventions, reuse existing owners of rules, preserve behavior during refactoring, and keep types, state, and abstractions clear. |
| [Documentation](../docs/agent-guidelines/documentation.md) | Apply ASD-STE100-inspired writing, update nearby READMEs, preserve precise contracts, and maintain useful comments and generated docs. |
| [Safety](../docs/agent-guidelines/safety.md) | Handle credentials, environment changes, migrations, external effects, and shared resources. |
| [Formal verification](../docs/agent-guidelines/formal-verification.md) | Choose a bounded protocol, map transitions to code, test negative controls and reachability, and report what the evidence covers. |
| [README standard](../docs/readme-standard.md) | Write useful subsystem, feature, and small-folder READMEs: ownership, invariants, decisions, verification, and history instead of narrated code. |
| [Code-sweep skill](../.agents/skills/code-sweep/SKILL.md) | Review recent work and recurring avoidable problems; report improvements without implementing fixes. Its workflow is contained in the skill. |

## Scripts and stack setup

Scripts live in `kits/typescript/scripts/`, `kits/python/tools/`, and the small
standalone examples below. They include editable roots, exclusions, and limits.

| Check | TypeScript | Python | Purpose |
| --- | --- | --- | --- |
| Maximum file lines | [check-loc.cjs](../kits/typescript/scripts/check-loc.cjs) | [check_max_lines.py](../kits/python/tools/check_max_lines.py) | Report oversized files for refactoring review. Configurable limit; `--strict` makes it blocking. |
| Nearest existing README reminder | [check-readme-coverage.cjs](../kits/typescript/scripts/check-readme-coverage.cjs) | [check_readme_coverage.py](../kits/python/tools/check_readme_coverage.py) | Prompt review of the closest existing README, falling back to the root README. Advisory; it does not require a README in every module. |
| Markdown links | [check-markdown-commonmark-links.cjs](../kits/typescript/scripts/check-markdown-commonmark-links.cjs) | [check_markdown_commonmark_links.py](../kits/python/tools/check_markdown_commonmark_links.py) | Detect broken local documentation links. The Python kit requires `markdown-it-py`; the TypeScript kit uses its declared parser dependencies. |
| Slow tests | [test-profile.cjs](../kits/typescript/scripts/test-profile.cjs) + [test-profile-summary.cjs](../kits/typescript/scripts/test-profile-summary.cjs) | `pytest --durations=15` | Show the most expensive tests so agents can investigate setup and runtime costs. |
| Combined checks | [check-local.cjs](../kits/typescript/scripts/check-local.cjs) | [check.py](../kits/python/tools/check.py) | Run the configured checks and return a failing exit status when a required check fails. |
| Setup diagnosis | [check-doctor.cjs](../kits/typescript/scripts/check-doctor.cjs) | `uv sync --locked` for setup; the combined gate verifies tools | Identify missing runtime/tooling prerequisites. Dependency installation is a separate setup step. |
| Check configuration and shared helpers | [harness.config.cjs](../kits/typescript/harness.config.cjs) + [scripts/lib/](../kits/typescript/scripts/lib/) | [harness.toml](../kits/python/harness.toml) + [harness.py](../kits/python/tools/harness.py) | Adapt paths and thresholds; copy required helpers with each selected script. |

For complete setup and exact copy dependencies:

- **[TypeScript kit](../kits/typescript/README.md):** npm, TypeScript, ESLint, Jest,
  the scripts above, small test fixtures, and optional pre-commit/pre-push hooks.
- **[Python kit](../kits/python/README.md):** uv, Ruff, Pyright, pytest, the helpers
  above, small test fixtures, and optional pre-commit/pre-push hooks.
- **[Port inspection](../examples/ports/README.md):** a standalone Node + `lsof`
  script to list listeners and suggest a port. It never kills another process.
- **[Formal starter](../examples/formal/README.md):** a standalone Python runner,
  pinned TLC tool setup, one bounded cache model, and executable Python and
  TypeScript examples. It includes guard-removal controls, reachability witnesses,
  implementation tests, input hashes, and retained failure logs.
- **[Documentation portability tools](../tools/README.md):** Python standard-library
  checks for local Markdown links and machine-specific paths.

### Standalone checks

These tools can be adopted without either stack kit. Each guide lists the files to
copy, configuration, commands, and tests. Add selected checks to the project's
existing scripts or hooks after approving the adoption plan.

| Tool | What it provides | When to use it |
| --- | --- | --- |
| [Git conflicts and overlaps](../examples/git-checks/README.md) | Check a target commit against a base and selected peer refs; report merge conflicts and files changed by both branches. | Multiple branches or agents work in the same repository. Uses Node and Git. |
| [Remote and PR conflicts](../tools/README.md#remote-conflict-check) | Fetch the integration branch, open GitHub PR heads, and selected remote branches; block merge conflicts while allowing clean same-file overlaps. | Check local commits before pushing. Uses Python and Git, plus authenticated `gh` for GitHub PR discovery. |
| [npm dependency audit](../examples/git-checks/README.md) | Audit the locked dependency graph, including development dependencies, at a selected severity threshold; reject malformed reports and manifest/lockfile mismatches. | A project uses npm and a package lockfile. Accepts a saved report or an explicitly requested online audit. |
| [Python import boundaries](../examples/repository-checks/README.md) | Check absolute and relative imports against configured module boundaries. | A Python project has layers that must remain independent. |
| [Changed-path check selection](../examples/repository-checks/README.md) | Map changed paths to configured checks, show the plan, and run selected commands when requested. | A repository has several areas with different checks. The commands can use any language; the planner runs on Python. |

The existing kit checks cover README reminders, local links, file sizes, and test
profiling. Keep those implementations when they already fit. App-specific build
wrappers, service login, billing or data maintenance, and product test registries
stay in the adopting project; use its actual commands and contracts instead of
copying another application's setup.

The kits are examples to adapt, not a requirement to replace a working test runner
or package manager. Their tiny source/test fixtures verify wiring, not your app.
There is no required test-suite taxonomy or universal coverage percentage.

## Pre-commit and pre-push

For this library's own active integration, including commit-msg, see the
[maintenance guide](maintenance.md). The kits below remain separately adopted
examples; their existing hooks do not validate commit messages.

Use hooks to catch failures before they enter a commit or leave your machine.
Both kits include working examples. **Copying the files does not enable them.**

| Kit | Before commit | Before push | Files and setup |
| --- | --- | --- | --- |
| TypeScript | Lint, types, and advisory staged README prompts | Full configured gate: lint, types, tests, harness tests, file-size prompts, and local links | [pre-commit](../kits/typescript/hooks/pre-commit), [pre-push](../kits/typescript/hooks/pre-push), [setup](../kits/typescript/README.md#pre-commit-and-pre-push) |
| Python | Static checks and advisory staged README prompts | Static checks plus tests | [.pre-commit-config.yaml](../kits/python/.pre-commit-config.yaml), [setup](../kits/python/README.md#pre-commit-and-pre-push) |

Ask the adopting agent to inspect the existing hook manager and effective hook
directory, propose how to merge these checks, and include activation in its
adoption plan. After approval, install dependencies, test both stages directly,
then enable and verify both hooks using the selected kit's commands. Do this in
the target project, not in this library.

A required command failure blocks the Git operation. README and default file-size
prompts remain advisory. Neither kit formats files, stages changes, or controls
commit messages. The examples check the current worktree; they do not isolate the
index or validate every pushed ref. Hooks can be bypassed, so use CI for required
shared enforcement. Formal verification is a separate, optional adoption.

## Try the formal example

From `examples/formal/`, use Python 3.10+ and Java 21+:

```sh
python3 verify.py setup
python3 verify.py --manifest python.json
```

Setup explicitly downloads and verifies the pinned checker. The run checks seven
model configurations and five implementation tests. For the TypeScript example,
also use Node 24+ and select `--manifest typescript.json`.

The example shows why an old cache fill needs an invalidation token and why a
new request must not join an obsolete load. Copy it, replace its source/test
mapping with your actual code, and run a meaningful failure before adopting it.
A passing sample does not validate your application. Read the
[formal starter guide](../examples/formal/README.md) for copy dependencies, bounds,
reports, and commands that run the implementation tests without Java.
