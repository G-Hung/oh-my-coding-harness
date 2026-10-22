# Agent guidelines

Detailed instructions to copy individually and adapt to your project. Each
general guide includes its own procedure. The modular skills have their own
[installation guidance](../adoption.md#skill-bundles-to-copy).

Select guidance from the task, nearby code, and project instructions. Read only
relevant guides; do not load every row or follow every source link. These are
decision aids, not a requirement to add patterns or tools. Keep essential project
constraints in AGENTS.md and detailed guidance here.

| Reference | Read when |
| --- | --- |
| [Workflow](workflow.md) | Starting work, reviewing, or handing off changes |
| [Verification](verification.md) | Selecting checks, profiling tests, or running a local server |
| [Documentation](documentation.md) | Behavior, interfaces, ownership, or editing guidance changes; ASD-STE100-inspired prose |
| [Code style](code-style.md) | Implementing or refactoring code |
| [Design and reuse](design-and-reuse.md) | DRY, constants, ownership, abstraction, cohesion, refactoring |
| [Contracts and naming](contracts-and-naming.md) | Interfaces, units, validation, compatibility, state meanings |
| [Composition and patterns](composition-and-patterns.md) | Dependency injection, strategy, factory, registry, adapter |
| [State and recovery](state-and-recovery.md) | Mutation, cache invalidation, concurrency, retries, idempotency |
| [Debugging](debugging.md) | Reproduction, competing hypotheses, repeated ineffective repairs |
| [Testing](testing.md) | Test boundaries, partitions, assertions, fixtures, regression sensitivity |
| [Safety](safety.md) | Work touches data, credentials, migrations, or external effects |
| [Formal verification](formal-verification.md) | A change affects an adopted modeled protocol, or bounded model checking may address a concrete risk |

Use [ship-cycle](../../.agents/skills/ship-cycle/SKILL.md) for approved implementation
and [code-sweep](../../.agents/skills/code-sweep/SKILL.md) for a read-only review.
Use the
[README standard](../readme-standard.md) for useful subsystem documentation.

Extend the cluster that owns a concern. Add a new guide only for a distinct task.
Use short rules, reasons, and examples; preserve conditions that make advice safe.
Keep general guides self-contained.

## Adoption

After approval, copy selected documents or sections, then add your project's
commands, conventions, and constraints. Keep only applicable guidance. Do not add a reference map to an existing AGENTS.md without explicit approval
for that targeted addition. Link only to files that exist. Each skill contains
its workflow; model preferences and engineering guides are optional.

When copying this index, retain only links to adopted or existing guides and
workflow assets. Copying an index does not require adopting its entire catalog.
