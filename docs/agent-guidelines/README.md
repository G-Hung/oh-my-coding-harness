# Agent guidelines

Detailed instructions to copy individually and adapt to your project. Each
general guide includes its own procedure. The modular skills have explicit
[copy dependencies](../adoption.md#skill-bundles-to-copy).

| Reference | Read when |
| --- | --- |
| [Ship procedure](ship-cycle.md) | Implementing approved work through the modular ship-cycle skill |
| [Model selection](model-selection.md) | Confirming or applying execution and reviewer policy |
| [Workflow](workflow.md) | Starting work, reviewing, or handing off changes |
| [Verification](verification.md) | Selecting checks, profiling tests, or running a local server |
| [Documentation](documentation.md) | Behavior, interfaces, ownership, or editing guidance changes; ASD-STE100-inspired prose |
| [Code style](code-style.md) | Implementing or refactoring code |
| [Safety](safety.md) | Work touches data, credentials, migrations, or external effects |
| [Formal verification](formal-verification.md) | A change affects an adopted modeled protocol, or bounded model checking may address a concrete risk |

Use [code sweep](../code-sweep.md) for findings-only maintenance. Use the
[README standard](../readme-standard.md) for useful subsystem documentation.

## Adoption

After approval, copy selected documents or sections, then add your project's
commands, conventions, and constraints. Keep only applicable guidance. Do not add a reference map to an existing AGENTS.md without explicit approval
for that targeted addition. Link only to files that exist. The
[ship-cycle skill](../../.agents/skills/ship-cycle/SKILL.md) uses the
[shared procedure](ship-cycle.md), [model selection](model-selection.md), and
[model policy](../../.agents/model-policy.toml).
