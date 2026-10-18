# Working on this library

## First principles

- Understand the behavior before editing its code or instructions. Inspect callers,
  tests, and copy requirements; preserve useful existing implementations.
- Complete the authorized scope, preserve unrelated work, and resolve routine
  choices from evidence. User instructions take precedence over these guidelines.
- Write instructions that change agent decisions. Keep principles clear and put
  detailed procedures in focused guides without weakening required gates.
- Use an ASD-STE100-inspired style for documentation, comments, and docstrings.
  Write short, direct sentences and use consistent terms. State conditions and
  actions explicitly. Preserve technical meaning, identifiers, and tool directives.
- Preserve useful conditions, examples, invariants, recovery steps, and decision
  history. Shorter text is not a quality target; remove duplication or stale
  guidance only after checking what depends on it.
- Fix causes, keep failures visible, and verify claims. Never weaken a check to
  obtain a pass; report unavailable validation explicitly.

## Library requirements

- Keep examples project-neutral: no private names, paths, credentials, business
  rules, or source provenance.
- Keep skill bundles copyable with their documented procedures and policy.
  Reference maps are optional; an adopted bundle must have no missing dependencies.
- Keep kits runnable after copying. Document required helpers, dependencies,
  working defaults, and checks; mark project choices with explanatory TODOs.
- Preserve existing tooling during adoption. The README must support selecting
  files and proposing changes and risks before asking permission to integrate.
- Leave work unstaged and uncommitted. Do not push, publish, or install hooks
  unless explicitly authorized.

## Focused guidance and checks

- `templates/AGENTS.md`: reference principles, not a default installation asset.
  Existing target AGENTS.md files require explicit approval for targeted additions.
- `docs/agent-guidelines/`: detailed behavior templates; edit the relevant guide
  when a procedure changes. These are library content, not automatically active
  requirements for every maintenance task.
- `docs/readme-standard.md`: README content and organization.
- `docs/agent-guidelines/documentation.md`: the practical ASD-STE100 adaptation.
- Before implementation, read `docs/maintenance.md`. This checkout uses tracked
  hooks after explicit setup; do not assume cloning activated them.
- Run `uv run --frozen --offline --no-sync python tools/check.py --static-only`
  during iteration and the full command without `--static-only` before handoff.
  Pre-commit checks staged content, commit-msg requires a Conventional Commit
  prefix (optional scope), and pre-push checks proposed committed objects.
- Fix reported failures and rerun the relevant command, then stage the fixes and
  retry. Never bypass a hook, weaken a gate, or silently auto-stage repairs.
- Use logical commits when authorized. Preserve other projects' hook managers and
  AGENTS.md during adoption; this repo's active setup is not permission to change theirs.
