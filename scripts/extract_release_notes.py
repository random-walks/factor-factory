#!/usr/bin/env python3
"""Pull the [vX.Y.Z] block out of CHANGELOG.md and print it to stdout.

Used by .github/workflows/release.yml to populate the GitHub Release body
without duplicating prose from the CHANGELOG.

Usage:
    python scripts/extract_release_notes.py 1.2.3
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


def extract(changelog: str, version: str) -> str:
    """Return the body of the `## [<version>] — ...` section."""
    pattern = re.compile(
        rf"^##\s*\[{re.escape(version)}\].*?$(.*?)(?=^##\s*\[|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(changelog)
    if not match:
        raise SystemExit(
            f"error: no section found for version [{version}] in CHANGELOG.md"
        )
    return match.group(1).strip()


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: extract_release_notes.py <version>")
    version = sys.argv[1]
    changelog_path = Path(__file__).parent.parent / "CHANGELOG.md"
    changelog = changelog_path.read_text(encoding="utf-8")
    print(extract(changelog, version))


if __name__ == "__main__":
    main()
