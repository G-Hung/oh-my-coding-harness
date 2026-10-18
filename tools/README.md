# Library maintenance checks

These small Python standard-library tools work with Python 3.9+ and Git. They
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
