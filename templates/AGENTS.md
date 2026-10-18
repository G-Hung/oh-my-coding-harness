# Agent Operating Guide

## Core Principles

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

Load only guidance relevant to the task. These paths are relative to the project
root; use them when present, along with the closest area instructions and README.

- `docs/agent-guidelines/workflow.md`: planning, ownership, review, and handoff.
- `docs/agent-guidelines/code-style.md`: implementation, reuse, and refactoring.
- `docs/agent-guidelines/verification.md`: checks, test quality, and local resources.
- `docs/agent-guidelines/documentation.md`: behavior and README maintenance.
- `docs/agent-guidelines/safety.md`: data, credentials, migrations, and external effects.
- `docs/agent-guidelines/formal-verification.md`: bounded models and implementation conformance, when adopted.
- `docs/readme-standard.md`: what a useful subsystem README should contain.

<!-- TODO: Only after explicit approval to create or adapt AGENTS.md, keep
pointers to adopted or existing files and adjust their paths. Add essential
project context, ownership boundaries, actual check commands, and approval constraints; keep detailed procedures in focused
guides. Preserve the project's existing safeguards rather than replacing them
with this template's generic defaults. -->
