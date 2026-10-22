# Testing

Use when adding coverage, refactoring tests, or diagnosing an escaped defect.
Choose tests from observable contracts and risks. This guide is self-contained.

## Choose the boundary

| Technique | Useful evidence | Watch for |
| --- | --- | --- |
| Unit | Local rules, transformations, edge cases | Mocking away the behavior being checked |
| Integration / contract | Persistence, adapters, serialization, component agreements | Fakes that disagree with the real boundary |
| End-to-end | Critical workflows through assembled components | Slow, broad failures for rules a smaller test could isolate |
| Property-based | Invariants over varied inputs | Weak generators or properties that accept broken behavior |
| Characterization / differential | Behavior preserved across refactoring or replacement | Freezing an existing defect or comparing two equally wrong implementations |
| Fault / concurrency | Recovery, retries, partial writes, competing operations | Timing-dependent sleeps instead of controlled failure points or schedules |

## Design useful assertions

- Derive expected results from requirements, contracts, or independently worked
  examples. When an agent writes both code and tests, copying the implementation
  into the expected-value calculation can repeat the same mistake.
- Partition meaningful cases: empty/nonempty, absent/present, below/at/above a
  boundary, valid/invalid, and relevant state transitions. Cover interactions
  where they change behavior rather than multiplying every possible combination.
- Check externally meaningful results and effects, including failure and recovery.
  Avoid assertions about private call order or structure unless it is the contract.
- Confirm the test detects the original defect or a representative broken case
  when practical. A green test that never reaches its assertion proves little.
- Keep fixtures independent and failures deterministic. Control clocks, randomness,
  external effects, and concurrency where they affect the assertion. Preserve
  useful seeds or failing inputs; report skipped and empty test selections.
- Use coverage to find unexamined paths, not as proof of correctness. Keep the same
  source denominator for comparisons, including unimported files.

## Examples

For a limit of 10, test 9, 10, and 11 with expected acceptance from the contract.
Do not calculate the expected answer by calling the same validation helper.

For a stale-result race, pause load A, invalidate, complete load B, then release A.
Assert that B remains authoritative. A long sleep does not ensure that ordering.

## Keep the suite useful

Profile before optimizing. Separate fixture cost from test-body cost and compare
like-for-like environments. Remove redundant scans, mounts, and delays without
removing distinct behavioral assertions. Tests deserve the same clarity as code.
Use focused tests while iterating and the adopted full gate before handoff; this
guide does not waive required integration or end-to-end coverage.
