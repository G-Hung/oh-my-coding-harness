# oh-my-coding-harness

Tools and workflows from [I Just Want My Coding Agent to Leave Me Alone](docs/articles/coding-agent-harness.md).
Plan the work with your agent, let it implement, check, review, and fix the result,
then use regular code sweeps to find problems that accumulate across changes.

These are working examples of the article's ideas. Understand the problems they
solve, compare your project's approach, and reuse or adapt what helps. Rust,
Swift, or Go projects can connect their own formatting, static checks, and tests
to the same feedback loop without importing a Python or TypeScript kit.

## Start with your agent

Share this repository URL in Plan Mode, or paste:

```text
Read https://github.com/G-Hung/oh-my-coding-harness.
Inspect this library and my project. Recommend useful workflows, guides, and
checks to adopt or adapt, while preserving what already works. Follow the
adoption guide and present one grouped plan before making changes. Leave the
result uncommitted for review.
```

Agents: follow the [adoption guide](docs/adoption.md), even for a repo-link-only
request. The library's root AGENTS.md governs its maintenance, not the target.

## Start with the problem

| Problem | Minimum practice | Optional examples |
| --- | --- | --- |
| Checks get forgotten | Give the agent one check command and its failure output. | [TypeScript](kits/typescript/README.md) and [Python](kits/python/README.md) kits |
| Design decisions get lost | Keep useful rationale near the code. | [README standard](docs/readme-standard.md) |
| Implementation misses defects | Use an independent reviewer through repairs and explicit approval. | [ship-cycle](.agents/skills/ship-cycle/SKILL.md) |
| Problems accumulate across changes | Periodically review recent code and recurring failures, then select fixes. | [code-sweep](.agents/skills/code-sweep/SKILL.md) |
| Engineering guidance is hard to find | Keep focused notes and read them when relevant. | [Guidelines](docs/agent-guidelines/README.md), [AGENTS template](templates/README.md) |
| Integration or resource conflicts escape local tests | Check affected boundaries with existing project tools. | [Standalone tools and advanced examples](docs/assets.md) |

[Model preferences](.agents/model-policy.toml) are optional when host defaults
are not enough. Adopt the practice using your existing tools before adding assets.

Read the [asset catalog](docs/assets.md) for individual scripts, prerequisites,
limitations, and hook details. File-size and README prompts are signals for review;
a passing check only supports the behavior it actually exercises.

## Use the adopted workflows

Copy each selected skill using the [installation guide](docs/adoption.md#skill-bundles-to-copy).
Each skill contains its workflow and uses the host's existing settings by default.
Optional project preferences can name models; they do not configure the host.

After agreeing on a task, use your host's skill invocation. In Codex, switch to
execution mode and invoke:

```text
$ship-cycle execute
```

For an audit:

```text
$code-sweep
```

Review its findings and choose work to send through the next ship cycle. The
ship-cycle commits reviewed task changes before handoff unless you explicitly
request an uncommitted result. Code-sweep remains read-only. Pushes, publication,
and schedules require task authorization.
See [Codex adoption notes](adapters/codex/README.md) for layout and invocation.

## Maintain this library

This repo uses its own checks. After the explicit [local setup](docs/maintenance.md),
tracked Git hooks run fast static checks on the staged snapshot, validate commit
subjects such as `feat(hooks): add checks`, and run the full gate on proposed pushed
commits. Before branch pushes, pre-push also checks merge compatibility with the
remote's current default branch and, on GitHub, other open PRs targeting it.
Same-file overlaps are informational; merge conflicts block the push. Checks use
a temporary repository. A failure returns the
command and error to the agent: fix, rerun, stage,
and retry. Hooks never fix or stage files on your behalf.

Run `uv run --frozen --offline --no-sync python tools/check.py` for the full gate,
or add `--static-only` for the pre-commit checks. See the
[maintenance guide](docs/maintenance.md) for setup, check coverage, examples of
rejected changes, and how the scripts fit together. Other projects should adopt
only the checks and hook integration approved for their environment.

Hooks are local and bypassable. Use the same commands in CI for shared enforcement.
Cloning does not activate hooks, and installing them does not authorize a push.

[MIT license](LICENSE).
