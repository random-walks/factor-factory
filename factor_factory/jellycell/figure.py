"""``from_path()`` — path-only ``jc.figure`` convenience wrapper.

Historical note: this helper was originally introduced as a workaround
for upstream jellycell's lack of a path-only ``jc.figure`` API, filed
as `random-walks/jellycell` #11. That issue **shipped in jellycell
1.3.2** and ``jellycell.api.figure(path, ...)`` now works without a
mandatory ``fig=`` argument. Our pin floor (``jellycell[server]>=1.3.5``)
guarantees the upstream fix is present.

We keep ``from_path()`` as a stable public API surface so downstream
callers don't have to track jellycell minor-version churn. It is a
thin wrapper: register the artifact and emit the IPython display.
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
    ``IPython.display.Image(path)`` inside a ``tags=["jc.figure"]``
    cell.

    Returns the displayable object so the cell renders the image.
    """
    path_obj = Path(path)
    if not path_obj.exists():
        raise FileNotFoundError(f"figure path does not exist: {path}")

    artifact_name = name or path_obj.stem

    try:
        jc = importlib.import_module("jellycell.api")
    except ImportError:  # pragma: no cover - default install carries jellycell
        jc = None

    if jc is not None:
        register = getattr(jc, "register_figure", None) or getattr(jc, "figure", None)
        if register is not None:
            # Be tolerant of older jellycell signatures that required ``fig=``;
            # our pin floor (1.3.5) ships the path-only API, but keep the
            # suppress so the shim stays robust if a caller overrides the pin.
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
