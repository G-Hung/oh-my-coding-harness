# Safety and resource ownership

Inspect the actual environment and data flow before operations with external or
destructive effects. A local app may connect to real shared data. Distinguish
read-only diagnostics from commands that migrate, repair, generate content,
charge money, send messages, or publish.

Use existing task authorization; do not introduce repeated confirmation for
already-authorized work. When an action is outside it, prepare the concrete
change and explain the remaining decision. Do not bypass a rejected tool action
by changing channels or weakening controls.

## Secrets and configuration

Inspect variable names and contract shape without printing secret values. Keep
credentials out of source, logs, reports, screenshots, and examples. Do not
source an unknown environment file as shell code. Do not replace a blocked fake
provider with live credentials just to make tests pass.

Prefer ordinary code configuration for non-sensitive behavior settings. Adding, removing, or changing environment variables or their contract requires
explicit approval for that configuration change; feature approval alone does not
authorize new deployment settings. Account for all consumers and document the
change. Authorization to change configuration never authorizes printing secrets.
Never mistake a custom forbidden-text scan for a comprehensive secret scanner.

## Data and migrations

Trace reads and writes across APIs, background work, storage, and consumers.
Check ownership, authorization, retries, partial failure, and transaction boundaries.
Use the project's migration tooling; distinguish generating or inspecting a
migration from applying it. Assess reversibility and data-loss risk before a
migration or cleanup, and obtain missing authorization for destructive effects.

Use disposable fixtures for integration tests when available. Do not repair
shared provider or database state as a side effect of a diagnostic.

## Processes and shared resources

Record ownership of servers, containers, temporary databases, and test artifacts.
Clean up only resources created by the task and verified as owned. Never kill
an unidentified listener, prune shared caches, or delete another task's locks.
Retain a process/session handle, confirm the actual listener after startup, and
verify it disappears after shutdown. If cleanup fails, report the owned resource
and exact stop instructions. A port number by itself is not proof of ownership.
