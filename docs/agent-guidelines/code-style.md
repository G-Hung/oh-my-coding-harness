# Code style

Follow the project's language, formatter, and library conventions. Prefer
consistent local choices over introducing a new personal style. This guide is
self-contained.

- Keep exception handling specific and failures visible. Avoid broad catches,
  default success values, or ignored errors that conceal the cause.
- Use existing import conventions and configured aliases. Remove unused imports
  introduced or exposed by the change.
- For user interfaces, prefer semantic elements and clear component boundaries.
  Add memoization when measured cost or dependency stability justifies it.
- Preserve behavior during refactoring, inspect callers, and update inaccurate
  comments. Check the states affected by the change.

For example, returning `[]` after any storage error makes an outage look like an
empty result. Handle an expected missing record explicitly and propagate or
report unexpected failures through the project's error path.

Use the project's selected engineering notes for deeper design decisions.
Record stack-specific choices near the code that uses them.
