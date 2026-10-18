# Model selection

Read the [model policy](../../.agents/model-policy.toml) when starting the workflow
and before assigning new work after a policy change. It is an agent-readable
configuration, not a runtime that switches already-running agents.

## Confirm adoption first

The shipped models and settings are a Codex reference. Inspect the actual product,
available models, reasoning settings, delegation API, and existing project policy.
Ask the user to confirm quality, speed, cost, provider/model preferences, adaptive
or fixed-role execution, the reviewer, and permitted fallback choices in one
adoption plan. Roles can use the same model. Preserve the human-selected main
agent. Do not infer consent from this example or from available account access.

Missing, contradictory, or `status = "reference"` policy does not authorize model
selection or delegation. Continue read-only planning, propose the missing choices,
and ask for confirmation. Set `status = "approved"` only after explicit agreement;
the field records that agreement, it cannot create it. Never invent a default
reviewer or declare acceptance without independent review.

For products without these exact settings, propose a supported local format and
map the same roles and constraints into it. Do not pass unsupported API arguments.
If independent review is not supported, explain the gap and agree on a feasible
review arrangement before adopting ship-cycle. Do not count self-review as an
independent reviewer.

## Select within the agreed policy

- `mode = "adaptive"`: select a suitable role from `allowed_roles` using the skill's
  task criteria. No escalation ladder or distinct model per tier is required.
- `mode = "fixed"`: every execution helper, including nested helpers, uses
  `fixed_role`, which must be in `allowed_roles`. Other defined roles do not grant
  permission to use them. Difficult work may return to the main agent.
- Start with `reasoning_effort`. Increase it only when justified and listed in
  that role's `allowed_reasoning_efforts`; an omitted list permits only the default.
- `unavailable = "ask"`: ask before substituting an unavailable execution model.
  Continue independent work that does not require the missing model.
- `unavailable = "allowed-role-or-main"`: in adaptive mode, choose another suitable
  allowed role or let the main agent implement directly. In fixed mode, return to
  the main agent; do not use another role. Report material substitutions.
- The `reviewer` settings are fixed separately. An unavailable reviewer blocks
  acceptance until the user explicitly approves a policy change. Execution
  fallbacks and effort changes do not apply to this role.

Use only supported settings and remain within the user's confirmed choices.
Routine selections inside that policy do not need repeated approval. New models,
settings outside the policy, or reviewer changes require explicit confirmation.
A model-policy change does not weaken required checks or change task authorization.

## Transfer work safely

A policy edit applies to subsequent assignments. To change an active assignment,
pause the previous owner, retain its findings and check evidence, and transfer
exclusive write ownership to a newly configured agent. Join descendants before
integration. Nested helpers follow the same restrictions. Keep one independent
reviewer throughout the fix/recheck loop unless it cannot continue; report any
replacement and preserve the review context.
