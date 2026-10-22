# Verification

Choose checks from the actual change and its risks. Use focused checks during
iteration, then the adopted full gate for implementation handoff. Add the project's
integration, build, or browser checks when changed boundaries require them.
For documentation-only edits, local-link checks and semantic README review may
be sufficient. Say what was not exercised.

Once the relevant checks and adopted gates pass, proceed to handoff. Repeat or
expand validation when behavior changes, new evidence appears, or a specific
unresolved risk remains. A simpler design may remove the need for another check.

Start with three actions:

1. Inventory the change against the comparison base, including staged, unstaged,
   and relevant untracked files.
2. Choose checks for the affected behavior and consumers. Prose needs link and
   accuracy review; agent instructions also need realistic usage scenarios.
3. Run the project's adopted gates and report what they actually exercised.
   With no changes, only explicitly requested audits and adopted gates apply.

## Select the evidence

Choose the smallest useful check for the failure mechanism, then satisfy all
adopted gates. A simpler design or stronger representation may prevent a problem
better than another check. This table does not require new tools or installations.

| Technique | Use for |
| --- | --- |
| Lint / static rules | Detectable mistakes, forbidden imports, structural conventions |
| Types / schemas | Invalid representations, interface mismatches, external input shape |
| Unit tests | Local rules and boundary cases |
| Integration / contract tests | Storage, serialization, adapters, component agreements |
| End-to-end tests | Critical workflows through assembled components |
| Build / package checks | Compilation, generated artifacts, distribution assembly |
| Property / differential tests | Broad invariants or comparison with an independent baseline |
| Fault / concurrency tests | Interrupted work, retries, partial writes, races |
| Profiling / benchmarks | Measured resource or performance problems under comparable workloads |
| Model checking / formal methods | Consequential state transitions and ordering invariants |

Match claims to the boundary exercised: static types need runtime validation at
external inputs; integration tests need representative dependencies; formal
results apply to the modeled assumptions and bounds. Inspect skips and empty
discovery before reporting a pass.

For a prose edit, check links and meaning, then finish the adopted gate. For a
checker behavior change, test its success and representative failure paths.
Investigate an unchanged checker when there is evidence of a defect or coverage
gap; do not add a second validation layer merely to reassure yourself.

For test-design examples, use the optional [testing guide](testing.md). For
modeled protocols, use [formal verification](formal-verification.md) if adopted.
This guide retains the execution and evidence rules needed on its own.

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
| Local Markdown links | `npm run check:links` | `uv run python tools/check_markdown_commonmark_links.py` |
| File-size review | `npm run check:loc` | `uv run python tools/check_max_lines.py` |
| Slow-test evidence | `npm run test:profile`, then `npm run test:slow` | `uv run pytest --durations=15` |
| Readiness | `npm run doctor` | `uv sync --locked` installs the pinned environment; the gate checks tool availability |

The Python kit documents `--frozen --offline` validation after initial setup.
Dependency installation is setup, not a read-only audit step.

Treat file-size and README heuristics as review prompts unless the adopted policy
makes them blocking. Review the affected design and documentation directly.

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

Check observable behavior, not a copy of the implementation. Select distinct
regressions for affected contracts and failure paths. If a selection finds no
tests for changed executable code, select meaningful coverage or report the gap.
Profile slow tests before optimizing; preserve assertions and compare equivalent
environments. Detailed test design and examples belong in the optional testing
guide; these minimum rules also apply when it has not been copied.

For parallel branches or worktrees, the optional [Git overlap check](../../examples/git-checks/README.md)
and [port helper](../../examples/ports/README.md) can reveal integration or listener
conflicts. Use existing project tools when they already solve the problem.
When a remote check reports a merge conflict, inspect both changes' intent,
repair the task branch, run affected checks, and recheck remote compatibility.
Same-file overlap alone needs no repair. Merging an unfinished peer PR is not
the default fix; ask when resolution requires a decision beyond the task's scope.

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

Before expensive computation, identify what changed and which result needs to be
refreshed. Reuse existing results when their inputs and assumptions still apply,
and distinguish reused results from new runs. Operations on shared environments
must stay within task authorization.
