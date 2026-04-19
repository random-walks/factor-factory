# Architecture

## Directory layout

```
factor_factory/
├── __init__.py                   # re-exports the most-used surface (Panel, TreatmentEvent, ...)
├── tidy/
│   ├── __init__.py
│   ├── socrata.py                # bulk_fetch + cache + dedup; swappable adapter
│   ├── geography.py              # boundary loader, centroids, distance matrices
│   ├── panel.py                  # Panel.from_records(...), period binning, treatment events
│   ├── record_view.py            # lat/lon-preserving companion view
│   └── contracts.py              # pydantic / TypedDict schemas
├── factors/
│   ├── __init__.py
│   ├── volume.py                 # count, rate, growth, level-shifts
│   ├── recurrence.py             # repeat-filer fraction, Gini of filer concentration
│   ├── hhi.py                    # Herfindahl concentration
│   ├── resolution.py             # resolution-rate, median-days, p90 resolution
│   └── reliability.py            # uptime-weighted coverage (subway-access flavor)
├── diagnostics/
│   ├── __init__.py
│   ├── distributions.py          # Jarque-Bera, Shapiro-Wilk, moment diagnostics
│   ├── missingness.py            # per-column + per-unit missingness heatmaps
│   ├── outliers.py               # Cook's distance, DFBETAS, leverage, z-score
│   ├── balance.py                # SMD tables, parallel-trends visuals
│   └── assertions.py             # MultiIndex integrity, period alignment, coverage
├── engines/
│   ├── __init__.py
│   ├── _base.py                  # Protocol + frozen result dataclasses (per family)
│   ├── _registry.py              # EngineRegistry for runtime discovery + extension
│   ├── did/
│   │   ├── __init__.py
│   │   ├── _base.py              # DidEngine Protocol + DidResult
│   │   ├── twfe.py               # linearmodels.PanelOLS adapter
│   │   ├── callaway_santanna.py  # `differences` adapter
│   │   ├── sun_abraham.py
│   │   └── borusyak_jaravel_spiess.py
│   ├── rdd/
│   │   ├── __init__.py
│   │   ├── _base.py              # RddEngine Protocol + RddResult
│   │   ├── rdrobust.py           # canonical rdrobust adapter
│   │   └── local_poly.py         # homegrown for teaching / fallback
│   ├── scm/
│   │   ├── __init__.py
│   │   ├── _base.py
│   │   ├── abadie_original.py
│   │   ├── pysyncon.py
│   │   └── augmented.py          # Ben-Michael-Feller-Rothstein 2021
│   ├── changepoint/              # ruptures (PELT, BinSeg) + bayesloop (Bayesian)
│   ├── stl/                      # statsmodels + sktime MSTL + prophet
│   ├── panel_reg/                # linearmodels + pyfixest
│   ├── inequality/               # theil + decompositions
│   ├── oaxaca_blinder/
│   ├── reporting_bias/           # latent EM with identification-constraint doc
│   └── hawkes/                   # tick + pyhawkes
├── jellycell/
│   ├── __init__.py
│   ├── cells.py                  # setup() helper, workaround for jellycell #J1
│   ├── figure.py                 # from_path() helper, workaround for jellycell #J2
│   ├── tearsheets/
│   │   ├── __init__.py
│   │   ├── methodology.py        # render(project) -> METHODOLOGY.md
│   │   ├── diagnostics.py        # render(project) -> DIAGNOSTICS_CHECKLIST.md
│   │   ├── findings.py           # render(project) -> FINDINGS.md
│   │   ├── manuscript.py         # render(project) -> MANUSCRIPT.md
│   │   └── audit.py              # render(project) -> AUDIT.md
│   ├── notebooks/
│   │   └── _scaffold.py          # implementation of `python -m factor_factory scaffold`
│   └── _templates/               # Jinja2 templates for the manuscript renderers
├── tests/
│   ├── _fixtures/
│   │   ├── synthetic_panels.py   # canonical synthetic panels for engine tests
│   │   └── known_results.py      # expected outputs from each engine on each fixture
│   ├── test_panel_contract.py
│   ├── test_engines/
│   │   ├── test_did_conformance.py   # every DidEngine adapter passes the same contract test
│   │   ├── test_rdd_conformance.py
│   │   └── ...
│   └── test_jellycell_integration.py
└── __main__.py                   # entry point for `python -m factor_factory scaffold`

docs/
├── og_context/                   # original design + spec + plan (this folder)
├── getting-started.md            # ship with v0.1
├── jellycell-integration.md      # ship with v0.1
├── adding-an-engine.md           # ship with v0.2 (first engine fan-out release)
└── reference/                    # ship with v1.0; not before
```

## Core abstraction: the `Panel`

The `Panel` is the central data structure that every layer operates
on. See [`03_specs/panel_contract.md`](03_specs/panel_contract.md)
for the full schema.

In short:
- `MultiIndex(unit_id: str, period: pd.Timestamp)`
- Required columns: `outcome` (the analytic target), one or more
  factor columns
- Optional but framework-aware columns: `treatment` (binary),
  `treated_unit` (binary), `post` (binary), `population` (int)
- Companion `record_view` (optional): per-record DataFrame with
  `(lat, lon, unit_id, period, outcome_i)` rows. Required for
  record-level RDD via rdrobust.

## Protocol pattern: pluggable engines

Every stats method family defines a Protocol + frozen result
dataclass. Engine adapters implement the Protocol:

```python
# factor_factory/engines/did/_base.py
from typing import Protocol
from dataclasses import dataclass

@dataclass(frozen=True)
class DidResult:
    method: str                      # e.g. "callaway_santanna"
    att: float                       # the headline ATT
    se: float
    ci_95: tuple[float, float]
    p_value: float
    n: int
    cohort_atts: dict | None = None  # event-study coefficients, if available
    diagnostics: dict | None = None  # method-specific extras
    meta: dict | None = None         # raw output, for users who want it

class DidEngine(Protocol):
    name: str
    def fit(self,
            panel,
            *,
            outcome: str,
            treatment: str,
            cluster: str | None = None,
            **kwargs) -> DidResult: ...
```

Each engine adapter is a separate module:

```python
# factor_factory/engines/did/twfe.py
from linearmodels.panel import PanelOLS
from ._base import DidEngine, DidResult

class TwfeEngine:
    name = "twfe"
    def fit(self, panel, *, outcome, treatment, cluster=None, **kwargs):
        # ... PanelOLS implementation ...
        return DidResult(method="twfe", att=..., se=..., ...)
```

User-facing dispatch:

```python
# factor_factory/engines/did/__init__.py
from ._registry import EngineRegistry
from .twfe import TwfeEngine
from .callaway_santanna import CallawaySantannaEngine
# ...

_registry = EngineRegistry({
    "twfe": TwfeEngine(),
    "cs": CallawaySantannaEngine(),
    # ...
})

def estimate(panel, *, methods=("twfe",), **kwargs):
    return [_registry[m].fit(panel, **kwargs) for m in methods]
```

The same shape repeats for `rdd/`, `scm/`, `changepoint/`, etc. See
[`03_specs/engine_protocol.md`](03_specs/engine_protocol.md) for
the full pattern with conformance test requirements.

## Optional-deps strategy

Default install:

```bash
pip install factor-factory
```

Gets you: `tidy`, `factors`, `diagnostics`, `jellycell`, plus
the framework scaffolding (`engines._base`, `engines._registry`).
**No engines.** Default install is small + jellycell-ready.

Each engine family is an extra:

```bash
pip install factor-factory[did]            # adds linearmodels + differences
pip install factor-factory[rdd]            # adds rdrobust
pip install factor-factory[scm]            # adds pysyncon
pip install factor-factory[changepoint]    # adds ruptures + bayesloop
pip install factor-factory[stl]            # adds sktime + prophet
pip install factor-factory[panel-reg]      # adds linearmodels + pyfixest
pip install factor-factory[inequality]     # adds inequality
pip install factor-factory[spatial]        # adds esda + libpysal + spreg
pip install factor-factory[reporting-bias]
pip install factor-factory[hawkes]         # adds tick or pyhawkes

pip install factor-factory[all]            # everything
```

Engines that aren't available raise `ImportError` only when called,
not at import time. The registry checks availability lazily.

## Naming + license

- **Package**: `factor-factory` on PyPI, `factor_factory` as the
  module
- **License**: MIT (matching sibling `random-walks` packages)
- **Python**: `>=3.12`
- **Versioning**: `0.x.y` during dev (frequent breaking changes
  allowed); `1.0.0` after Phase 4 settles, then SemVer
- **Repo**: `random-walks/factor-factory`

## Top-level imports

The `__init__.py` re-exports the most common entry points so
notebooks don't need deep import paths:

```python
import factor_factory as ff

panel = ff.Panel.from_records(...)
results = ff.engines.did.estimate(panel, methods=("twfe", "cs"), ...)
ff.diagnostics.standardized_mean_differences(panel, ...)
ff.jellycell.tearsheets.methodology(project="my-showcase")
```

Full top-level surface (re-exports):

```python
# factor_factory/__init__.py
from .tidy import Panel, TreatmentEvent
from . import engines, factors, diagnostics, jellycell
from ._version import __version__
```

## Dependencies

Mandatory (default install):
- `pandas>=2.2`
- `numpy>=2`
- `pydantic>=2`
- `pyarrow>=18` (so `jellycell.api.table` works out of the box —
  jellycell #J4 workaround)
- `jellycell[server]>=1.3,<2`
- `matplotlib>=3.8`
- `seaborn>=0.13`
- `geopandas>=1.0` (for the geography layer)
- `shapely>=2.0`

Optional (per engine family) — see `01_architecture.md` § Optional-deps
above and the per-engine specs in [`03_specs/`](03_specs/).
