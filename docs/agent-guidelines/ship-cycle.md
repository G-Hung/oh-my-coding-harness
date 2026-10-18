# Ship cycle procedure

Complete the authorized scope through implementation, integration, meaningful
checks, independent review, and final validation. An implementation request
authorizes its stated scope; resolve routine choices without another approval
pause. Planning and findings-only audits do not authorize edits. Use the adopted project context and real check commands. Read the
[model-selection rules](model-selection.md) and
[model policy](../../.agents/model-policy.toml) before assigning work.

## Preparation And Ownership

Inspect checkout, branch, working tree, approved plan, and existing project
instructions. Preserve unrelated changes. Establish a task branch before editing
unless the user requests otherwise; follow the project's naming conventions.
Use the selected diff base, otherwise discover the default branch. Record the
base and applicable focused, pre-review, and final check commands. Do not invent
missing commands or treat a sample command as an installed check.

Use direct implementation for tiny or tightly coupled work when delegation costs
more. Use zero, one, or multiple workers for concrete bounded assignments whose
benefit exceeds briefing, integration, and repair cost. Reuse capable workers;
additional waves and nested helpers are allowed within configured capacity across
the entire tree. Do not fill slots or create an extra management layer by default.

The main agent owns scope, write ownership, shared contracts, integration, complete
checks, Git staging/commits, and handoff. It may implement retained work while
workers run. Pass the selected role's model, reasoning settings, and policy context setting
through the available delegation API. Use only arguments that it supports; do not
assume it accepts `agent_type` or `service_tier`. Give concise assignments: repository,
diff base, deliverable, interfaces, relevant guidance, exclusive writable paths,
and focused checks. Tell workers they are not alone and must preserve concurrent
work. Workers may inspect broadly but must report out-of-scope edit needs before
writing. They must not change branches, stage/commit, start acceptance reviewers,
run complete ship gates, or declare the task shipped.

A worker may transfer an exclusive subset of its scope to a helper, report that
ownership to the main agent, stop writing that subset, and join the helper before
returning. Pause overlapping assignments before further edits. A model change
requires pausing the previous owner and transferring scope to a newly configured
agent; preserve useful findings and check evidence. Follow-ups carry changed
requirements and findings rather than repeating the full plan. If one focused
correction leaves the same requirement unresolved, reassess scope/model or take
over instead of repeating equivalent attempts.

Join every worker and descendant. Inspect their diffs, reconcile contracts, and
finish the complete tests and documentation. Worker checks support integration;
worker completion alone cannot establish acceptance.

## Validation And Review

Run the adopted pre-review checks on the integrated change, review affected
READMEs, and finish applicable browser, build, and integration verification under
the project's authorization and isolation rules. Inspect selected tests, skips,
and empty discovery; add meaningful coverage where needed. Distinguish a required
check from an advisory documentation prompt or an unconfigured optional check.
Fix in-scope failures and rerun affected checks. Continue independent work when
blocked, but do not proceed to acceptance review, commits, or completion until
required checks pass or the user explicitly overrides the requirement. Never
weaken a gate, use live credentials, or repair shared data to obtain a pass.

If the project has adopted models for affected state transitions, inspect their
mapping to implementation code. Run the required bounded models and conformance
tests. Require completed baseline exploration and exact expected counterexamples
for controls and witnesses; reject skipped or incomplete checks. Report the bounds,
assumptions, and excluded behavior. A passing model does not prove that application
code conforms to it. Do not introduce a new mandatory formal gate for unrelated work.

After integration and required checks pass, start one fresh independent reviewer
using the adopted policy's `reviewer` settings. Do not use a generic review role
whose settings differ from that policy. This gate applies even with no execution
helpers. If the configured reviewer is unavailable, acceptance is blocked until
the user explicitly approves a policy change. Do not silently substitute a model.

Supply the repository path, diff base, complete latest scope/plan, full integrated
change including new files, and validation evidence. Ask for all actionable
findings together with severity, location, evidence, and impact, covering changed
code and content, correctness, regressions, security, data flow, failure/recovery,
tests, documentation, architectural fit, and nearby consumers. The reviewer reads
without editing or starting servers; the main agent owns runtime verification.

Pause implementation during each review pass. Validate findings against evidence,
fix valid in-scope issues, explain concrete rejections, rerun affected checks,
join repair work, and return the complete revised result to the SAME reviewer
until it approves with no unresolved valid findings. Replace it only if it cannot
continue. Repeated feedback warrants checking abstraction and ownership problems;
request a scope decision when a necessary correction exceeds authorization.

## Final Gate And Handoff

Leave changes unstaged and uncommitted unless the task authorizes commits.
When authorized, commit coherent reviewed chunks under existing ownership rules,
with normal hooks and plain messages. Run the adopted final gate on the completed
state: the working tree for an uncommitted handoff, or after commits for a committed
handoff. Do not run both merely to manufacture an extra phase. Any resulting fix
returns through affected checks and the same reviewer, then a corrective commit
when authorized and the final gate. Never bypass hooks or claim a blocked gate
passed. Push, publication, and deployment require task authorization.

Stop every owned server/container or disposable resource and verify cleanup unless
the user requested it remain running. Use retained handles and verified ownership;
never kill an unidentified listener or remove another task's data or locks. Report
any resource that could not be cleaned up and its stop instructions.

Report the result, review outcome, checks and gaps, Git state, resource cleanup,
and any design follow-up. Summarize observable main settings, worker counts by
model/effort including nested helpers, reuse, and material escalations; mark unknown
settings unknown. Optimize total cost including main coordination, workers,
repairs, validation, and review. Report comparable usage when available, but do
not infer savings from allocation or convert API prices into Codex percentages.
Do not add telemetry infrastructure to satisfy this report.

<!-- TODO: After copying, record actual focused/pre-review/final check commands,
diff-base and commit conventions, resource ownership, build approval boundaries,
and isolated integration prerequisites. Keep every existing project safeguard. -->
