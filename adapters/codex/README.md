# Copyable skills

- [Ship cycle](.agents/skills/ship-cycle/SKILL.md): the complete implementation,
  adaptive execution and nested ownership, main-agent integration, Astra Medium
  review/fix loop, validation, and handoff procedure. Terra Medium is the execution
  default; the optional Luna-only policy applies to every execution descendant.
- [Weekly sweep](.agents/skills/weekly-sweep/SKILL.md): a broad active-area scan with
  deeper investigation of the last two weeks, affected contracts, and concrete risks;
  dependency, integration-test, slow-test, and README results remain explicit.

After approving adoption, copy either skill folder into the target project's
`.agents/skills/`. Each `SKILL.md` contains its whole procedure and has no required
companion docs, scripts, or model configuration. Modify it after copying: add the
project's real commands, conventions, and chosen agent settings.

For another agent, use its supported skill location or copy the instructions into
its existing workflow. These files do not install plugins, hooks, or schedules.

Preserve the project's detailed safeguards during adoption. A worker-model change
does not alter required checks or the independent review gate. If adopting both
the skill and a focused workflow guide, resolve overlapping rules into consistent
local guidance without leaving essential steps in a file that was not copied.
