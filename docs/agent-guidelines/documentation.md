# Documentation

Update the nearby README when active behavior, interfaces, ownership, failure
handling, or non-obvious constraints change. Create documentation at a useful feature
or subsystem boundary rather than one document per file.

Document what a future editor cannot discover quickly from code: invariants,
source of truth, recovery rules, reasons for a decision, and where to read next.
Remove narrated code and stale inventories. Label archived guidance clearly.

Preserve useful detail rather than optimizing word count. Conditions, exceptions,
worked examples, failure/recovery steps, and decision history may prevent mistakes
even when they make a guide longer. Before removing a rule, check its consumers
and whether another maintained explanation preserves its meaning. When moving
detail, keep a clear conditional pointer and verify the target is available to
the reader. Independently copied material must retain its essential procedure.

## Documentation checks

Use the project's README change prompt, if available, to find potentially stale
nearby READMEs. A changed README does not prove it is accurate, and an unchanged one
need not be wrong. Review the actual behavioral change before updating text.
Inspect overly broad README ownership or oversized content using the README
rubric below. Check changed local links with the project's checker or inspect
their targets directly when no checker is installed.

Use the project's existing check commands. No other library document is required.
Neither heuristics nor link checks establish semantic correctness.

## README Rubric

- Document subsystem intent, boundaries, source-of-truth ownership, failure and
  recovery rules, and decisions future editors must not casually reverse.
- Keep small/static folders brief. Give complex cross-file subsystems the detail
  needed to edit safely; do not force every folder into the same template.
- Use dated history only to explain an important decision or replaced approach.
- Do not collapse distinct behaviors into a generic summary that loses when a
  rule applies, why it exists, or how to recover when it fails.
- Remove stale routes, configuration claims, and file inventories after changes.
- Keep active guidance separate from archive context. Do not preserve narrated
  function signatures or obvious code walkthroughs merely to fill sections.
- Maintain one canonical explanation. If you link to another file, verify that
  it exists in this project and is the actual owner of the information.

## Canonical maps and generated files

When the project has cross-system behavior maps, keep them aligned with changes
to orchestration, retries, persistence, or external service use. Maintain one
canonical owner; link to it rather than maintaining parallel lists.

Edit generated documentation at its declared input and run its generator. Never
hand-edit generated output to hide drift. Use fictional examples for public
material and keep credentials and private records out of documentation.

Comments should explain why a constraint exists, particularly around lifecycle,
concurrency, and recovery. Avoid restating syntax.

<!-- TODO: Name existing canonical maps and generators here only if this project
has them. Do not introduce empty registries to satisfy this guide. -->
