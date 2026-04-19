"""Audit tearsheet renderer (what's strong / what's gappy)."""

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
    """Render AUDIT.md for ``project``."""
    return render_template(
        "audit.md.j2",
        project,
        output_path=output_path,
        overwrite=overwrite,
        template_overrides=template_overrides,
    )
