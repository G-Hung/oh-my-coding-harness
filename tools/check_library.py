from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CHECKS = (
    ("repository portability", "check_portability.py"),
    ("Markdown links", "check_markdown_links.py"),
)


def main() -> int:
    failed: list[str] = []
    for name, script in CHECKS:
        print(f"Checking {name}", flush=True)
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools" / script)], cwd=ROOT, check=False
        )
        if result.returncode != 0:
            failed.append(name)

    if failed:
        print(f"Repository checks failed: {', '.join(failed)}")
        return 1
    print("All repository checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
