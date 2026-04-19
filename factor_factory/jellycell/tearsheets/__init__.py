"""Five canonical manuscript renderers.

Each ``render(project, *, output_path=None, overwrite=False,
template_overrides=None) -> Path`` writes the named manuscript file
under ``<project>/manuscripts/``. The ``<!-- tearsheet:freeze -->``
marker in each template delineates a regenerated section (above) from
a preserved section (below) — re-running with ``overwrite=True`` only
rewrites the regenerated section.
"""

from .audit import render as audit
from .diagnostics import render as diagnostics
from .findings import render as findings
from .manuscript import render as manuscript
from .methodology import render as methodology

__all__ = ["audit", "diagnostics", "findings", "manuscript", "methodology"]
