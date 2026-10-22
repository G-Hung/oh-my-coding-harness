# Workflow

Use when framing work or handing it off. This guide is self-contained; explicit
implementation workflows may use the project's adopted ship-cycle skill.

## Establish the work

Inspect the checkout, working tree, applicable instructions, and nearby README.
Preserve unrelated changes and the user's branch choice. Use the selected
comparison base; otherwise discover the default branch and record the choice.

Translate the request into observable outcomes and a bounded scope. Resolve
routine details from code and existing conventions. Ask when missing intent or
authorization materially changes the work. Implementation requests authorize
their stated scope; planning and findings-only requests remain read-only.

## Keep the change coherent

Trace affected callers, state, persistence, and consumers. Keep implementation,
behavioral tests, and documentation aligned. Fix demonstrated in-scope problems
without expanding a task into a speculative rewrite. When repeated repairs stop
making progress, reassess the approach and preserve what the attempts established.

Keep progress reports focused on findings, decisions, and remaining uncertainty.
When parallel branches or services affect the work, check relevant merge overlaps
and resource conflicts using the project's existing tools before handoff.
Continue independent work when one check is blocked, and report that limitation.
Follow the project's adopted coordination, review, and validation requirements.

## Handoff

Report what changed, why, what was verified, and what remains uncertain. Distinguish
completed work from proposed follow-up and local preparation from publication.
State Git status and any owned resources still running. Follow the selected
workflow's commit policy. Ship-cycle commits reviewed task changes before handoff
unless the user explicitly requests an uncommitted result. Without an adopted
commit policy or task authorization, leave work unstaged and uncommitted.
Pushing and publishing require task authorization.
Never bypass checks or claim an unavailable check passed.
