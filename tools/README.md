# Library maintenance checks

The integrated [maintenance guide](../docs/maintenance.md) explains setup,
pre-commit, commit-msg, pre-push, and the agent fix/retry loop.
`check.py` runs static checks or the full gate; `git_gate.py` exports exact trees
for `pre_commit.py` and `pre_push.py`. `install_hooks.py` enables the tracked
hooks only on explicit request. `check_commit_message.py` checks the subject
without constraining the body. Hook dispatch is tested in disposable Git repos.

## Remote conflict check

`check_remote_conflicts.py` checks committed changes against a fresh remote
integration branch, selected peer branches, and open GitHub PRs targeting that
integration branch. Copy this one file; it uses Python 3.9+ and Git 2.38+.
GitHub checks also require an authenticated `gh` CLI with `api --paginate --slurp`.

```sh
python3 tools/check_remote_conflicts.py --remote origin
python3 tools/check_remote_conflicts.py --remote origin --target feature --base main --peer other-feature
python3 tools/check_remote_conflicts.py --remote origin --github-repo git.example/owner/repo
```

`--remote` accepts a remote name or push URL; `--target` defaults to HEAD and
`--base` defaults to the remote HEAD branch. Repeat `--peer` for additional remote
branches. Standard github.com HTTPS, SSH, and SCP push URLs enable PR discovery
automatically. Use `--github-repo OWNER/REPO` or `HOST/OWNER/REPO` for an alias or
GitHub Enterprise. Other remotes need no `gh` and use Git branch checks only.

The checker queries all open PR pages, including drafts, bots, and forks. It
excludes a target's own PR only when source repository and destination branch
both match. The hook supplies the actual pushed destination; the standalone
command uses the selected local branch name. Detached targets exclude no PRs.
Each PR head is fetched and compared locally. Merge conflicts block; shared-file
overlap without a conflict is informational. Diagnostics name the PR or branch
and affected files. No PR code runs, and local refs and worktrees remain untouched.

Each discovery, query, and fetch has a 120-second timeout. Missing authentication,
incomplete results, unavailable refs, and changed PR heads fail the check; rerun
after resolving the cause. Checks do not retry or cache results. They check Git
merge compatibility; CI checks the integrated behavior.

## Portable documentation helpers

These helpers use the Python standard library and work with Python 3.9+ and Git. They
check tracked and untracked files while respecting Git ignore rules. They do
not install anything, stage files, or contact external services.

```sh
python3 tools/check_library.py
python3 -m unittest discover -s tools/tests -v
```

`check_library.py` runs both helpers and propagates failures:

- `check_markdown_inline_links.py` checks local inline Markdown path links, excluding
  code blocks and inline code. It rejects missing or outside-repository targets.
  It does not check anchors, reference-style links, or remote availability.
- `check_portability.py` spots machine-specific home-directory paths and file
  URLs in text, including TLA+ modules and configurations. Diagnostics report
  locations without repeating matched values.
  Use `portability-check: ignore` on a deliberate example only. This is a
  portability check, not a credential scanner or comprehensive privacy audit.

These helpers can also be copied together into another documentation repository
under `tools/`. Review file extensions and intentional exclusions before using
them. The stack kits carry their own source/documentation configuration and do
not depend on these files.
