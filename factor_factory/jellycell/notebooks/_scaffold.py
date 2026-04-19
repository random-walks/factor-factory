"""Implementation of ``python -m factor_factory scaffold <name>``."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from ..tearsheets import audit, diagnostics, findings, manuscript, methodology

_TEMPLATE_DIR = Path(__file__).resolve().parent / "_templates"

# Files copied verbatim with __PROJECT__ substituted.
_FILES_TO_COPY = (
    ("01_load.py", "notebooks/01_load.py"),
    ("_helpers.py", "notebooks/_helpers.py"),
    ("jellycell.toml", "jellycell.toml"),
    ("data_README.md", "data/README.md"),
)

_PROJECT_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9-]{1,49}$")


def scaffold(name: str, *, into: Path | None = None) -> Path:
    """Create ``<into>/<name>/`` populated with a runnable showcase skeleton.

    Returns the project directory path.
    """
    if not _PROJECT_NAME_PATTERN.match(name):
        raise ValueError(
            f"Invalid project name {name!r}. "
            "Use lowercase letters, digits, and hyphens; start with a letter; "
            "max 50 characters."
        )

    base = (into or Path.cwd()).resolve()
    project_dir = base / name
    if project_dir.exists():
        raise FileExistsError(f"{project_dir} already exists. Pick a different name or remove it.")

    for sub in ("notebooks", "data", "artifacts", "artifacts/figures", "manuscripts", "site"):
        (project_dir / sub).mkdir(parents=True, exist_ok=True)

    for src_name, rel_dest in _FILES_TO_COPY:
        src = _TEMPLATE_DIR / src_name
        body = src.read_text().replace("__PROJECT__", name)
        dest = project_dir / rel_dest
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(body)

    # Render starter manuscripts so the four canonical files exist
    # immediately after scaffolding (before the notebook has even run).
    methodology(name, output_path=project_dir / "manuscripts" / "METHODOLOGY.md", overwrite=True)
    diagnostics(
        name, output_path=project_dir / "manuscripts" / "DIAGNOSTICS_CHECKLIST.md", overwrite=True
    )
    findings(name, output_path=project_dir / "manuscripts" / "FINDINGS.md", overwrite=True)
    manuscript(name, output_path=project_dir / "manuscripts" / "MANUSCRIPT.md", overwrite=True)
    audit(name, output_path=project_dir / "manuscripts" / "AUDIT.md", overwrite=True)

    # Detect a parent AGENTS.md (per the spec).
    agents_path = _walk_up_for("AGENTS.md", start=base)
    if agents_path is not None:
        print(
            f"✓ agent guide detected at {agents_path} — Cursor / Codex / "
            "Copilot / Claude Code already covered."
        )

    return project_dir


def _walk_up_for(filename: str, *, start: Path, max_depth: int = 6) -> Path | None:
    cur = start
    for _ in range(max_depth):
        candidate = cur / filename
        if candidate.exists():
            return candidate
        if cur.parent == cur:
            break
        cur = cur.parent
    return None


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m factor_factory scaffold",
        description=(
            "Generate a working factor-factory + jellycell showcase skeleton. "
            "Drops a notebook stub, jellycell.toml, manuscripts, and the "
            "canonical data/artifacts directories."
        ),
    )
    parser.add_argument("name", help="Project name (lowercase, hyphens allowed).")
    parser.add_argument(
        "--into",
        type=Path,
        default=None,
        help="Parent directory to create the project under (default: cwd).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)
    out = scaffold(args.name, into=args.into)
    print(f"✓ scaffolded {args.name} at {out}")
    print("Next:")
    print(f"  cd {out}")
    print("  uv run --with 'factor-factory[did]' jellycell run notebooks/01_load.py")
    return 0


__all__ = ["main", "scaffold", "build_argument_parser"]
