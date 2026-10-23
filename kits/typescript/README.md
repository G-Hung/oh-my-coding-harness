# TypeScript harness kit

A small npm / TypeScript / ESLint / Jest reference, with copyable checks. Node 22.13+ (22.x) or Node 24+ and npm are required. Git is needed for changed-file documentation prompts and doctor. Preserve an existing project's package manager and tooling: merge relevant scripts and dependencies rather than replace its manifest or lockfile.

## Adopt and verify

For a new project copy this entire directory, including dotfiles, into its Git root. Run `npm ci`, then `npm run check` and `npm run doctor`. Hooks are not installed automatically. Replace the sample `src/` fixture after verifying the kit; it proves only that the tools work together.

For selective adoption copy `harness.config.cjs`, the chosen `scripts/*.cjs` entry points, and **all of `scripts/lib/`**. Merge the matching package commands. The Markdown link checker additionally needs `unified` and `remark-parse`; other harness scripts use Node built-ins. The full static/test kit additionally needs the package devDependencies, `tsconfig.json`, `eslint.config.cjs`, `jest.config.cjs`, and relevant tests. `tests/harness.test.cjs` verifies script behavior; adapt its coverage when changing the scripts.

Edit the TODOs in [configuration](harness.config.cjs): source roots, Markdown roots, excluded generated/vendor directories, extensions, physical-line limit and required check scripts. Paths are project-root-relative literal paths, not globs. Each configured root must exist. Scans reject symlinks rather than follow them; exclude intentionally linked directories explicitly. The kit directory becomes the project root when copied; run its commands from that root.

## Commands

Keep TypeScript within the peer ranges of both `ts-jest` and `typescript-eslint`.
The current kit uses TypeScript 5.9. TypeScript 7 is not compatible with these
tools: `ts-jest` 29.4.15 requires `<7`, and `typescript-eslint` 8.72.0 requires
`>=4.8.4 <6.1.0`. Do not use `--force` or `--legacy-peer-deps` to bypass this
conflict. Recheck both peer ranges before upgrading the compiler.

| Command | Behavior |
| --- | --- |
| `npm run check` | Sequential lint, types, full Jest tests, script tests, line check and local Markdown links; continue gathering failures and retain failure logs |
| `npm run lint` / `npm run typecheck` | Strict lint (including warnings) and TypeScript checks |
| `npm test -- --runTestsByPath src/clamp.test.ts` | Focused test iteration; run the full gate before handoff |
| `npm run test:harness` | Behavioral tests for the copied tooling |
| `npm run check:loc` | Advisory list of source files above 500 physical lines by default, including blank lines and comments |
| `npm run check:loc -- --strict --max-lines 500` | Blocking line limit; change config/check command if this belongs in your gate |
| `npm run check:readme` | Advisory nearest existing README prompts for staged, unstaged and untracked source changes; falls back to the root README |
| `npm run check:readme -- --staged` | Only staged paths; reads current working-copy README files |
| `npm run check:readme -- --base main` | Merge-base-to-working-tree changes plus untracked files; fails for invalid base |
| `npm run check:links` | Blocking local Markdown link/image destination existence check |
| `npm run test:profile` then `npm run test:slow` | Collect fresh Jest JSON and report top spent suites/cases |
| `npm run doctor` | Runtime, installed tools, configured source scope and Git-root readiness; report optional hooks |

Line limits are review signals. Extract cohesive responsibilities when useful; do not fragment code merely to satisfy the threshold. Missing roots, empty source scans and bad configuration fail even in advisory mode. README co-change is not proof of accuracy; missing documentation is reported explicitly and requires agent judgment. The README command requires this kit to be copied to a standalone Git project root, so it intentionally refuses to analyze the library's parent repository.

Link checking parses ordinary Markdown and reference links, ignores fenced examples, and supports percent-encoded spaces. Leading `/` means project root. It does not validate anchors, HTML, site routing, remote URLs, or semantic accuracy. Adapt the checker before using it on a site with URL rewrite conventions.

Set `JEST_SLOW_TOP=10 JEST_SLOW_MIN_MS=100 npm run test:slow` to narrow the diagnostic. It reports input modification time and recorded test success. Always create a fresh profile first; timing depends on the machine and run mode, and parallel suite time cannot be summed into elapsed time. A slow test is not automatically redundant. Optimize expensive setup or scope only after preserving its behavior coverage. No complexity-dependent suite registry or coverage threshold is imposed.

## Pre-commit and pre-push

Copy [pre-commit](hooks/pre-commit) and [pre-push](hooks/pre-push), together with
their package commands, configuration, scripts, and helpers. Activation is opt-in.
Run these commands from the target project's Git root.

1. Inspect existing configuration and the effective hook directory:

   ```sh
   git config --show-origin --get core.hooksPath
   git rev-parse --git-path hooks
   ```

   No configured `core.hooksPath` is normal. Inspect the directory returned by the
   second command for existing hooks. If the project uses a hook manager, merge
   these commands into it. Do not replace its hooks or change its path blindly.

2. Install dependencies and test both stages before activation:

   ```sh
   npm ci
   sh hooks/pre-commit
   sh hooks/pre-push
   ```

   These commands run the checks without committing or pushing. In a disposable
   checkout, introduce a type error and confirm pre-commit fails. Restore it,
   introduce a failing test, and confirm pre-push fails. Restore the fixture and
   rerun both stages successfully.

3. For a project with no existing hook setup, enable these files locally:

   ```sh
   chmod +x hooks/pre-commit hooks/pre-push
   git config --local core.hooksPath hooks
   git rev-parse --git-path hooks
   test -x hooks/pre-commit && test -x hooks/pre-push
   ```

   The effective directory must resolve to the copied `hooks/` directory, and both
   executable checks must pass. `npm run doctor` reports the configured path; it
   does not establish that either hook is installed or executable. Activation is
   local to this repository; verify each checkout before relying on it.

Pre-commit runs lint, types, and staged README prompts. Pre-push runs `npm run
check`, including tests. A required command failure blocks the operation; README
and default file-size prompts remain advisory. Neither hook formats files, stages
changes, or checks commit messages. POSIX shell is required; Windows needs a
compatible Git shell.

The checks inspect the current worktree, not an isolated index snapshot or each
pushed ref. Before a reviewed handoff, validate the exact state being handed off.
Hooks can be bypassed, so mirror the chosen gate in CI if enforcement matters.
Formal verification is not enabled by these hooks.

The default gate does not perform security, network, integration or dependency-upgrade checks. Select and configure those for the actual project; an unavailable required check is blocked, never passed.

README change selection unions branch changes since the merge base, index changes,
worktree changes, and visible untracked paths. A staged change is still reported
if the worktree cancels it. Both rename paths count. A changed README remains a
prompt to verify accuracy, not evidence that its content is current.
