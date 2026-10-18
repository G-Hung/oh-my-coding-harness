# oh-my-coding-harness

Tools and workflows from [I Just Want My Coding Agent to Leave Me Alone](docs/articles/coding-agent-harness.md).
Plan the work with your agent, let it implement, check, review, and fix the result,
then use regular code sweeps to find problems that accumulate across changes.

This is a library to adapt, not an installer or a replacement for your project's
working tools. The skills and model settings started in Codex. Use them as a
reference; your agent should inspect your environment and confirm the choices
with you before adopting them.

## Start with your agent

Share this repository URL in Plan Mode, or paste:

```text
Read the README and docs/adoption.md in this repository.
Inspect my project's instructions, stack, checks, hooks, and agent environment.
Read the complete relevant assets and assess what to add, adapt, keep, or skip.
Explain dependencies and propose model roles, reasoning settings, reviewer,
and fallback choices based on my available tools and preferences. Confirm those
choices with me; the Codex configuration is a reference, not my default.
Present one adoption plan before integrating anything. After approval, copy
selected new assets and their dependencies first, then adapt them; merge approved
changes into existing files. Do not recreate a shortened version from memory.
Treat AGENTS.md as reference only. General adoption approval does not authorize
editing it; suggest specific lessons separately for my explicit selection.
Leave changes uncommitted. Do not install hooks, schedule, push, or publish
unless those actions are explicitly authorized.
```

Agents: follow the [adoption guide](docs/adoption.md), including when the user only
provides the repo link. Inspect first, agree on the selection and settings, then
copy and adapt. The library's root AGENTS.md is for maintaining this library;
it is not a file to copy into the user's project.

## What is here

| Asset | Use it for |
| --- | --- |
| [ship-cycle](.agents/skills/ship-cycle/SKILL.md) | Approved implementation, integration, required checks, one independent review/fix loop, and local handoff. |
| [code-sweep](.agents/skills/code-sweep/SKILL.md) | A findings-only audit of recent work and affected areas, dependencies, tests, architecture, and documentation. No automatic fixes or schedule. |
| [Model policy](.agents/model-policy.toml) | Configurable execution roles and a separate reviewer. Confirm models, reasoning, fixed/adaptive execution, and fallbacks with the user. |
| [Guidelines](docs/agent-guidelines/README.md) and [README standard](docs/readme-standard.md) | Working principles, verification, safety, and useful documentation. The [AGENTS template](templates/README.md) is for comparison and optional lessons. |
| [TypeScript](kits/typescript/README.md) and [Python](kits/python/README.md) kits | Runnable local checks, configuration, tests, and optional hook examples. Keep the target's existing stack when it already works. |
| [Standalone tools and advanced examples](docs/assets.md) | Git conflicts/overlaps, npm audits, Python import boundaries, changed-path check selection, ports, documentation checks, and bounded formal verification. |

Read the [asset catalog](docs/assets.md) for individual scripts, prerequisites,
limitations, and hook details. File-size and README prompts are signals for review;
a passing check only supports the behavior it actually exercises.

## Use the adopted workflows

Copy each skill with its [required dependencies](docs/adoption.md#skill-bundles-to-copy).
The skill selects roles, the procedure defines the workflow, and the model policy
holds the confirmed settings. Updating that policy changes subsequent assignments;
it does not switch a running agent's model.

After agreeing on a task, switch to execution mode and explicitly invoke:

```text
$ship-cycle execute
```

For an audit:

```text
$code-sweep
```

Review its findings and choose work to send through the next ship cycle. The
skills do not authorize commits, pushes, publication, or schedules by themselves.
See [Codex adoption notes](adapters/codex/README.md) for layout and invocation.

## Maintain this library

This repo uses its own checks. After the explicit [local setup](docs/maintenance.md),
tracked Git hooks run fast static checks on the staged snapshot, validate commit
subjects such as `feat(hooks): add checks`, and run the full gate on proposed pushed
commits. A failure returns the command and error to the agent: fix, rerun, stage,
and retry. Hooks never fix or stage files on your behalf.

Run `uv run --frozen --offline --no-sync python tools/check.py` for the full gate,
or add `--static-only` for the pre-commit checks. See the
[maintenance guide](docs/maintenance.md) for setup, check coverage, examples of
rejected changes, and how the scripts fit together. Other projects should adopt
only the checks and hook integration approved for their environment.

Hooks are local and bypassable. Use the same commands in CI for shared enforcement.
Cloning does not activate hooks, and installing them does not authorize a push.

[MIT license](LICENSE).
