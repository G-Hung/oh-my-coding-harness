# Formal verification

Use bounded model checking when correctness depends on action order: concurrent
writes, retries, ownership changes, recovery, or publication. Start with one
consequential protocol whose state and required behavior you can explain.
Ordinary lint, types, and tests remain useful; a model adds evidence about the
interleavings in its declared scope.

## Establish the contract

Read the implementation, callers, and tests before writing the model. Define the
state, transitions, safety invariants, finite bounds, and assumptions. Map each
transition to its implementation owner and tests. Distinguish intended behavior
from existing behavior when they disagree.

Keep meaningful failures in the model: stale observations, lost responses,
interruptions, and rejected recovery where relevant. Do not assume away the race
you want to check. State which actions are atomic and why that assumption is valid
at the implementation boundary. Record excluded behavior explicitly.

## Check the model and its sensitivity

- A baseline must complete exploration of its finite state graph with no violation
  and no states left on the queue. A successful exit alone is insufficient.
- Remove one guard at a time in negative configurations. Require the specific
  invariant violation that demonstrates why the guard matters.
- Use a reachability witness when a scenario might be impossible. Keep the guards
  and check a deliberately false claim that the scenario cannot occur. Its exact
  counterexample establishes reachability, not eventual completion.
- Reject parse errors, wrong violations, timeouts, interruptions, and unavailable
  tools. None of these outcomes supplies the expected counterexample.

Pin the checker and verify its checksum. Bound runtime and memory. Use disposable
state directories and preserve logs. Keep these checks opt-in unless the project
has adopted them as a required gate. Do not add hooks or install runtimes as an
unrequested consequence of running an audit.

## Connect evidence to code

Test the actual implementation at the modeled boundaries. Control scheduling with
explicit steps, deferred results, or events instead of wall-clock sleeps. Assert
the observable contract independently of the guard predicates. Include failure
and recovery cases and verify that a broken guard makes the test fail.

Treat a counterexample as a lead. Compare its action order with the source and
reproduce a defect in implementation tests before changing production behavior.
A mismatch may require correcting the abstraction rather than the code.

Record the model/configuration, tool, source, test, runtime, and bound identities.
Source hashes reveal drift; they do not prove that code implements the model.
Evidence is reusable only for compatible inputs and assumptions. A required gate
cannot be waived merely because an older model run passed.

## Report the result precisely

Separate baseline results, successful negative controls, witnesses, and implementation
tests. Report configured bounds, assumptions, excluded behavior, skipped tests,
and blockers. Review model correspondence when an adopted modeled contract changes;
run its relevant checks according to the project's verification policy.

TLC checks the reachable states of a configured finite model. The result does not
automatically apply to arbitrary system sizes or application code. It does not
establish a theorem proof, refinement proof, or a liveness claim that was not
specified and checked. See the
[TLA+ introduction](https://learning.tlapl.us/intro/platform/) for this distinction.

<!-- TODO: After copying, name adopted protocols, implementation owners, finite
bounds, exact commands, prerequisites, and which changes require these checks.
Keep this guide usable without other library files. -->
