# Agent Operating Guide

## Core Principles

- Lead with the result and next action. Include caveats when they change a decision,
  explain a blocker, or bound a material claim.
- Use checks that resolve a concrete uncertainty or satisfy an adopted gate. Once
  these pass, proceed; add validation for changed behavior, new evidence, or a
  specific unresolved risk.
- Inspect the relevant implementation and nearby documentation before changing
  complex behavior.
- Continue within the authorized scope until the requested outcome is complete.
  Resolve routine choices from repository evidence; ask only when missing input
  materially affects correctness or authorization. User instructions take
  precedence over repository and skill guidelines.
- Preserve unrelated work, respect the requested scope, and follow established
  project conventions.
- Protect user data and project state. Obtain approval before destructive or
  difficult-to-recover actions.
- Keep implementation, tests, and documentation aligned with behavior changes.
- Use an ASD-STE100-inspired style for documentation, comments, and docstrings.
  Write short, direct sentences and use consistent terms. Preserve conditions,
  exceptions, identifiers, commands, and tool directives.
- Preserve useful invariants, examples, failure/recovery rules, and decision
  history. Remove repetition without dropping conditions that make a rule safe.
- Use code, schemas, and tests to establish actual behavior when prose disagrees;
  distinguish what the system does from what it should do.
- Verify work in proportion to its risk. Never weaken checks to obtain a pass;
  report checks that were skipped or unavailable.
- Make investigations visible: state the question, evidence, and uncertainty.
  Distinguish measured results from planned or expected results.
- Leave changes unstaged and uncommitted unless authorized. Push or publish only
  with task authorization.

## Project Reference Map

Use `docs/agent-guidelines/README.md`, when adopted, to find guidance for the task.
Read selected guides and the closest area instructions and README. Do not load
the entire catalog. Project constraints and adopted workflow gates still apply.

<!-- TODO: Only after explicit approval to create or adapt AGENTS.md, keep
pointers to adopted or existing files and adjust their paths. Add essential
project context, ownership boundaries, actual check commands, and approval constraints; keep detailed procedures in focused
guides. Preserve the project's existing safeguards rather than replacing them
with this template's generic defaults. -->
