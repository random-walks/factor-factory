"""Manuscript stub renderer (long-form, mostly hand-authored after first run)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ._render import render_template


def render(
    project: str,
    *,
    output_path: Path | None = None,
    overwrite: bool = False,
    template_overrides: dict[str, Any] | None = None,
) -> Path:
    """Render MANUSCRIPT.md for ``project``.

    First run produces a stub; subsequent runs only regenerate the
    section above the ``<!-- tearsheet:freeze -->`` marker.
    """
    return render_template(
        "manuscript.md.j2",
        project,
        output_path=output_path,
        overwrite=overwrite,
        template_overrides=template_overrides,
    )
