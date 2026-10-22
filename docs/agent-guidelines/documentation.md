# Documentation

Update the nearby README when active behavior, interfaces, ownership, failure
handling, or non-obvious constraints change. Create documentation at a useful feature
or subsystem boundary rather than one document per file.

Document what a future editor cannot discover quickly from code: invariants,
source of truth, recovery rules, reasons for a decision, and where to read next.
Remove narrated code and stale inventories. Label archived guidance clearly.

Keep conditions, examples, recovery steps, and rationale that change how a reader
uses or edits the system. Merge repeated warnings and remove obsolete detail.
When moving a procedure, keep it available to its consumers, including readers
who copy the guide independently.

Lead with the result or action. Add a limitation where it changes the reader's
decision. For example, replace "Passing checks do not guarantee correctness, and
some environments may differ" with "The unit tests pass; the database integration
check is blocked because its service is unavailable." Omit unrelated caveats.

## Simplified Technical English

Use an ASD-STE100-inspired style for maintained English documentation, comments,
and docstrings. This is a software adaptation, not a claim of full compliance
with the standard or its controlled dictionary. Use the
[official ASD-STE100 overview](https://www.asd-ste100.org/about_STE.html) as the
reference for the standard.

- Give each sentence one main idea. Use short sentences when they preserve clarity;
  do not omit conditions or necessary words to meet a length target.
- Name the actor when ownership matters. Prefer active voice and direct verbs.
- Put prerequisites and conditions before the action. Use numbered steps when
  the reader must perform actions in order.
- Use the same term for the same concept. Preserve distinctions such as missing
  versus zero, failed versus blocked, and model checking versus implementation tests.
- Preserve requirement strength. Do not interchange `must`, `may`, and `must not`.
- State consequential limits, failure behavior, and recovery steps explicitly.
  Explain the reason for a constraint when code alone does not make it clear.
- Avoid idioms, filler, dense noun phrases, and ambiguous pronouns.

For example, replace "If appropriate, leverage the gate" with "If a change affects
a modeled contract, run its adopted formal check." Keep the exact condition that
limits when the action is required.

Preserve identifiers, commands, links, heading anchors, legal notices, and tool
directives. Do not rewrite executable examples to satisfy a prose rule. A style
pass does not authorize changes to runtime prompts, UI text, logs, error strings,
fixtures, snapshots, generated content, or historical records. Check the code
before rewriting a behavioral claim and report uncertainty where evidence is missing.

## Documentation checks

Use the project's README change prompt, if available, to find potentially stale
nearby READMEs. A changed README does not prove it is accurate, and an unchanged one
need not be wrong. Review the actual behavioral change before updating text.
Inspect overly broad README ownership or oversized content using the README
rubric below. Check changed local links with the project's checker or inspect
their targets directly when no checker is installed.

Use the project's existing check commands and review the changed meaning.

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
