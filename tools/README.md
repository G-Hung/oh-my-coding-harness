# Library maintenance checks

The integrated [maintenance guide](../docs/maintenance.md) explains setup,
pre-commit, commit-msg, pre-push, and the agent fix/retry loop.
`check.py` runs static checks or the full gate; `git_gate.py` exports exact trees
for `pre_commit.py` and `pre_push.py`. `install_hooks.py` enables the tracked
hooks only on explicit request. `check_commit_message.py` checks the subject
without constraining the body. Hook dispatch is tested in disposable Git repos.

## Portable documentation helpers

The three helpers below are Python standard-library tools work with Python 3.9+ and Git. They
check tracked and untracked files while respecting Git ignore rules. They do
not install anything, stage files, or contact external services.

```sh
python3 tools/check_library.py
python3 -m unittest discover -s tools/tests -v
```

`check_library.py` runs both helpers and propagates failures:

- `check_markdown_links.py` checks local inline Markdown path links, excluding
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
