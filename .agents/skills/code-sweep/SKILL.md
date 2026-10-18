---
name: code-sweep
description: Audit recent changes, active areas, dependencies, tests, and documentation; return evidence and proposed fixes without implementing them.
---

# Code sweep

Follow the [code-sweep procedure](../../../docs/code-sweep.md). Default to the
last 14 days unless the user chooses another window. This skill does not create
a schedule or authorize fixes. Bring selected findings back to planning; approved
implementation can then use ship-cycle.

Before delegating, read [model selection](../../../docs/agent-guidelines/model-selection.md)
and the [model policy](../../model-policy.toml). Use `execution.standard` for
bounded investigations, `execution.routine` for repetitive checks with clear
verification, and `execution.difficult` for consequential uncertainty or difficult
cross-module failure analysis. Respect allowed roles, fixed-role preferences,
and approved fallback choices for all descendants. This audit does not start the
ship-cycle acceptance reviewer; the main agent integrates and evaluates findings.

## Copy dependencies

Copy this folder with `.agents/model-policy.toml`,
`docs/agent-guidelines/model-selection.md`, and `docs/code-sweep.md`.
Preserve relative paths or update links when relocating files. Share the policy
and model-selection guide if adopting both skills. Inspect existing destination
files and merge approved changes rather than overwriting them. Do not copy the
library's root AGENTS.md.
