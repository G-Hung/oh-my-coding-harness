# Contracts and naming

Use when defining or changing an interface, data shape, name, or validation rule.
Inspect actual consumers and existing terminology. This guide is self-contained.

- Name domain concepts consistently. Make units and relevant distinctions clear:
  `timeoutMs`, `expiresAt`, and `retryCount` answer different questions.
- Describe observable behavior: accepted inputs, results, effects, failure cases,
  and ordering guarantees that callers need. Avoid narrating implementation steps
  or writing a formal specification for an obvious local helper.
- Keep missing, empty, zero, failed, and unknown distinct when they mean different
  things. Do not convert a failure into a plausible success value.
- Validate untrusted data at its boundary and carry validated representations
  inward. Static types alone do not validate files, requests, or stored records.
  Retain internal invariant checks where mutation or another boundary can break
  assumptions; do not scatter redundant validation everywhere.
- Preserve caller guarantees when replacing an implementation. Requiring more
  from callers or promising less is a contract change, even if types still match.
- Before a rename, inspect serialized fields, configuration, events, stored data,
  documentation, and external consumers. Use migration or compatibility support
  when required; do not assume a source-code rename reaches every consumer.

## Examples

A function that accepts any iterable cannot be replaced transparently by one
that accepts arrays only. A result promised in input order cannot become an
unordered set without checking and changing the callers' contract.

Prefer a meaningful result such as `Found(value) | Missing | Failed(error)` when
callers need different recovery actions. Do not invent a result framework when
the language's existing optional value and error mechanism already expresses it.

For a parser, specify whether invalid input is rejected and whether the input is
modified. Tests should assert those effects, not the parser's private loop shape.
