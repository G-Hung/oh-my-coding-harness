# State and recovery

Use when changing shared state, caches, asynchronous work, retries, or persistence.
Trace reads, writes, and ownership first. This guide is self-contained.

- Identify authoritative state and derive other values when practical. If copies
  are necessary, define who synchronizes them and what staleness is acceptable.
- Keep mutable state within its owner's operations. A private field is not
  protected if a returned reference lets callers mutate it. Use controlled
  operations, immutable values, or defensive copies as the contract requires;
  shallow copies do not isolate nested mutable objects.
- State the invariant and the atomic boundary. Check-then-write sequences can
  race across requests, workers, or an `await`, even without shared threads.
- Include all behavior-changing inputs in cache identity, including authorization
  scope where relevant. Define invalidation, lifetime, and failed-load behavior.
  A TTL alone does not guarantee freshness after a write.
- Reject obsolete asynchronous results using the operation's identity or version.
  Cancellation may stop local waiting without undoing an external effect.
- Retry only with a clear failure policy. For effects that may already have
  completed, use an idempotency key or reconciliation before repeating them.
- Define partial-failure recovery and cleanup ownership. Transactions, atomic
  replacement, compensation, and reconciliation solve different boundaries;
  choose from the actual system rather than assuming all effects can roll back.

## Examples

`if available(): reserve()` can race. Put `reserveIfAvailable()` under the owner
that can enforce the condition and change atomically.

Cache race: load A starts, a write invalidates the entry, then A finishes with
old data. Invalidation must also prevent A from publishing that obsolete result,
for example by comparing a captured generation before insertion.

A payment request times out after the remote service accepts it. A blind retry
may duplicate the effect; reuse the supported idempotency identity or query the
outcome. A local timeout does not prove remote failure.

## Verification signal

Exercise failure between steps and force competing operations into a meaningful
order. Check both the result and durable state. Random sleeps and repeated green
runs do not establish that a race is gone.
