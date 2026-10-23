# Maintaining the library

The library uses the same feedback loop it recommends: an agent receives a check
failure, fixes the cause, reruns the check, and retries the Git operation. Files
are not formatted, fixed, or staged silently. The checks are shared commands;
hooks are the integration points, not a second implementation of the rules.

## One-time local setup

Use Python 3.12+, uv 0.13.4+, Node 24.22.1, npm, and Git 2.38+. GitHub pre-push checks also
need an authenticated GitHub CLI (`gh`) with `api --paginate --slurp` support.
From the library root:

```sh
uv sync --locked
uv sync --project kits/python --locked
npm --prefix kits/typescript ci
uv run --frozen --offline --no-sync python tools/check.py
uv run --frozen --offline --no-sync python tools/install_hooks.py
```

The first three commands install the pinned development environments. Hook setup
is an explicit local action, not a clone-time side effect. The installer sets
`core.hooksPath` to `.githooks` and refuses to replace another hook owner or active
unmanaged hooks. Inspect and integrate existing hooks deliberately instead of
forcing setup. Verify the result with `git config --show-origin --get core.hooksPath`.

Git configuration can be shared across linked worktrees. Each worktree still needs
the tracked hook files and its own installed dependencies. Repeat prerequisites
when a lockfile changes. Dependency commands use offline, no-sync mode: hooks do
not install packages, audit registries, or run Java/TLC setup. Pre-push fetches the
remote integration and peer refs into a disposable repository for the merge check below.

## Certificate trust maintenance

The [October 2026 Python advisory](https://discuss.python.org/t/information-for-python-users-regarding-emudhra-emsign-ca-certificate-security-incident/109576)
requires uv 0.13.4+, pip 26.2.2+, and certifi 2026.10.19+ where installed.
Both uv projects enforce the uv minimum. The Python kit constrains virtualenv to
21.14.12+ because it bundles patched pip for the supported Python versions.
The CI workflow pins patched uv and Node releases. Review these pins when new
security releases appear; a package lockfile does not update its package manager.

Update tools through their installation manager. For Homebrew-managed uv, use
`brew upgrade uv` when an update is needed. Use `uv self update` only for a
standalone uv installation. Check `uv --version` before fetching dependencies.
Do not disable TLS verification or switch trust stores without checking them.

Keep these uv environments pip-free. `python -m venv` or `ensurepip` can seed an
older pip from the base interpreter, even when uv is patched. If an environment
needs pip, use the advisory's checksum-pinned bootstrap procedure before its
first package download. Updating a separate certifi package or the OS trust store
does not replace pip's vendored certificate bundle. Inspect pip and certifi in
each environment that uses them; updating one environment does not update others.

Keep OS certificates and each tool's bundled trust store current. Rebuild applicable
container images with updated base images and layer caching disabled. This library
has no checked-in Docker image to rebuild. A patched uv does not establish that
other tools, other environments, or the system trust store are patched.

## Which check runs when

| Entry point | Blocking checks | Why here |
| --- | --- | --- |
| pre-commit | Root lockfile, Python formatting/lint/types, local Markdown paths, portability, Node syntax, Python kit static checks, TypeScript kit lint/types/links | Catch inexpensive errors before a commit exists. File-size prompts remain advisory. |
| commit-msg | `type: description` or `type(scope): description`, optional `!` | Keep intent visible in history without controlling the body or description language. |
| pre-push | Remote default-branch and open GitHub PR merge checks, then the full gate, including maintenance/hook regression tests, standalone checks' tests, formal-runner and executable-cache tests, and both kits' full gates | Detect merge conflicts and exercise behavior before sharing committed work. It does not run TLC model exploration. |

The root Python environment checks maintenance scripts and Python examples. Each
kit retains its own pinned dependencies and configuration. TypeScript typechecking
covers the TypeScript kit; standalone JavaScript gets syntax and behavioral tests.
The formal TypeScript cache example runs with Node's TypeScript support; this gate
does not claim static type coverage for that example. README/file-size signals do
not prove documentation accuracy or architecture quality. Current library link
checks cover local inline paths; the Python kit also supports reference links.

The pre-commit runner exports the index into a disposable Git checkout, runs the
static gate there, then removes it. An unstaged repair cannot hide a staged failure.
The pre-push runner checks each object supplied by Git, including multiple refs,
and skips deletions. Uncommitted repairs and unrelated HEAD commits cannot hide a
bad pushed revision. Empty stdin during a direct manual invocation checks HEAD.
A revision without the gate is blocked rather than treated as validated.

For branch pushes, the runner discovers the remote default branch and fetches it
into a temporary bare repository using the checkout's effective URL, SSH, HTTP,
and credential settings. Git merge-tree checks each proposed branch against that
snapshot and, when included in the push, the proposed default-branch
revision. Conflicts block the push without changing local refs, the index, or the
working tree. Remote access failures and a populated remote with no default HEAD
also block the check; fix the reported cause and retry. Empty remotes have no
integration base yet. Tags and deletions do not need a merge check. Manual runs
without Git's remote arguments check local trees only.

For standard github.com push URLs, the same checker queries every open PR targeting
the default branch, including drafts, bots, and forks. It requires authenticated
`gh` with `api --paginate --slurp`. It fetches PR heads into the same temporary
repository and checks merge conflicts locally. The target's own PR is excluded
only when source repository and pushed destination branch both match. Shared-file
overlap without a conflict is informational. Query or fetch failures block;
each remote operation has a 120-second timeout, with no retries or cache.

Other hosts use Git-only checks and do not require `gh`. Use the standalone
[remote conflict check](../tools/README.md#remote-conflict-check) for an explicit
integration branch, additional peer branches, or a GitHub Enterprise repository.
No PR code runs. CI must check integrated behavior; Git still enforces its normal
push rules if the remote changes after this snapshot.

Both runners reuse installed dependency environments, not their source files, from
the originating checkout. Update those environments to match the relevant lockfiles
before running checks. Dependencies and their caches are not isolated security
sandboxes. Source snapshots are temporary. Each check prints one progress/result line with
elapsed time. Warnings and file-size review prompts remain visible (up to three
short messages per check); full output is retained in a separate temporary log
directory whenever a check warns, fails, or cannot start. Missing top-level tools
are reported directly before checks start. Failures
show the rerun command and the last 60 lines, capped at 12,000 characters. Logs
survive snapshot cleanup; remove them after investigation. Clean runs delete their
logs. Negative-test error output stays in the log rather than looking like a
failed gate. This changes presentation only, not check selection or exit status.
The full gate itself stays offline; remote access belongs to the pre-push merge
check. Git still needs task authorization for an actual push.

## Fix the reported cause

```sh
# Same static gate as pre-commit, against your working tree while fixing:
uv run --frozen --offline --no-sync python tools/check.py --static-only
# Full local gate, including tests:
uv run --frozen --offline --no-sync python tools/check.py
# Formatting is an explicit editing action:
uv run --frozen --offline --no-sync ruff format tools examples
# Retry after reviewing and staging the actual fixes:
git add <selected-files>
git commit -m "fix(checks): handle the reported case"
```

Do not bypass hooks or weaken checks to get a commit through. Missing prerequisites
are failures to resolve, not passes. Investigate the first failing command; the
gate stops there to keep the feedback useful. Do not stage unrelated changes.

Accepted message examples: `feat(hooks): add validation`, `fix: handle missing input`,
`docs: 更新使用說明`, and `refactor(api)!: change the contract`. Allowed types are
feat, fix, docs, style, refactor, perf, test, build, ci, chore, and revert. Scope is
optional; there is no imposed subject-case or body format. A missing type, missing
description, or malformed prefix blocks the commit. Automatic merge/revert/fixup
subjects are not exempt; provide a conforming subject when using those operations.
The old initialization commit is historical and is not rewritten by these hooks.

## Evidence and adoption elsewhere

`tools/tests/test_git_hooks.py` drives actual Git commits and pushes against a
throwaway local bare repository. It verifies rejected messages, scoped prefixes,
staged failures hidden by unstaged fixes, successful repairs, exact pushed-object
checks, remote merge conflicts, multi-ref integration, and protection of existing hooks.
Its tiny fixture gate avoids recursively
running this same test suite. The real full gate separately checks the actual code.
The tests never push this library or contact a hosted repository.

The [adoption guide](adoption.md) still applies to other projects. Preserve their
hook manager and commands. The portable message checker is
`tools/check_commit_message.py` (Python standard library); copy its policy only if
the user wants it. The snapshot runners depend on each other and this library's
layout, gate, and dependency paths; they are an integration example to adapt, not
standalone scripts to paste into arbitrary projects. Read their complete context.
No generic adoption approval permits replacing AGENTS.md or enabling hooks.

## GitHub automation

The CI workflow installs the locked root Python, Python kit, and TypeScript kit
environments, then runs the same full maintenance gate. It runs on pull requests,
pushes to `master`, and manual dispatch. It does not install hooks or run the
remote pre-push merge check. Keep workflow branch filters and the README badge
aligned if the default branch changes.

CodeQL scans Python and JavaScript/TypeScript on pull requests, default-branch
pushes, weekly schedules, and manual dispatch. It reports potential security
defects in GitHub's code scanning results. Review alerts and fix valid findings;
do not treat a completed analysis as proof that the code has no vulnerabilities.
CodeQL uses advanced setup from the checked-in workflow. Do not enable a duplicate
CodeQL default setup.

Dependabot checks both uv projects, the TypeScript kit, and GitHub Actions weekly.
Each configuration groups minor and patch version updates and permits at most
three open version-update pull requests. Major updates remain separate. Security
update pull requests use GitHub's separate security-update policy and limits.
Review manifest and lockfile changes together. Require passing CI before merging;
no workflow enables automatic merging. The formal TypeScript example has no
package dependencies and needs no separate npm update entry.

TypeScript 7.x version updates are temporarily excluded because the kit's Jest
transformer and ESLint parser do not support that compiler version. Keep other
updates enabled. Remove the exclusion when both tools declare compatible peer
ranges, then verify a normal `npm ci` and the full gate. See the
[TypeScript kit](../kits/typescript/README.md#commands) for the current constraints.

Actions use full commit hashes with version comments for Dependabot. CI uses
read-only repository access. Only the CodeQL reporting job requests
`security-events: write`. Pull request workflows use `pull_request` and do not
receive repository secrets. Retain these limits when changing the workflows.

The local gate remains offline. Dependency installation and hosted scanners use
the network. Standard GitHub-hosted runners are free for public repositories;
larger runners and storage above the included allowance can incur charges.
These workflows use standard Ubuntu runners, disable uv caching, and do not add
artifact uploads. See [GitHub Actions billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions).

### GitHub security activation

The checked-in configuration does not prove that hosted services are active.
After the files reach the default branch, a repository administrator must:

1. Verify that the repository is public before relying on public-repository free
   security features. This change does not change repository visibility.
2. Enable or verify Dependabot alerts and Dependabot security updates. Check the
   dependency graph for both Python lockfiles and the npm lockfile. Investigate
   unsupported or missing dependency data before claiming vulnerability coverage.
3. Enable or verify secret scanning and repository push protection.
4. Enable private vulnerability reporting. Confirm that **Report a vulnerability**
   is available in the Security tab.
5. Confirm that Actions can run the pinned workflows. Confirm the first CI run
   passes and both CodeQL languages report results without upload errors.
6. Verify the README CI badge links to the default branch's run. Before the first
   run on that branch, its status is not validation evidence.

Use GitHub's [repository security settings guide](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-security-and-analysis-settings-for-your-repository).
Settings changes and first hosted runs remain pending until verified on GitHub.
Do not dispatch workflows or change repository settings as part of a local check.
