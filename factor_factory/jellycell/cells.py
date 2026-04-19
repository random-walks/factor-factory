"""``setup()`` — workaround for jellycell #J1 (cache-skip footgun).

Upstream bug filed as `random-walks/jellycell` #10. The docs claim
``# %% tags=["jc.setup"]`` cells are not cached; in practice they are,
and the imports they declare don't survive into subsequent re-executed
cells. This module's ``setup()`` returns the imports as a dict the cell
unpacks locally, sidestepping the cache-scope bug entirely.

Intended usage (canonical pattern enforced by the scaffolded notebooks):

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

    Workaround for the jellycell upstream bug
    (`random-walks/jellycell` #10) where ``# %% tags=["jc.setup"]``
    cells get cached and their imports do not survive into subsequent
    re-executed cells. Calling ``setup()`` from any cell guarantees the
    imports are in scope regardless of cache state.

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
