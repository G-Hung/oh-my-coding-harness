# README Writing Standard

Use this rubric to write README files that help future editors work safely.

It is written for both humans and AI agents. The goal is not to maximize
documentation volume. The goal is to maximize future editing safety and speed.

This is a rubric, not a rigid template. Keep the key signals strong, but if a
README needs extra context that materially helps future editors and does not
fit neatly into the suggested sections, include it.

## Purpose

README files are most useful here when they capture what code alone does not
show quickly:

- subsystem intent
- architectural boundaries
- source-of-truth ownership
- active vs legacy/archive status
- historical decisions that should not be reversed casually
- where a future editor should read next

Bad README content is harmful, not neutral. A stale or narrated-code README can
mislead a future AI agent into making worse edits than if it had just read the
code directly.

## Core Principles

- Use fictional examples; keep private records and credentials out of README files.
- Prefer signal over exhaustiveness.
- Preserve useful detail: conditions, exceptions, examples, recovery procedures,
  and decision history. Concision is not a word-count target.
- Document what is hard to infer from code.
- Keep active guidance clearly separate from legacy or archive context.
- Shrink low-value sections instead of expanding them.
- Update README content in the same task when it encodes active behavior,
  contracts, or ownership that changed.
- Use README files to reduce the number of files a future editor must open, not
  to duplicate those files.

## What To Include

Include the sections that materially help future editors. Typical high-signal
content includes:

- A short overview of why the subsystem exists.
- Key files or entry points when the folder is large or non-obvious.
- Boundary rules, invariants, and "do not" constraints.
- Canonical data flow, ownership, or source-of-truth rules when behavior spans
  multiple files.
- Testing or verification notes only when they help safe editing.
- History entries only when they explain why a prior approach was replaced or
  would be dangerous to reintroduce.
- When you add history, prefer a consistent `YYYY-MM-DD` date prefix so future
  AI agents can scan changes chronologically.

## What To Avoid

Avoid README content that mostly restates the code:

- narrated walkthroughs of obvious function signatures or component props
- long prose for simple/static pages
- duplicate security/performance explanations that are clearer in source
- giant file inventories for simple folders
- active implementation guidance mixed together with archive-only behavior
- stale route names, model claims, or file paths left behind after refactors

If a section only restates one source file, consider removing that duplication.
Keep rationale, operational examples, and recovery instructions that explain how
to use or change the code safely even when the implementation is easy to find.

## README Tiers

Not every README should look the same.

### 1. Subsystem / Architecture README

Use this for complex cross-file systems such as workflow orchestration, shared
stores, APIs, or comment architecture.

Good sections here often include:

- `Overview`
- `Files` or `Entry Points`
- `Boundary Rules`
- `Data Flow / Ownership`
- `Testing / Verification`
- `History`

These READMEs can be longer, but every section still needs to earn its place.

### 2. Feature / Medium-Complexity README

Use this for folders with several files, non-obvious behavior, or local design
rules.

Keep these compact. Include only the sections that reduce future file reading
or prevent likely mistakes.

### 3. Leaf / Static / Archive README

Use this for small pages, simple packages, or retired folders.

Usually only include the following, with enough detail to preserve any meaningful
constraint or recovery procedure:

- purpose
- caveats
- active vs archived status
- a short maintenance or history note when needed

## Rough Template

Use this as a menu, not a rigid form. Do not force every section into every
README.

```md
# Feature or Subsystem Name

## Overview

- Why this exists
- What it owns

## Files / Entry Points

- Only for non-trivial folders
- List the files a future editor should read first

## Boundary Rules

- Invariants
- "Do not" constraints
- Source-of-truth ownership

## Data Flow / Ownership

- Only when behavior spans multiple files or layers

## Testing / Verification

- Only the checks that materially help safe edits

## History

- Dated notes only when they prevent regressions
```

## Anti-Pattern Guidance

Weaker README files usually fail in one of these ways:

- They explain code that is already easier to read directly.
- They keep growing after the folder stopped being complex enough to justify
  the length.
- They mix active behavior with historical or archived behavior without clear
  labeling.
- They try to be exhaustive and become stale faster than they help.

If a README feels like a narrated source dump, compress it.

## History Pattern

When a README includes history, prefer a consistent date-first pattern:

- `2026-03-30: retired X because Y`
- `2026-03-27 via commit abc12345: moved ownership from A to B because Y`

The goal is not to log every minor edit. The goal is to preserve the decisions
that future humans or AI agents are most likely to accidentally reverse.

If a history note is present, prefer:

- `YYYY-MM-DD` first for scanability
- one sentence about what changed
- one short reason when the change prevents a likely regression
- optional commit reference when it materially helps trace the change

## Maintenance Checklist

Before keeping or adding a section, ask:

- Does this tell a future agent something the code does not show quickly?
- Does this clarify active vs archived behavior?
- Does this prevent a likely bad edit?
- Does this help a future editor know what to read next?
- Is this section likely to go stale faster than it provides value?

If the answer to the last question is yes, correct or relocate the explanation
to its maintained owner. Remove it only if it is obsolete or the useful detail
remains available through a valid pointer; do not erase an important constraint
merely because keeping it current requires work.

## Repo Expectation

When a task changes a subsystem's active contracts, behavior, ownership, or
historical guidance, update the relevant README in the same task.

When a README becomes noisy, separate useful contracts and examples from stale
or duplicated text. Preserve the former and delete or compress the latter. Check
the before/after meaning, including conditions and exceptions, before finishing.
