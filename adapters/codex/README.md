# Codex adoption notes

Both entrypoints live at the repository root:
[ship-cycle](../../.agents/skills/ship-cycle/SKILL.md) and
[code-sweep](../../.agents/skills/code-sweep/SKILL.md).
Copy the full [dependency bundles](../../docs/adoption.md#skill-bundles-to-copy),
not just the skill folders. They share the model policy and model-selection guide.

Inspect your Codex environment, supported model and reasoning settings, and
existing project instructions. Confirm preferences and role assignments through
the adoption plan. The supplied policy is reference-only until approved; do not
silently use its models or replace an existing policy.

After adoption, agree on a task, switch from planning to execution mode, and send
`$ship-cycle execute`. Explicit invocation identifies the desired workflow;
UI button behavior depends on the host and its instructions. Use `$code-sweep`
for a findings-only audit, then choose any implementation work separately.

For another product, adapt the skill location, policy format, and supported
settings during adoption. These assets install no plugins, hooks, or schedules.
