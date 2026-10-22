# Debugging

Use for an unexplained failure or when successive repairs stop adding evidence.
An obvious local defect need not become a lengthy investigation. This guide is
self-contained.

1. Establish expected versus observed behavior. Preserve the first useful error,
   input, trace, and runtime identity. Check the test's expectation too.
2. Reproduce with the smallest useful case in an isolated environment. Confirm
   that executed source, build, configuration, and checkout match the inspection.
3. State a hypothesis and an observation that would support or reject it. Choose
   a focused probe that separates plausible causes; avoid changing several things
   at once or rerunning an unchanged experiment without a reason.
4. Use the observation to narrow the cause. Compare passing and failing inputs,
   revisions, or execution paths. Update the hypothesis when evidence disagrees.
5. Repair the cause and verify the original failure plus affected contracts.
   Add a regression when it protects meaningful behavior. Remove temporary probes
   and clean up only resources owned by the investigation.

## Example

A save appears successful but a reload loses the change. Separate three hypotheses:
the write failed, the reload reads another store, or the cache returns old data.
Inspect the write outcome and storage identity before changing cache policy.
An extra retry would not distinguish these causes and may duplicate the write.

## Keep the evidence useful

For a multi-step investigation, keep a brief record of hypothesis, experiment,
prediction, and observation in the existing task report or diagnostic artifact.
This prevents repeated attempts after handoff and gives later sweeps evidence.
Do not create a logging platform or retain secrets and unrelated conversations.

Do not hide failures with broad catches, default success values, or relaxed tests.
If isolation or tools are unavailable, record the blocker and continue independent
inspection. A diagnostic rerun supplements the original evidence; it does not erase it.
