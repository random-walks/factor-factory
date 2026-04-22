"""``setup()`` — per-cell import helper for scaffolded notebooks.

Historical note: this helper was originally introduced as a workaround
for a jellycell cache-scope bug (``jc.setup``-tagged cells got cached
and their imports didn't survive re-executed cells), filed as
`random-walks/jellycell` #10. That issue **shipped in jellycell 1.3.2**
(``jc.setup`` cells are never cached). Our pin floor
(``jellycell[server]>=1.4.0``) guarantees the upstream fix.

We keep ``setup()`` as the canonical per-cell import pattern for
scaffolded notebooks: it returns the imports as a dict, giving every
cell a self-contained, reproducible namespace regardless of jellycell
version or cache state. It is stable public API — downstream callers
don't need to track jellycell minor-version churn.

Intended usage (enforced by the scaffolded notebooks):

```python
# %% tags=["jc.load", "name=panel"]
from factor_factory.jellycell.cells import setup
ns = setup(also=("matplotlib.pyplot as plt",))
jc, pd, np, plt, Image = ns["jc"], ns["pd"], ns["np"], ns["plt"], ns["Image"]
```
"""

from __future__ import annotations

import importlib
import re
from typing import Any

_ALSO_PATTERN = re.compile(
    r"^\s*(?P<module>[A-Za-z_][\w.]*)\s*(?:as\s+(?P<alias>[A-Za-z_]\w*))?\s*$"
)


def setup(
    *,
    also: tuple[str, ...] = (),
    jellycell_module: str = "jellycell.api",
) -> dict[str, Any]:
    """Return a dict of imports for unpacking at the top of every cell.

    The canonical per-cell import pattern for scaffolded showcase
    notebooks. Each cell calls ``setup()`` and unpacks the returned
    dict locally, giving every cell a self-contained, reproducible
    namespace — independent of jellycell cache state or version.

    (Historically a workaround for `random-walks/jellycell` #10, fixed
    upstream in jellycell 1.3.2. Retained as stable public API.)

    Parameters
    ----------
    also
        Additional import statements to evaluate, e.g.
        ``("matplotlib.pyplot as plt", "scipy.stats as sps")``. Each
        entry is parsed as ``<module> [as <alias>]``.
    jellycell_module
        Which jellycell module to import as ``jc``. Override only for
        testing.

    Returns
    -------
    dict
        Keys: at minimum ``jc``, ``pd``, ``np``, ``Image``. Plus any
        aliases from ``also``.
    """
    ns: dict[str, Any] = {}

    try:
        ns["jc"] = importlib.import_module(jellycell_module)
    except ImportError as exc:
        raise ImportError(
            f"factor_factory.jellycell.cells.setup() could not import "
            f"'{jellycell_module}'. Is the `jellycell` package installed? "
            "factor-factory ships with `jellycell[server]` as a default dep, "
            "so this is unusual."
        ) from exc

    ns["pd"] = importlib.import_module("pandas")
    ns["np"] = importlib.import_module("numpy")
    try:
        from IPython.display import Image

        ns["Image"] = Image
    except ImportError:  # pragma: no cover
        ns["Image"] = None

    for entry in also:
        match = _ALSO_PATTERN.match(entry)
        if match is None:
            raise ValueError(
                f"Cannot parse `also=` entry {entry!r}. "
                "Expected '<module>' or '<module> as <alias>'."
            )
        module_name = match.group("module")
        alias = match.group("alias") or module_name.split(".")[0]
        ns[alias] = importlib.import_module(module_name)

    return ns


__all__ = ["setup"]
