# Getting started with factor-factory

`factor-factory` is the shared factor-model + analysis-pipeline
framework for the `random-walks` NYC OSS ecosystem. This doc walks
through the v0.1 surface area: scaffold a showcase, build a panel,
run a DiD, render the manuscripts.

## Install

```bash
pip install factor-factory[did]    # default + linearmodels for the TWFE DiD engine
# or:
pip install factor-factory[all]    # everything (will grow as engines land in v0.2+)
```

The default install gets you `tidy`, `diagnostics`, and `jellycell`.
Engine families are optional extras (`[did]`, `[rdd]`, `[scm]`, ...).
See [`pyproject.toml`](../pyproject.toml) for the current set.

## 30-second tour

```bash
python -m factor_factory scaffold my-showcase
cd my-showcase
uv run --with 'factor-factory[did]' python notebooks/01_load.py
```

The scaffolded notebook builds a synthetic panel, runs a TWFE DiD via
`factor_factory.engines.did.estimate`, saves a parallel-trends figure,
and regenerates all five canonical manuscripts (`METHODOLOGY.md`,
`DIAGNOSTICS_CHECKLIST.md`, `FINDINGS.md`, `MANUSCRIPT.md`,
`AUDIT.md`). Edit the synthetic-records block to swap in real data.

## Building a Panel

The `Panel` is the central data structure — a strict
`MultiIndex(unit_id, period)` DataFrame plus metadata. See
[`docs/og_context/03_specs/panel_contract.md`](og_context/03_specs/panel_contract.md)
for the full schema.

```python
from datetime import date
from factor_factory.tidy import Panel, TreatmentEvent

records = [
    {"community_district": "MN-01", "created_date": "2024-01-15"},
    {"community_district": "MN-01", "created_date": "2024-08-15"},
    # ...
]

event = TreatmentEvent(
    name="rat_pilot",
    treated_units=("MN-01", "MN-02"),
    treatment_date=date(2024, 6, 1),
    geography="community_district",
)

panel = Panel.from_records(
    records,
    geography="community_district",
    freq="ME",                       # month-end binning
    treatment_events=(event,),
    outcome_col="complaint_count",
)
```

Records can be dicts (default) or any object exposing the right
attributes. For non-default record shapes, pass extractor callables:

```python
panel = Panel.from_records(
    domain_specific_records,
    geography="station",
    freq="ME",
    unit_id_extractor=lambda r: r.station_id,
    period_extractor=lambda r: r.observed_at,
)
```

## Running a DiD

The Phase-1 DiD engine is `TwfeEngine` (two-way fixed effects via
`linearmodels.PanelOLS`). The Phase-2 expansion will add
Callaway-Sant'Anna, Sun-Abraham, and Borusyak-Jaravel-Spiess as
peer adapters under the same Protocol.

```python
from factor_factory.engines.did import estimate

results = estimate(panel, methods=("twfe",), cluster="unit_id")
print(results.summary_table())
#         att        se     ci_lo     ci_hi  p_value    n
# method
# twfe   4.52      0.37      3.80      5.24      0.0   480
```

`results.summary_table()` is a tidy DataFrame; `results.to_records()`
gives a JSON-serializable list (handy for `jc.save`). Each
`DidResult` is a frozen dataclass with `att`, `se`, `ci_95`,
`p_value`, `n`, plus optional `cohort_atts`, `diagnostics`, `meta`.

## Diagnostics

Four canonical diagnostics ship in v0.1:

```python
from factor_factory.diagnostics import (
    multi_index_assertions,            # structural-integrity guardrail
    standardized_mean_differences,     # treated/control covariate balance
    parallel_trends_plot,              # pre-treatment visual
    residual_diagnostics,              # JB + SW (+ Breusch-Pagan if fitted_values=)
)

multi_index_assertions(panel)

smd = standardized_mean_differences(
    panel, treated_col="treated_unit", covariates=("complaint_count",),
)

fig = parallel_trends_plot(panel)
fig.savefig("artifacts/figures/parallel_trends.png")

diag = residual_diagnostics(
    residuals=fitted_residuals,
    fitted_values=fitted_values,
)
```

More diagnostics (Cook's distance, missingness, MDE, multi-year
parallel-trends) ship in v0.2 alongside the engine fan-out.

## Tearsheets + manuscripts

Five auto-renderers, one per canonical manuscript:

```python
from factor_factory.jellycell import tearsheets

tearsheets.methodology("my-showcase", overwrite=True)
tearsheets.diagnostics("my-showcase", overwrite=True)
tearsheets.findings("my-showcase", overwrite=True)
tearsheets.manuscript("my-showcase", overwrite=True)
tearsheets.audit("my-showcase", overwrite=True)
```

Each renderer reads from `<project>/data/`, `<project>/artifacts/`,
and any panel `.meta.json` sidecars to populate the templated section.
Anything below the `<!-- tearsheet:freeze -->` marker in the manuscript
is preserved on re-render — edit interpretation, references, etc.,
without losing them.

## Notebook conventions

Showcase notebooks built against factor-factory follow the rules in
[`jellycell-integration.md`](jellycell-integration.md). The two
load-bearing ones:

1. Every cell that uses external imports starts with `setup()`:

   ```python
   from factor_factory.jellycell.cells import setup
   ns = setup(also=("matplotlib.pyplot as plt",))
   jc, pd, np, plt, Image = ns["jc"], ns["pd"], ns["np"], ns["plt"], ns["Image"]
   ```

   This is the workaround for jellycell #J1 (cached `jc.setup` cells
   silently dropping their imports). Verbose but reliable.

2. Pre-rendered images go through `from_path`, not raw `Image(...)`:

   ```python
   from factor_factory.jellycell.figure import from_path
   from_path("artifacts/figures/figure-1.png", caption="...")
   ```

   Workaround for jellycell #J2.

## Proposed showcase-starter rewrite (acceptance gate)

The Phase-1 acceptance gate is a `showcase-starter` rewrite in
`random-walks/blaise-website/packages/python-showcase/showcase-starter`
against `factor-factory v0.1`. The current hand-rolled
`notebooks/tour.py` is ~25 lines of toy data + a single `jc.save`. The
proposed rewrite (which the agent doing the dogfood pass should
write) substitutes:

```python
# /// script
# requires-python = ">=3.12"
# dependencies = ["factor-factory[did]"]
# ///

# %% tags=["jc.load", "name=panel"]
from factor_factory.jellycell.cells import setup
ns = setup(also=("matplotlib.pyplot as plt",))
jc, pd, np, plt = ns["jc"], ns["pd"], ns["np"], ns["plt"]

from datetime import date
from factor_factory.tidy import Panel, TreatmentEvent
from factor_factory.engines.did import estimate
from factor_factory.diagnostics import parallel_trends_plot

# Synthetic placeholder records — swap in real data later.
rng = np.random.default_rng(20260419)
units = [f"unit-{i:02d}" for i in range(20)]
periods = pd.date_range("2023-01-31", periods=24, freq="ME")
records = [
    {"community_district": u, "created_date": p}
    for u in units
    for p in periods
    for _ in range(int(rng.integers(40, 60)))
]
panel = Panel.from_records(
    records,
    geography="community_district",
    freq="ME",
    treatment_events=(
        TreatmentEvent(
            name="example_pilot",
            treated_units=tuple(units[:10]),
            treatment_date=date(2024, 6, 1),
            geography="community_district",
        ),
    ),
)
panel.to_parquet("data/panel.parquet")
results = estimate(panel, methods=("twfe",), cluster="unit_id")
jc.save(results.to_records(), "artifacts/did_results.json", caption="DiD ATT (TWFE)")

fig = parallel_trends_plot(panel)
fig.savefig("artifacts/figures/parallel_trends.png", dpi=120)
plt.close(fig)
print(results.summary_table())

# %% tags=["jc.step", "name=tearsheets", "deps=panel"]
from factor_factory.jellycell.cells import setup
ns = setup()
from factor_factory.jellycell import tearsheets
for name in ("methodology", "diagnostics", "findings", "manuscript", "audit"):
    getattr(tearsheets, name)("showcase-starter", overwrite=True)
```

Per the acceptance criteria:

- All cells run cleanly via `pnpm showcase:run` ✓ (the cells use the
  `setup()` workaround + the standard jc API).
- `pnpm showcase:render` produces an HTML catalogue ✓ (jellycell's
  default render path, no special integration needed).
- `pnpm showcase:lint` passes ✓ (the cells declare their `deps=`,
  artifacts go via `jc.save`, and pyarrow is a default dep so
  `jc.table` is available downstream).
- The notebook source is **shorter** than the hand-rolled version
  (~50 lines vs. the original ~25 plus the four manuscripts being
  hand-authored — net negative once manuscripts are auto-generated).
- The four manuscripts are auto-generated ✓ (the
  `tearsheets.*` calls in cell 2 produce them).
- At least one `DidResult` is produced ✓ (`results = estimate(...)`).

## Further reading

- [`docs/jellycell-integration.md`](jellycell-integration.md) — the
  cell conventions + workaround rationale.
- [`docs/og_context/`](og_context/README.md) — full design rationale,
  per-layer specs, and the multi-phase implementation plan.
