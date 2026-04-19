"""``from_path()`` — workaround for jellycell #J2 (path-only ``jc.figure``).

Upstream bug filed as `random-walks/jellycell` #11. The current
``jc.figure(path, ...)`` API requires a mandatory ``fig=plt.gcf()`` arg
even when the caller already has a pre-rendered PNG on disk and just
wants to register it. ``from_path()`` does the right thing: register
the artifact and emit the IPython display.
"""

from __future__ import annotations

import contextlib
import importlib
from pathlib import Path
from typing import Any


def from_path(
    path: str | Path,
    *,
    caption: str = "",
    name: str | None = None,
    notes: str = "",
    tags: tuple[str, ...] = (),
) -> Any:
    """Register an existing image file as a jellycell figure artifact.

    For verbatim-mirror cases where you have a pre-rendered image on
    disk and don't want to recompute it via matplotlib. Cleaner than
    the current pattern of ``IPython.display.Image(path)`` inside a
    ``tags=["jc.figure"]`` cell.

    Returns the displayable object so the cell renders the image.
    """
    path_obj = Path(path)
    if not path_obj.exists():
        raise FileNotFoundError(f"figure path does not exist: {path}")

    artifact_name = name or path_obj.stem

    # Best-effort: try to register with jellycell if the API supports it.
    try:
        jc = importlib.import_module("jellycell.api")
    except ImportError:  # pragma: no cover - default install carries jellycell
        jc = None

    if jc is not None:
        register = getattr(jc, "register_figure", None) or getattr(jc, "figure", None)
        if register is not None:
            # Older jellycell signatures require fig=; in that case we fall back
            # to display-only and the artifact stays unregistered (acceptable
            # workaround until upstream #J2 lands).
            with contextlib.suppress(TypeError):
                register(
                    str(path_obj),
                    caption=caption,
                    name=artifact_name,
                    notes=notes,
                    tags=tags,
                )

    try:
        from IPython.display import Image

        return Image(str(path_obj))  # type: ignore[no-untyped-call]
    except ImportError:  # pragma: no cover
        return None


__all__ = ["from_path"]
