# oh-my-coding-harness

Agent instructions, ship skills, and validation scripts to copy into your own
projects. These are the pieces of my coding workflow: establish the scope, choose
how to execute it, run meaningful checks, review and fix until resolved, and
regularly inspect the codebase for problems.

Pick individual files or a whole stack kit. **After approval, copy the files first,
then modify them and add your project's context.** You do not need everything here.

## Ask your agent to assess it

> Check this repository's README against my existing project. Identify which
> instructions, skills, and scripts would be useful to integrate. Show me a plan:
> what you would copy, how you would adapt it, and the risks or conflicts with my
> current setup. Ask for my permission before making changes. Once approved,
> copy the selected files first, then modify them and add my project's context.

This README lists the available files so the agent can select relevant items
without a separate codebase walkthrough. Its proposal should name the files and
required helpers, the changes it would make, and how it would verify them.

## What this workflow preserves

The main agent owns scope, integration, validation, and handoff. It can implement
directly, reuse a worker, or delegate more work when the task benefits. The Codex
ship skill defaults execution to Terra Medium, adapts capability to the assignment,
and keeps one independent Astra Medium reviewer through the complete fix/recheck
loop. Model choices and required checks are separate decisions.

The goal is lower total task cost while keeping meaningful validation and resolved
review findings. Coordination, repairs, and review all count; using a cheaper model
does not by itself prove savings. The core Markdown guides remain model-neutral
so another agent can adopt the same ownership and completion rules.

Useful detail belongs here: conditions, examples, invariants, recovery procedures,
and the reasons behind decisions. Keep the always-loaded instructions focused and
read detailed guidance when relevant. Do not shorten a workflow by deleting the
steps that make it safe to execute, or replace a project's rules with generic prose.

## AGENTS.md and skills

These are the basic starting points for directing an agent's work.

| File | What it contains |
| --- | --- |
| [AGENTS.md template](templates/AGENTS.md) | Working rules: trace callers and contracts, reuse existing code, fix root causes, keep failures visible, verify behavior, and finish the authorized scope. Add your project's commands and conventions. |
| [Ship-cycle skill](adapters/codex/.agents/skills/ship-cycle/SKILL.md) | Adaptive execution, exclusive ownership across nested helpers, integration, required checks, one Astra Medium reviewer/fix loop, final validation, and design assessment. Includes an optional Luna-only execution policy. |
| [Weekly-sweep skill](adapters/codex/.agents/skills/weekly-sweep/SKILL.md) | Broadly scan active areas; deeply investigate the last two weeks, affected contracts, and concrete risks. Preserve required integration runs, dependency and README audits, and explicit coverage limits. |

Both skills are **self-contained**. Copy either skill folder into your project's
`.agents/skills/` directory for Codex, or adapt the instructions to your agent.
Neither needs this repository's docs. The ship skill leaves work uncommitted
unless the task explicitly authorizes commits. The sweep does not create a schedule.

## Detailed agent instructions

Under `docs/agent-guidelines/` are detailed instructions on **how and what to do**.
Copy only the relevant documents or sections; each procedure can stand on its own.

| File | What it tells the agent to do |
| --- | --- |
| [Workflow](docs/agent-guidelines/workflow.md) | Establish the task, finish the approved scope, integrate changes, resolve review findings, and report the actual Git state. |
| [Verification](docs/agent-guidelines/verification.md) | Choose checks for the changed behavior, inspect failures and skipped tests, maintain hooks/worktrees, and manage local servers. |
| [Code style](docs/agent-guidelines/code-style.md) | Follow coding conventions, reuse existing owners of rules, preserve behavior during refactoring, and keep types, state, and abstractions clear. |
| [Documentation](docs/agent-guidelines/documentation.md) | Update nearby READMEs with behavior changes, maintain canonical behavior maps, handle generated docs, and write useful comments. |
| [Safety](docs/agent-guidelines/safety.md) | Handle credentials, environment changes, migrations, external effects, and shared resources. |
| [README standard](docs/readme-standard.md) | Write useful subsystem, feature, and small-folder READMEs: ownership, invariants, decisions, verification, and history instead of narrated code. |
| [Weekly sweep document](docs/weekly-sweep.md) | The audit procedure in plain Markdown, usable directly or as the prompt for your own scheduled task. No skill installation required. |

## Scripts and stack setup

Scripts live in `kits/typescript/scripts/`, `kits/python/tools/`, and the small
standalone examples below. They include editable roots, exclusions, and limits.

| Check | TypeScript | Python | Purpose |
| --- | --- | --- | --- |
| Maximum file lines | [check-loc.cjs](kits/typescript/scripts/check-loc.cjs) | [check_max_lines.py](kits/python/tools/check_max_lines.py) | Report oversized files for refactoring review. Configurable limit; `--strict` makes it blocking. |
| README coverage | [check-readme-coverage.cjs](kits/typescript/scripts/check-readme-coverage.cjs) | [check_readme_coverage.py](kits/python/tools/check_readme_coverage.py) | Identify nearby READMEs that may need updates after source changes. Advisory; the agent must review accuracy. |
| Markdown links | [check-links.cjs](kits/typescript/scripts/check-links.cjs) | [check_markdown_links.py](kits/python/tools/check_markdown_links.py) | Detect broken local documentation links. |
| Slow tests | [test-profile.cjs](kits/typescript/scripts/test-profile.cjs) + [test-profile-summary.cjs](kits/typescript/scripts/test-profile-summary.cjs) | `pytest --durations=15` | Show the most expensive tests so agents can investigate setup and runtime costs. |
| Combined checks | [check-local.cjs](kits/typescript/scripts/check-local.cjs) | [check.py](kits/python/tools/check.py) | Run the configured checks and return a failing exit status when a required check fails. |
| Setup diagnosis | [check-doctor.cjs](kits/typescript/scripts/check-doctor.cjs) | `uv sync --locked` for setup; the combined gate verifies tools | Identify missing runtime/tooling prerequisites. Dependency installation is a separate setup step. |
| Check configuration and shared helpers | [harness.config.cjs](kits/typescript/harness.config.cjs) + [scripts/lib/](kits/typescript/scripts/lib/) | [harness.toml](kits/python/harness.toml) + [harness.py](kits/python/tools/harness.py) | Adapt paths and thresholds; copy required helpers with each selected script. |

For complete setup and exact copy dependencies:

- **[TypeScript kit](kits/typescript/README.md):** npm, TypeScript, ESLint, Jest,
  the scripts above, small test fixtures, and optional pre-commit/pre-push hooks.
- **[Python kit](kits/python/README.md):** uv, Ruff, Pyright, pytest, the helpers
  above, small test fixtures, and optional pre-commit/pre-push hooks.
- **[Port inspection](examples/ports/README.md):** a standalone Node + `lsof`
  script to list listeners and suggest a port. It never kills another process.
- **[Documentation portability tools](tools/README.md):** Python standard-library
  checks for local Markdown links and machine-specific paths.

The kits are examples to adapt, not a requirement to replace a working test runner
or package manager. Their tiny source/test fixtures verify wiring, not your app.
There is no required test-suite taxonomy or universal coverage percentage.

## After you approve an adoption plan

1. Copy the selected files, including their required script helpers. Documents,
   the AGENTS template, and either skill can be copied individually.
2. Modify the copied files: add your project's context, commands, source paths,
   exclusions, conventions, and validation requirements. Resolve relevant TODOs.
3. Preserve useful existing instructions and tooling. Add references only to files
   that actually exist in your project; do not leave links to things you did not copy.
   Keep one owner for each adopted rule and make skill/guide wording agree. This
   library keeps skills self-contained for independent copying; you may consolidate
   them into a shared procedure only when all its required files exist in your repo.
   Preserve ownership, data/credential rules, migration and deployment boundaries,
   and the exact prerequisites and cleanup for adopted integration tests.
4. Run the adopted checks and verify a meaningful failure is detected. Test commands
   directly before enabling optional hooks. Leave changes uncommitted for review.

For example, a small content repository may adopt the operating guide and link
checks, while an application may also adopt the ship skill, test helpers, and
integration requirements. A pipeline can add evidence-reuse and artifact-lifecycle
rules to the verification guide. Use the project's real contracts for those
choices; the library supplies no business rules or production configuration.

## Maintain this library

Run `python3 tools/check_library.py` for local Markdown paths and portability.
For script changes, also run that kit's documented checks. Nothing here installs
hooks or schedules, commits, pushes, or deploys automatically.

[MIT license](LICENSE).
