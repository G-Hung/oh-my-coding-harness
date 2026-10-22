---
name: ship-cycle
description: Execute approved changes through implementation, useful delegation, independent review, and verified local handoff.
---

# Ship cycle

Complete the authorized outcome through implementation, checks, review, and
handoff. Planning and review-only requests do not authorize edits. Use project
instructions and nearby documentation to find relevant engineering guidance;
read what helps the task, not an entire catalog.

## Establish the work

Inspect the checkout, working tree, approved scope, and existing conventions.
Preserve unrelated work and the user's branch instructions. Reuse an existing task
branch or host-managed checkout, including a detached worktree. Establish a task
branch when starting on the default branch or when project conventions require it.
Record the selected comparison base, or discover the default
branch, and the actual focused, pre-review, and final check commands.

Use the host's existing agent settings unless the user or project specifies a
model policy. The main agent manages helpers through the host's supported tools.
The workflow does not require a policy file, a particular provider, or model
switching. Honor explicit model choices; resolve unavailable requested choices
with the user rather than silently replacing them.

## Implement and integrate

Implement directly when coordination would cost more than it helps. Otherwise
delegate bounded work with clear deliverables, interfaces, exclusive writable
paths, relevant guidance, and focused checks. Reuse capable workers; do not fill
slots. The main agent owns scope, shared contracts, integration, complete gates,
Git, and handoff. Workers preserve concurrent work and report out-of-scope needs;
they do not change branches, stage, commit, start acceptance reviews, or hand off.

Keep write ownership clear, including nested helpers. Pause conflicting writers
and transfer scope and evidence before replacing an owner. Reassess repeated
ineffective repairs instead of repeating them unchanged.

Join all descendants, inspect their changes, and reconcile the whole result.
Keep behavior, tests, and documentation aligned. Worker completion alone does
not establish integration. Resolve routine choices from evidence; request a scope
decision only when a necessary change exceeds authorization.

## Validate and review

Run adopted pre-review checks on the integrated result, including applicable
build, browser, integration, and formal checks. Inspect skips and empty discovery.
Use isolated data and owned resources; never substitute live credentials or repair
shared data to make checks pass. Preserve failure evidence and fix in-scope causes.
Required failures or blocked checks prevent acceptance review and completion
unless explicitly overridden. Do not weaken gates or treat advisory signals as proof.

After checks pass, start one fresh independent reviewer in a separate review
context, even if implementation used no workers. The reviewer may use the same
model, but must not be the implementing agent reviewing its own work. If the host
cannot provide independent review, report that acceptance is blocked and agree
on a review arrangement. Supply the complete scope,
comparison base, full change including new files, and verification evidence.
Request all actionable findings with location, consequence, and evidence across
correctness, security, recovery, architecture, tests, docs, and affected consumers.
The reviewer does not edit or start servers; the main agent owns runtime checks.

Pause edits during review. Validate findings, fix valid in-scope issues, explain
rejections, and rerun affected checks. Return the entire revised result to the
same reviewer for a full review after every repair. Continue until that reviewer
explicitly approves the complete current change, including any new issues found
during re-review. Silence or fixing the previous list is not approval. Replace
the reviewer only if it cannot continue; the replacement reviews the whole change. Repeated feedback may warrant a design correction, not another patch.

## Final gate and handoff

Leave work unstaged and uncommitted unless authorized. When authorized, use
coherent reviewed commits and normal hooks. Run the adopted final gate against
the completed working tree, or committed state when committing. Any resulting
repair returns through checks and the same reviewer, then the final gate.
Never bypass hooks. Push, publication, and deployment need task authorization.

Stop and verify cleanup of owned resources unless a running preview was requested;
do not touch unidentified processes or other tasks' data. Report remaining resources.
Summarize changes, review, check outcomes and gaps, Git state, and follow-up needs.
Report actual delegation and material substitutions; do not invent usage savings
or add telemetry for the report.
