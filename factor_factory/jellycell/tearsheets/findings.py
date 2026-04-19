"""Findings tearsheet renderer."""

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
    """Render FINDINGS.md for ``project``."""
    return render_template(
        "findings.md.j2",
        project,
        output_path=output_path,
        overwrite=overwrite,
        template_overrides=template_overrides,
    )
