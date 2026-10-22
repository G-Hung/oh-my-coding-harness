# Design and reuse

Use when extracting shared code, moving responsibilities, or refactoring.
Inspect callers and existing abstractions first. This guide is self-contained.

- Consolidate shared knowledge, not merely similar syntax. Two callers belong
  together when the same rule should change both; otherwise duplication may be
  cheaper than coupling them through flags and exceptions.
- Put constants, policies, and transitions with their domain owner. Reuse that
  owner instead of creating a global constants file or another parallel registry.
- Reuse existing local helpers and SDK wrappers before adding another integration.
  Inspect versions and contracts; common examples include ID generation and
  environment detection. Preserve useful existing implementations.
- Keep things that change for the same reason together. Split responsibilities
  when independent changes interfere, not just when a file reaches a line limit.
- Hide meaningful complexity behind a small interface. A wrapper that repeats
  every argument and exposes every detail may add more reading than it saves.
- Separate policy from mechanisms and pure transformations from effects where
  this makes behavior easier to understand and verify. Do not require new layers.
- State consequential invariants near their owner. Prefer representations and
  operations that preserve them over repeated repairs in callers.
- Refactor against an established behavior contract. Inspect consumers, preserve
  useful comments, and use existing tests or focused characterization evidence.
  Treat intentional behavior changes separately; do not preserve a known bug
  merely because a snapshot captured it.

## Examples

`requestTimeoutMs = 5000` and `cacheTtlMs = 5000` express different policies.
Keep them independent. A maximum upload size used by both admission and processing
is one policy: give it an owner and make both consumers use that contract.

A shared formatter that accumulates `forEmail`, `forExport`, and `legacyMode`
flags may combine unrelated behavior. Inspect which rules really vary together;
separate the callers before extracting only their stable common transformation.

## Review signal

Can a reader find the rule's owner and understand its callers without following
unnecessary layers? Does the change reduce inconsistent edits while preserving
distinct behavior? Fewer lines alone do not establish either outcome.
