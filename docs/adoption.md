# Adopt the harness

Start here when a user shares the repository URL, including in Plan Mode. Read
the [article](articles/coding-agent-harness.md) for motivation, then assess the
assets against the target environment. A URL or planning request is not permission
to install. You may inspect or obtain a reference checkout without integrating it
into the target project. Do not work around private-repository access restrictions.

### Inspect the target project

Read the existing `AGENTS.md` and applicable area instructions before proposing
changes. Inspect the code, architecture, languages, package manager, test runners,
package scripts, CI, and hook setup. For a new project, use its planned stack and
requirements. Ask about missing context only when it changes the recommendation.

### Assess the assets item by item

Use the [asset catalog](assets.md) and skill bundles below as the inventory. Read the source instructions
and relevant kit README before recommending an item. Start with `ship-cycle`,
`code-sweep`, agent guidelines, the README standard, test gates, and hooks.
Then assess the remaining scripts, helpers, and examples, including port inspection,
Git conflict checks, dependency audits, import boundaries, changed-path check
selection, formal verification, and documentation portability tools. Do not stop after picking
a few easy scripts or limit the result to a fixed number of recommendations.

Address each listed skill, guide, and tool, including items you recommend skipping.
Treat required helpers as part of their parent item and state which files they
include. For equivalent TypeScript and Python implementations, select the version
that fits the project; explain why the other is unnecessary or why both are useful.
A project using another language may still benefit from the guides and workflows
without adopting either stack kit.

Give each recommendation a stable item ID and show:

| Field | What the user should be able to judge |
| --- | --- |
| Asset and existing equivalent | Link the library files and identify what the project already uses. |
| Decision | Add, adapt, keep the existing approach, or skip. |
| Project-specific reason | Explain the benefit or mismatch for its language, architecture, risks, and current tools. |
| Proposed changes | Name destination files, required helpers, configuration changes, and conflicts to resolve. |
| Verification | Name actual commands or review steps and any prerequisites. |

Preserve working tools. Do not replace a package manager, test runner, package
scripts, hooks, or established project rules merely to match the kit. Recommend
only the additions that solve a relevant problem. Hook activation, dependency
installation, and model-policy changes must be visible in the proposed item,
not hidden consequences of copying files.

### Approve the plan once, then carry it out

Present the recommendations together and request explicit approval before editing,
copying, installing dependencies, or enabling hooks. The user can approve the whole
plan or a selected group of items in one reply. Do not ask a separate question for
each item. Leave unapproved or deferred items unchanged. Approval covers the listed
helpers and implementation steps; complete them without asking the same question
again.
If a new conflict requires a material change to the approved scope, explain it and
request approval for that change.

## Confirm models and preferences

The supplied [model policy](../.agents/model-policy.toml) is a Codex reference.
Read [model selection](agent-guidelines/model-selection.md). Inspect actual model
access, supported reasoning and delegation settings, and existing user preferences.
Propose the execution roles, reviewer, adaptive or fixed execution, and permitted
fallbacks. Explain quality, speed, and total task cost, including coordination and
repairs, without promising savings from model names. Roles may share a model.
Keep the human-selected main agent. Ask about unknown preferences and confirm the
configuration with the user in the adoption plan; do not silently adopt ours.

For another product, propose a supported format and explain any missing capability.
If the product cannot provide independent review, agree on a review arrangement
before adopting ship-cycle. Approval of selected tools alone does not approve an
unspecified model policy. After confirmation, record the actual choices and change
`adoption.status` to `approved`; future changes outside those choices need approval.

## AGENTS.md is a reference exception

Read existing target instructions. Compare the [template](../templates/AGENTS.md)
for useful lessons, but exclude AGENTS.md from the default copy and edit list.
General adoption approval does not authorize changing it. Offer concrete optional
additions with reasons; apply one only if the user explicitly selects that targeted
addition. Preserve all other text. Never replace the file or insert a reference map
just because skills were adopted. If absent, offer creation as a separate explicit
choice; do not create it automatically. The library's root AGENTS.md governs this
library's maintenance and is never an installation asset.

## Skill bundles to copy

| Selection | Required files, relative to library and target root |
| --- | --- |
| ship-cycle | `.agents/skills/ship-cycle/`, `.agents/model-policy.toml`, `docs/agent-guidelines/model-selection.md`, `docs/agent-guidelines/ship-cycle.md` |
| code-sweep | `.agents/skills/code-sweep/`, `.agents/model-policy.toml`, `docs/agent-guidelines/model-selection.md`, `docs/code-sweep.md` |

Read every file in the selected bundle. Both skills share one policy and the
model-selection guide; copy those once. Keep relative paths or update all links
when using another layout. A skill entrypoint alone is not a complete installation.
The detailed [asset catalog](assets.md) lists the remaining guides, checks, kits,
hooks, prerequisites, and limitations. Treat required helpers as part of each item.

## Integrate the approved selection

1. Copy selected new assets and their complete dependencies first, then adapt
   them. Do not reconstruct a shortened workflow from memory or a summary. For
   existing destinations, compare and apply an approved integration diff instead
   of copying over them. AGENTS.md remains the exception described above.
2. Add real commands, context, paths, exclusions, conventions, and validation
   prerequisites. Resolve applicable TODOs. Preserve existing tooling, hooks,
   ownership, credential rules, migration/deployment boundaries, and isolated
   integration requirements. Keep essential conditions, recovery steps, and reasons.
3. Keep one owner for each rule. Reconcile overlapping skill and guide instructions;
   link only to files that exist. Leave deferred items unchanged. New material
   conflicts require a scope decision; approved routine steps do not need another
   approval round.
4. Run the adopted checks and demonstrate meaningful failures in a disposable
   project. Verify copy dependencies, policy roles, and supported API settings.
   Test hook commands directly before any explicitly approved activation.
5. Report adopted and skipped items, model choices, checks and gaps, and remaining
   user decisions. Leave changes unstaged and uncommitted unless separately
   authorized. Do not push, publish, schedule, or install hooks implicitly.

## Adoption scenarios to verify

- Existing project: keep its package manager, tests, hooks, and AGENTS.md intact
  unless the user specifically approves a change to the relevant item.
- Fixed-model preference: all execution descendants use the approved fixed role;
  difficult work can return to the main agent, never to an unapproved model.
- Unavailable execution model: use only the agreed fallback or ask. An unavailable
  reviewer blocks acceptance until an explicit policy change.
- Non-Codex product: use supported settings and skill locations, explain missing
  capabilities, and agree on alternatives rather than passing Codex-only arguments.
- Missing policy or dependencies: report the incomplete adoption; never synthesize
  hidden model defaults or claim the skill is ready.
- Policy update: subsequent assignments read it; active work requires an explicit
  ownership transfer, not an assumed live model switch.
