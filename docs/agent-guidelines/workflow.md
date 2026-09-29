# Workflow

## Establish the work

Inspect the checkout, branch, working tree, applicable instructions, and nearby
README before editing. Preserve unrelated changes. Use the user-selected base
for comparison; otherwise discover the default branch. Record the base rather
than silently comparing against a stale or unrelated branch.

Translate the request into observable outcomes and a bounded plan. Resolve
implementation details from code before asking questions. Ask only when missing
intent, ownership, or authorization materially changes the work. An explicit
implementation request authorizes its stated scope; it does not require a second
approval for routine choices. An audit or planning request remains read-only.

## Execution and ownership

Keep the main agent on the human-selected settings. It owns scope, shared
contracts, integration, complete checks, Git, and handoff, and may implement
directly. Use zero, one, or several workers only for concrete bounded assignments
that justify their briefing, integration, and repair costs. Tiny or tightly
coupled work often belongs with the main agent. Reuse capable workers; additional
waves and nested helpers are allowed within available capacity across the tree.

Choose execution capability directly from ambiguity, coupling, consequences,
verification, and expected repair cost under the adopted model policy. Do not
force an escalation ladder or fill slots. Assign exclusive writable paths and
interfaces, relevant guidance, and focused checks with a concise self-contained
brief and fresh context where supported. Tell workers to preserve concurrent
work. They may inspect broadly but must return out-of-scope edit needs to the
main agent; no worker may expand scope, change branches, stage/commit, start
acceptance reviews, run complete ship gates, or independently hand off the task.

A delegating worker transfers an exclusive subset of its scope, reports it to
the main agent, stops writing that subset, and joins its helpers before returning.
Pause any ownership conflict before further writes. A model change requires
pausing the previous owner and explicitly transferring scope and useful evidence
to an appropriately configured worker or the main agent. After a focused repair
leaves the same requirement unmet, reassess the scope/model rather than repeating
equivalent attempts. Keep follow-ups to changed requirements and findings.

Join every descendant before acceptance. The main agent inspects worker diffs
and reconciles the complete change; worker completion and checks alone cannot
establish integration or acceptance.

## Complete a coherent change

Follow the real data flow across callers, state, persistence, and consumers.
Keep related implementation, behavioral tests, and documentation together.
Fix demonstrated in-scope problems; do not expand a task into a speculative
rewrite. When repeated patches stop making progress, reassess the approach and
state the actual conflict or missing prerequisite.

Keep progress reports short: what changed, what was learned, and what remains.
Separate verified behavior from plans and hypotheses. Continue independent work
when one check is blocked, recording the limitation.

## Independent review

After integration and applicable checks, provide one independent reviewer the
request, plan, complete diff, known constraints, and verification evidence.
Ask for all actionable findings together, prioritizing correctness, regressions,
architectural fit, test gaps, and cross-layer effects. Require a concrete trigger,
consequence, and file/line evidence. Optional cleanup is not a blocking defect.
Use one fresh reviewer under the adopted review-model policy, independently of
the execution-model policy. The reviewer inspects all changed code and content
without editing or changing Git state; the main agent owns browser/build work
unless runtime verification is explicitly delegated to a separate owner.
Pause implementation during each review pass so the reviewed result stays stable.

Evaluate each finding against the code. Fix valid in-scope issues, explain any
rejected finding with evidence, and return the updated diff to the same reviewer.
Repeat broad reviews of the entire revised change until the reviewer explicitly
approves or reports no valid in-scope findings. Do not narrow review to the previous
comments or replace the reviewer to obtain a different answer. Replace it only if
it fails or cannot continue. If independent review is unavailable, report the gate
as blocked; self-review does not satisfy it.

Do not begin review until implementation, integration, tests, documentation, and
the required pre-review gate are complete. Do not declare completion or commit
with valid in-scope findings outstanding. Required checks that fail or cannot run
block acceptance unless the user explicitly overrides the requirement; continue
independent work and report the blocker without weakening checks. After the loop,
assess whether repeated feedback exposed wrong abstractions, duplicated rules, unclear ownership, an
oversized module, or ordinary independent bugs. Correct in-scope design problems
and review resulting changes again; report any required plan change.

## Handoff and Git

The default endpoint is a reviewed, verified, uncommitted diff for the user.
Do not stage or commit unless the current task explicitly authorizes it. A user
request to review before committing overrides any inherited commit workflow.

When commits are explicitly authorized, use coherent changes and plain,
descriptive messages under existing project conventions. Do not add agent tags,
model names, decorative prefixes, or attribution trailers unless requested.
Never bypass hooks. Run the adopted final gate on the completed working tree for
an uncommitted handoff, or on the committed state when commits are authorized.
Any final-gate fix returns through affected checks and the same reviewer, then
a corrective commit when authorized and another final gate. Pushing or publishing
needs separate task authorization.

Report what changed and why, checks and outcomes, any remaining risks or blockers,
and Git status. Summarize actual agent allocation, reuse, material escalations,
and available comparable usage. Include coordination, workers, repairs, checks,
and review in cost reasoning; cheaper workers alone do not establish savings.
Do not create telemetry merely for this report. Do not claim complete independent
review when only self-review was possible, or claim publication from local preparation.
