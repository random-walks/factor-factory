# Getting started with factor-factory

`factor-factory` is a domain-agnostic factor-model + analysis-pipeline
framework. The same `Panel` shape hosts NYC-civic data, finance event
studies, multi-arm RCTs, agronomic dose-response trials, and chemistry
assays. This doc walks through the v0.1 surface area: scaffold a
showcase, build a panel, run a DiD, render the manuscripts.

For the full data-shape contract, see
[`docs/design-contracts.md`](design-contracts.md).

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
[`docs/design-contracts.md`](design-contracts.md) for the full schema.

### Civic / DiD style

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
    dimension="community_district",
)

panel = Panel.from_records(
    records,
    dimension="community_district",
    freq="ME",                       # month-end binning
    treatment_events=(event,),
    outcome_col="complaint_count",
)
```

### Finance event study

Daily ticker × business day, multi-outcome (returns + abnormal returns),
weighted by market cap. Note `freq=None` because business days don't
fit into pandas' month-end / quarter-end rebinning:

```python
from datetime import date
from factor_factory.tidy import Panel, PanelMetadata, Provenance, TreatmentEvent

# Build the wide DataFrame yourself when you have multiple outcomes.
metadata = PanelMetadata(
    outcome_cols=("returns", "abnormal_returns"),
    period_kind="timestamp",
    freq=None,
    dimension="ticker",
    treatment_events=(
        TreatmentEvent(
            name="earnings_event",
            treated_units=tuple(treated_tickers),
            treatment_date=date(2024, 7, 15),
            dimension="ticker",
        ),
    ),
    weights_col="market_cap_mm",
    provenance=Provenance(
        data_source="bloomberg.com/api/v3",
        license="proprietary",
        citation="Author, Year",
    ),
)
panel = Panel(prebuilt_df, metadata)
```

### Multi-arm RCT

Three arms (placebo, low_dose, high_dose); categorical treatments
produce per-event `arm__<name>` columns:

```python
events = (
    TreatmentEvent(
        name="low_dose",
        treated_units=tuple(low_dose_patient_ids),
        treatment_date=enrolment_date,
        dimension="patient_id",
        kind="categorical",
        arm="low_dose",
    ),
    TreatmentEvent(
        name="high_dose",
        treated_units=tuple(high_dose_patient_ids),
        treatment_date=enrolment_date,
        dimension="patient_id",
        kind="categorical",
        arm="high_dose",
    ),
)

panel = Panel.from_records(
    visit_records,
    dimension="patient_id",
    freq="W",
    treatment_events=events,
    outcome_col="symptom_score",
    provenance=Provenance(
        ethics_note="IRB #2024-001, approved 2024-02-10",
        data_source="REDCap study export",
    ),
)
```

### Continuous treatment intensity (agronomic dose-response)

```python
event = TreatmentEvent(
    name="fertilizer_program",
    treated_units=tuple(treated_plot_ids),
    treatment_date=date(2024, 3, 1),
    dimension="plot_id",
    kind="continuous",
    intensity=80.0,                  # kg/ha
)
panel = Panel.from_records(
    plot_records,
    dimension="plot_id",
    freq="6ME",
    treatment_events=(event,),
    outcome_col="yield_tons_per_ha",
    weights_col="plot_area_ha",
)
```

The aggregate `treatment` column is float64 (mask × intensity).

### Non-time periods (chemistry dose-response)

`period_kind="float"` means the period axis is continuous (e.g.,
concentration in μM). No time, no `freq`:

```python
panel = Panel.from_records(
    assay_records,
    dimension="compound_id",
    period_kind="float",
    freq=None,
    outcome_col="response_fraction",
)
```

For analyses with a treatment threshold on a non-time panel, use
`period_value=` instead of `treatment_date=` on the event:

```python
TreatmentEvent(
    name="ic50_above_threshold",
    treated_units=tuple(potent_compounds),
    period_value=1.0,
    dimension="compound_id",
    kind="binary",
)
```

### Custom extractors

Records can be dicts (default) or any object exposing the right
attributes. For non-default record shapes, pass extractor callables:

```python
panel = Panel.from_records(
    domain_specific_records,
    dimension="station",
    freq="ME",
    unit_id_extractor=lambda r: r.station_id,
    period_extractor=lambda r: r.observed_at,
)
```

### Per-event columns (staggered DiD)

When multiple events are present, `from_records` attaches per-event
columns named `treatment__<event_name>` / `treated_unit__<event_name>` /
`post__<event_name>`, plus aggregate columns. Use the helper to fit
engines against a specific event:

```python
treatment_col, treated_col, post_col = panel.per_event_columns("alpha")
results = engines.did.estimate(panel, methods=("twfe",), treatment=treatment_col)
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

## Dogfood reference notebook

The shape a downstream showcase notebook takes against factor-factory
v0.1 is reproduced below. The scaffolded `notebooks/01_load.py`
(generated by `python -m factor_factory scaffold <name>`) is a
working version of this; the snippet below distils it down to the
canonical idioms.

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
    getattr(tearsheets, name)("my-showcase", overwrite=True)
```

What this buys you, line-by-line against the canonical jellycell
acceptance criteria:

- All cells run cleanly under `jellycell run` (the cells use the
  `setup()` workaround + the standard jc API).
- `jellycell render` produces an HTML catalogue (default render
  path, no special integration needed).
- `jellycell lint` passes (the cells declare their `deps=`,
  artifacts go via `jc.save`, and pyarrow is a default factor-factory
  dep so `jc.table` is available downstream).
- Notebook source is short — the manuscripts are auto-generated
  rather than hand-authored.
- The four canonical manuscripts (METHODOLOGY, DIAGNOSTICS_CHECKLIST,
  FINDINGS, MANUSCRIPT, AUDIT) are produced by the `tearsheets.*`
  calls in the second cell.
- At least one `DidResult` is produced via `estimate(panel,
  methods=("twfe",))`.

## Further reading

- [`docs/jellycell-integration.md`](jellycell-integration.md) — the
  cell conventions + workaround rationale.
- [`docs/og_context/`](og_context/README.md) — full design rationale,
  per-layer specs, and the multi-phase implementation plan.
