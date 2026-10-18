---
name: ship-cycle
description: Execute approved changes through adaptive execution roles, independent review, and verified local handoff.
---

# Ship cycle

For approved implementation, follow the [ship procedure](../../../docs/agent-guidelines/ship-cycle.md).
Planning and findings-only requests do not authorize implementation.
Read [model selection](../../../docs/agent-guidelines/model-selection.md) and the
[model policy](../../model-policy.toml) before assigning work. The supplied Codex
policy is a reference, not permission to choose the user's models.

Use `execution.standard` for everyday bounded implementation, debugging, tests,
and documentation. Use `execution.routine` for repetitive, well-specified work
with cheap verification. Reserve `execution.difficult` for consequential
uncertainty, hard architecture, or unresolved failures whose repair cost warrants
it. Choose directly; there is no mandatory escalation ladder. Respect a fixed-role
policy even when another role looks attractive. The main agent can work directly.
Execution choices never change the independent reviewer.

## Copy dependencies

Copy this folder together with `.agents/model-policy.toml`,
`docs/agent-guidelines/model-selection.md`, and
`docs/agent-guidelines/ship-cycle.md`, preserving relative paths. If relocating
files, update their links. Inspect existing destination files and merge approved
changes instead of overwriting them. Follow the library's adoption guide before
integrating; do not copy its root AGENTS.md.
