---
name: ship-cycle
description: Execute approved changes through implementation, useful delegation, independent review, commits, and verified local handoff.
---

# Ship cycle

Complete approved implementation through integration, checks, independent review,
commits, and handoff. Invoking this skill authorizes committing reviewed task
changes unless the user explicitly requests an uncommitted result. Planning and
review-only requests remain read-only.

## Establish the work

Inspect the checkout, scope, project instructions, and nearby documentation.
Preserve unrelated work and the user's branch choice; reuse an existing task
branch or host-managed checkout. Follow project conventions when a new branch is
needed. Record the comparison base and actual check commands. Read engineering
guidance relevant to the change.

Use host defaults unless the user or project specifies agent settings. Honor
explicit model choices and resolve unavailable choices with the user. No particular
provider or policy file is required.

## Implement and integrate

Implement directly or delegate bounded work when useful. Give helpers clear scope,
write ownership, interfaces, and focused checks. The main agent owns integration,
complete validation, independent review, Git, and handoff; workers preserve
concurrent work and leave those decisions to the main agent.

Join all helper work, inspect the complete diff, and reconcile affected contracts,
tests, and documentation before review. Resolve routine choices from evidence;
ask when a necessary change exceeds the approved scope.

## Validate and review

Prepare the integrated change to meet the project's applicable merge requirements.
Inspect existing CI configuration and test gates to identify the checks, then run
their applicable commands locally, respecting change-based selection. Reading CI
configuration does not authorize triggering CI workflows. Add checks for concrete
risks the gate misses. Without an established gate, choose checks for affected
behavior and consumers. Do not run every test or add a build merely because the
tool is available.

Inspect skips and empty discovery. Fix in-scope failures without weakening checks
or changing shared data to obtain a pass. A failing or unavailable required check
blocks acceptance review and completion unless the user explicitly overrides it;
report the gap and continue independent work.

After checks pass, start a fresh independent reviewer in a separate context, even
if no workers were used. The same model is acceptable; self-review is not. If
independent review is unavailable, agree on a review arrangement before acceptance.
Provide the scope, comparison base, complete change including new files, and check
evidence. Request actionable findings across correctness, design, affected
consumers, tests, and documentation, with locations and consequences.

Pause edits during review; the reviewer is read-only. Fix valid in-scope findings,
explain rejected findings, and rerun affected checks. Return the entire revised
result to the same reviewer after each repair until it explicitly approves the
complete current change, including newly discovered issues. Fixing the previous
list alone is not approval. Replace the reviewer only if it cannot continue;
the replacement reviews the whole change.

## Final gate and handoff

After approval, commit only task changes in coherent, reviewable chunks with normal
hooks; no separate commit confirmation is needed. Run the project's final gate
against the committed state. For an explicit "don't commit" request, leave task
changes unstaged and uncommitted and run the same final gate against the complete
worktree. Any repair returns through affected checks and the same reviewer before
repeating the final gate. Never bypass hooks. Push, publication, and deployment
require task authorization.

Clean up owned resources unless a running preview was requested. Report delivered
changes, reviewer approval, checks and gaps, commits or uncommitted state, and
remaining resources or follow-up needs.
