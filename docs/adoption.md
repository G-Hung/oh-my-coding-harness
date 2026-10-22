# Adopt the harness

Start here when a user shares the repository URL, including in Plan Mode. Read
the [article](articles/coding-agent-harness.md) for motivation, then assess the
assets against the target environment. A URL or planning request is not permission
to install. You may inspect or obtain a reference checkout without integrating it
into the target project. Do not work around private-repository access restrictions.

For URL-only access, use a unique temporary shallow checkout when terminal and
network access are available and local inspection will help. Otherwise read the
required files through available tools and report access gaps. Remove only the
task-owned reference checkout when it is no longer needed.

### Understand the project and the ideas

Read existing `AGENTS.md` and area instructions, then inspect the architecture,
toolchain, checks, CI, hooks, and actual working practices. For a new project,
use its planned requirements. Use the [asset catalog](assets.md) to explore the
problems these examples address, not as a shopping list of files to install.

Compare behavior, not just names: an existing tool or instruction may already
solve the problem, or contain a useful gap. Before dismissing an idea, inspect
the relevant workflow; for parallel Git work, that includes worktrees, branches,
and integration checks. Missing evidence is a reason to investigate or ask,
not evidence that the capability is unnecessary.

Read the complete relevant assets. Reuse suitable implementations; when the stack
differs, adapt the idea using the project's ecosystem and existing tools. Keep
the useful behavior and failure feedback, not incidental language or layout
choices. Do not replace working tooling merely to match a kit, or add capabilities
without a project-specific benefit.

### Propose the useful changes

Lead with recommended improvements and decisions for the user. Group related
ideas; a separate report row for every script is unnecessary. Explain the current
approach, the benefit, destination files and dependencies, and how to verify the
result. Briefly account for areas already covered or not useful here.

Make dependency installation, hook activation, and model-policy changes visible
in the proposal. Preserve existing ownership and safeguards. Use item IDs so the
user can select changes without approving unrelated work.

### Approve the plan once, then carry it out

Present the recommendations together and request explicit approval before editing,
copying, installing dependencies, or enabling hooks. The user can approve the whole
plan or a selected group of items in one reply. Do not ask a separate question for
each item. Leave unapproved or deferred items unchanged. Approval covers the listed
helpers and implementation steps; complete them without asking the same question
again.
If a new conflict requires a material change to the approved scope, explain it and
request approval for that change.

## Agent settings and review

Use the host's existing settings by default. Inspect whether it supports helpers
and a fresh independent review context. The main agent manages helpers; ship-cycle
keeps the same reviewer through repairs until explicit approval.

If the user wants specific models, propose available choices and record them
using the project's existing configuration or the optional
[model preferences example](../.agents/model-policy.toml). The same model may fill
both roles. These preferences do not configure the host; use its supported tools.
Choose the record's location to fit the project and reference it from an existing
project instruction or host configuration entry point so future agents can find it.
Any targeted AGENTS.md edit still follows the approval rule below.
Honor existing user choices and explain any unavailable capability. If independent
review is unavailable, agree on a review arrangement before claiming acceptance.

## AGENTS.md is a reference exception

Compare the [template](../templates/AGENTS.md) with existing target instructions:
identify principles already covered and useful gaps, preferably in their existing
guide rather than a duplicate rule. Exclude AGENTS.md from the default copy and
edit list; protection from overwriting is not a reason to skip this comparison.
General adoption approval does not authorize changing it. Offer concrete optional
additions with reasons; apply one only if the user explicitly selects that targeted
addition. Preserve all other text. Never replace the file or insert a reference map
just because skills were adopted. If absent, offer creation as a separate explicit
choice; do not create it automatically. The library's root AGENTS.md governs this
library's maintenance and is never an installation asset.

## Skill bundles to copy

| Selection | Source folder in this library |
| --- | --- |
| ship-cycle | `.agents/skills/ship-cycle/` |
| code-sweep | `.agents/skills/code-sweep/` |

Install each selected folder in the target host's supported skill location and
confirm that the host discovers its `SKILL.md`. The source paths above do not
prescribe the destination. Use the host's invocation and agent tools.

Read and copy the selected skill. Model preferences and engineering guides are
optional; no separate workflow documents are needed. Keep installation instructions
here, outside runtime skills. Retain installed assets and remove only task-owned
temporary reference checkouts when no longer needed.
The detailed [asset catalog](assets.md) lists the remaining guides, checks, kits,
hooks, prerequisites, and limitations. Treat required helpers as part of each item.

Engineering guides are optional selections, not additional skill gates. Copy
only useful clusters. If copying the guidelines index, retain only links to
adopted or existing files. Remove optional cross-links whose guides were not
selected; each general guide retains its own essential instructions. Required
skill assets above must remain present, even when the index is omitted.

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
   project. Verify copied assets, review capability, and any requested model choices.
   Test hook commands directly before any explicitly approved activation.
5. Report adopted and skipped items, any model choices, checks and gaps, and remaining
   user decisions. Leave changes unstaged and uncommitted unless separately
   authorized. Do not push, publish, schedule, or install hooks implicitly.

## Adoption scenarios to verify

- Existing project: preserve its tools, hooks, and instructions; apply selected changes.
- No model policy: use host defaults; both skills remain usable.
- Requested model unavailable: explain the limitation and resolve that choice.
- Independent review: start a separate reviewer and keep it through explicit approval.
- Another host: use its skill location and agent tools without platform-specific arguments.
- Partial adoption: copied skills stand alone; the index links only to selected guides.
