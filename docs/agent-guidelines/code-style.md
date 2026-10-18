# Code Style Guidelines

Apply the sections for the languages and libraries this project actually uses.
After copying, add its conventions and resolve conflicts with existing rules.
No other library document is required.

## TypeScript

- Prefer `type` over `interface` unless a specific library or pattern requires
  an interface.
- Prefer explicit type annotations when they improve clarity, while keeping
  syntax valid and readable.
- Use defined generated enums or status constants instead of hardcoded strings when
  they already exist.
- Prefer `as const` objects with derived union types for app-owned string
  constants and registries. Keep `enum` for generated values or existing
  external contracts where changing shape would add compatibility churn.
- Remove unused imports introduced or exposed by the change.

## React And State

- Prefer semantic HTML over overusing `div`.
- Do not use `React.FC` or `React.FunctionComponent`; annotate props directly
  on plain function components.
- Prefer clean abstractions that keep components readable and avoid bulky render
  trees.
- If a new feature appears to require refactor cleanup, consider that refactor
  task during planning instead of burying it inside an oversized component.
- Prefer `useCallback` and `useMemo` when they meaningfully reduce re-renders or
  stabilize dependencies.
- For Zustand stores, export stable selectors for state and actions, and use
  those selectors in components instead of inline arrow selectors.

## Styling And Imports

- Prefer `cn` for Tailwind class composition instead of long conditional style
  chains.
- Use the project's configured import aliases where appropriate; keep local
  same-folder imports relative. Do not introduce an alias without its configuration.

## Refactoring

- Preserve behavior when refactoring unless the task explicitly changes it.
  Keep useful explanatory comments and update those made inaccurate by the edit.

## Reuse And Naming

- Reuse and adapt existing components, utilities, and local helper APIs before
  duplicating logic.
- Prefer repo-local utilities for established patterns, such as generated ID
  helpers and environment detection helpers.
- Use the project's existing SDK integration and local wrappers for external
  services; inspect versions and contracts before adding another integration.
- For analytics, inspect existing event/property names and flag conventions
  before adding names. Reuse shared constants when names recur, validate flag
  values, and preserve existing reporting contracts. Ask only when a material
  naming or compatibility ambiguity remains after inspection. Do not expose
  credentials or silently change deployment configuration while renaming events.

## Python

- Use the project's declared environment and package manager for commands.
- Keep type annotations and runtime validation aligned. Validate untrusted inputs
  at boundaries; type hints alone do not validate incoming JSON or files.
- Keep exception handling specific. Do not hide failures with broad catches,
  default success values, or type ignores just to pass checks.
- Keep I/O, state changes, and pure transformations distinct enough to test their
  failure behavior. Preserve public contracts when extracting helpers.

## Review Refactoring Outcomes

- Inspect callers and consumers before moving a shared rule. Keep one source of
  truth for statuses, limits, policy, and state transitions.
- Split oversized modules around responsibilities and ownership. Do not scatter
  cohesive logic merely to satisfy a line-count threshold.
- Check success, loading, empty, error, retry, cancellation, and stale-response
  behavior where applicable. Preserve ordering and cleanup when optimizing.

<!-- TODO: Add project-specific choices for aliases, state stores, styling,
external SDKs, and Python conventions. Remove sections for unused libraries. -->
