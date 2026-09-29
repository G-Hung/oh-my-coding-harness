# Weekly code sweep

Review code changed in the last 1–2 weeks and the paths it affects. Find concrete
improvements that make the system robust and easier for future AI agents to
understand, change, and verify. Start with security, then examine correctness,
architecture, costly tests, and README maintenance.

## Scope

Use the requested review window, defaulting to the last 14 days. Read existing
project instructions and inspect recent commits, diffs, and current uncommitted
changes. Record the window and checkout state; distinguish uncommitted work from
committed changes. Briefly scan all active product areas using the ownership map,
entry points, and existing evidence. Investigate the recent changes, affected
callers/contracts, test failures, and concrete risks deeply. A broad scan is not
exhaustive coverage of every area against every dimension; record what received
depth and why without turning the sweep into a whole-repository rewrite proposal.

This is an audit: run non-mutating checks and propose fixes. Do not change source,
documentation, dependencies, or Git state unless the user has authorized that work.
Use the existing toolchain and safe test environment; record blockers and continue
independent checks. Never expose secret values or substitute live credentials for
isolated tests.

<!-- TODO: Add the project's security and validation commands and any required
integration-test prerequisites after copying. -->

## Delegation and integration-test ownership

Delegate useful independent read-only investigations under the adopted model
policy; reuse agents and existing evidence rather than duplicating searches.
Give each an explicit question, area, and evidence expectations. One owner manages
the integration/E2E run, its processes, containers, ports, databases, and artifacts;
other auditors must not launch a competing harness or modify its fixtures.

When the project requires a full integration/E2E run, preserve its full serial
scope and actual compiled/runtime defaults. Do not substitute selected smoke tests
for that requirement. Use the configured isolated environment, disposable data,
synthetic providers, and separate outputs where supported. Record prerequisites
and command outcomes. Do not automatically retry failures unless the adopted
policy explicitly requires it; retain the first failure's logs, traces, screenshots,
or other available artifacts separately from diagnostic reruns. Follow the project's
authorization rules for builds and external effects. Missing isolation never
authorizes live credentials or changes to shared data.

If the harness is blocked, continue independent code, dependency, and documentation
auditing. Report which test scenarios remain unverified. Stop only owned resources
using retained handles, verify shutdown, and preserve the failure evidence. This
skill starts no schedule and does not modify an existing automation's settings.

## Security and basic checks

Run configured security, dependency, lint, type, and relevant test checks. Inspect
changed trust boundaries, authorization, and sensitive-data handling. Distinguish
confirmed vulnerabilities from outdated packages; verify upgrade recommendations
against current advisories and compatibility requirements.

Record PASS, FAIL, or BLOCKED with commands and evidence. Identify unconfigured
checks and skipped or empty tests; a green exit alone does not establish coverage.
Preserve failure evidence and clean up resources started for the audit.

## Correctness and architecture

Trace recent changes through their failure and recovery paths. Look for silent
failures, stale state, races, partial writes, retry duplication, and broken contracts.
Check whether meaningful tests would catch those failures.

Review repeated patterns, duplicated rules, oversized responsibilities, unclear
ownership, and dependencies crossing established boundaries. Recommend abstraction
or consolidation when it removes a demonstrated source of inconsistency or makes
future changes safer. Preserve distinct behavior; similarity alone is insufficient.
Prefer improvements to shared contracts, diagnostics, or checks that prevent a
mistake recurring over isolated cosmetic cleanup.

## Performance and slow tests

Inspect the highest-cost tests from available timing reports and performance risks
in affected code, such as repeated I/O, unbounded work, or resource leaks. Recommend
focused measurement where evidence is missing. Treat a single slow sample as a lead,
not a regression; avoid universal timing budgets or a prescribed test architecture.

## README consolidation and updates

Compare relevant READMEs with current code and commands. Propose specific updates
for stale setup steps, changed contracts, unclear ownership, and missing validation
or recovery instructions. Consolidate overlapping or contradictory guidance into
a clear home, preserving context needed by agents working in each area. Identify
which files and sections to merge, shorten, or remove, and any links that must change.
Preserve useful conditions, examples, recovery procedures, and decision history;
verify that moved detail remains reachable and no invariant disappears in a summary.
Keep READMEs useful for decisions and navigation rather than narrating implementation.

## Report

Return a concise, prioritized report: window and checkout, areas broadly scanned,
deeper investigations and reasons, check results and blockers, then findings with
file/line evidence, consequences, the smallest useful fix, and how to verify it.
Report dependency/security results and README findings separately; neither proves
the other's health. Separate confirmed problems from hypotheses and optional
improvements. Include README proposals, resource cleanup, uninvestigated areas and
other limitations, or state when no actionable issues were found. Leave implementation
ready for approval unless already authorized. Do not imply full coverage from a scan.
