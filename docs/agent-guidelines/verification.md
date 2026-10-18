# Verification

Choose checks from the actual change and its risks. Use focused checks during
iteration, then the adopted full gate for implementation handoff. Add the project's
integration, build, or browser checks when changed boundaries require them.
For documentation-only edits, local-link checks and semantic README review may
be sufficient. Say what was not exercised.

Before concluding there is no changed scope, inventory changes against the
selected base, staged and unstaged changes, and relevant untracked files. An empty
`git diff` alone is insufficient. When that complete inventory is empty, infer no
change-specific reading or checks; explicitly requested audits and adopted ship
gates still apply. Ordinary prose edits need relevant documentation guidance;
instruction changes also need realistic
routing and ownership scenarios. Source, configuration, schema, stylesheet, and
mixed changes retain affected-domain checks and consumer discovery, regardless
of file extension. A helper's suggestions do not replace the adopted ship gate.

## Adopted commands

Commands run from the target project after copying and adapting its kit. In this
library, run non-Git checks from the selected kit directory; Git-root diagnostics
and README change prompts need a copy at an independent project's root.
These are examples only: copy or keep the commands that actually exist in the
target project. This guide requires no other library document. Record the final
commands and prerequisites when adopting it; do not run missing sample commands.

| Purpose | TypeScript kit | Python kit |
| --- | --- | --- |
| Full local gate | `npm run check` | `uv run python tools/check.py` |
| README change prompt | `npm run check:readme` | `uv run python tools/check_readme_coverage.py --staged` |
| Local Markdown links | `npm run check:links` | `uv run python tools/check_markdown_links.py` |
| File-size review | `npm run check:loc` | `uv run python tools/check_max_lines.py` |
| Slow-test evidence | `npm run test:profile`, then `npm run test:slow` | `uv run pytest --durations=15` |
| Readiness | `npm run doctor` | `uv sync --locked` installs the pinned environment; the gate checks tool availability |

The Python kit documents `--frozen --offline` validation after initial setup.
Dependency installation is setup, not a read-only audit step.

Treat file-size and README heuristics as review prompts unless the adopted policy
explicitly makes them blocking. A passing prompt does not prove documentation
accuracy or architectural quality. A full test pass only supports the scenarios
that actually ran; inspect skips and empty discovery. Do not use a green formatter
or typecheck result as evidence that runtime behavior works.

<!-- TODO: Add the project's build, integration, and browser commands here, with
prerequisites and the conditions that make each required. -->

## Bootstrap and hooks

Verify runtime versions, lockfile, installed tools, and configured prerequisites
before interpreting failures. Use the existing package manager. Do not share
mutable generated dependencies across worktrees when generation can overwrite
another checkout's artifacts; use independent environments instead.

Hooks are optional adoption examples, not automatically installed by this guide.
Preserve existing hooks. If adopted, verify tracked hooks and generated shims in
each checkout: a shared hooks-path setting does not guarantee local shims exist.
Do not bypass hooks or assume they ran because a Git command succeeded.

## Test quality and speed

Prefer distinct behavioral regressions: state, permission, persistence, recovery,
concurrency, and failure handling. Avoid tests that simply mirror an implementation
or assert styling details unrelated to the requested behavior. A new test file is
not itself evidence of better coverage.

Use the top-slow-test report to choose optimization targets. Distinguish expensive
fixture setup from test-body cost; compare like-for-like runtime and cache states.
Replace unnecessary long delays, repeated scans, and redundant integration mounts
while preserving meaningful contracts. Do not remove assertions merely for speed.
Scan source once when several assertions use the same repository snapshot.

If a focused selection finds no tests for changed executable code, choose relevant
behavioral coverage explicitly or report the gap. When coverage is measured, keep
the same source denominator before and after a change, including unimported files.

## Server lifecycle

Before starting a server, inspect listeners using the project's helper or system
tooling. Record the checkout, URL, process/session handle, and actual bound port.
An unused port is a snapshot, not a reservation; confirm bind and readiness.
Never infer ownership from a port number alone.

Use independent build/output directories or worktrees for simultaneous servers.
If a server repeatedly restarts, inspect logs before repeated browser refreshes.
Do not delete another process's lock or kill an unidentified listener to recover.

Stop owned servers after checks, on failures, and before handoff unless a running
preview was requested. Use the retained session or verified process handle, wait
for exit, and check the listener is gone. Report remaining owned resources and
stop instructions. After interruption, reconcile ownership before launching more.

## Adopted formal checks

When a change affects a modeled contract, inspect its transition-to-code mapping
and run the formal checks required by the project's policy. Check both the model
and the linked implementation tests. Treat negative controls and reachability
witnesses as distinct expected counterexamples; verify the exact invariant and
checker outcome. Do not count a timeout, skipped suite, or incomplete exploration
as evidence. Record bounds, assumptions, input identities, and coverage limits.

Formal verification is optional until adopted. Keep it separate from ordinary
kit checks and do not create automatic hooks or require a new runtime for unrelated
work. A passing model cannot replace implementation tests or the final ship gate.

## Evidence and failures

Record the command, checkout, exit outcome, and relevant report or failure excerpt.
Separate FAIL from BLOCKED prerequisites and from optional checks not configured.
Continue independent work, but never turn an unavailable check into a pass.
Fix in-scope failures and rerun affected checks; broaden or repeat passing checks
only for new changes, demonstrated risk, or an explicit requirement. Preserve
original failures when diagnostic reruns add evidence.

For expensive derived-data or artifact computation, identify the changed inputs,
rules, runtime, scope, and downstream consumers before executing. Reuse evidence
only under the project's compatibility/provenance contract and distinguish new
execution, reused evidence, and unverified scope. Retain completed evidence across
interruptions. Missing evidence is a gap to resolve, not permission to launch a
production rebuild. This does not waive required code checks or the final gate;
local test fixtures and production recomputation have different effects.
