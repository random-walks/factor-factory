"""First-class jellycell integration.

Three pieces of surface area:

- ``cells.setup()`` — per-cell import helper (stable public API;
  originally a workaround for `random-walks/jellycell` #10, fixed
  upstream in 1.3.2).
- ``figure.from_path()`` — path-only ``jc.figure`` convenience wrapper
  (originally a workaround for `random-walks/jellycell` #11, fixed
  upstream in 1.3.2; retained as stable public API).
- ``tearsheets.*`` — five canonical manuscript renderers
  (METHODOLOGY, DIAGNOSTICS_CHECKLIST, FINDINGS, MANUSCRIPT, AUDIT)
  driven by a project's on-disk artifacts.

Plus the ``scaffold`` command under ``notebooks._scaffold``.

All jellycell upstream issues (#10–#15) that motivated the original
``cells`` / ``figure`` shims have shipped upstream (jellycell 1.3.2 →
1.3.5). Our pin floor (``jellycell[server]>=1.4.0``) guarantees every
fix is present. The shims stay — they're stable public API that
insulates downstream callers from jellycell minor-version churn.
"""

from . import notebooks, tearsheets
from .cells import setup
from .figure import from_path

__all__ = ["from_path", "notebooks", "setup", "tearsheets"]
