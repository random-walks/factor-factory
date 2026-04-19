# Design contracts

The data shapes factor-factory commits to. These are the contracts
downstream consumers — `nyc311`, `subway-access`, finance toolkits,
clinical-trial pipelines, agronomic-yield analyses, chemistry assay
workflows — build against. They are designed to be **domain-agnostic**:
the same `Panel` shape hosts NYC-civic data, a hedge-fund event study,
a multi-arm RCT, a fertilizer dose-response trial, and an in-vitro
inhibitor IC₅₀ assay.

This doc supersedes the v0.1-skeleton sketch in
[`og_context/03_specs/panel_contract.md`](og_context/03_specs/panel_contract.md).
Treat it as the canonical reference for the shapes the framework
guarantees.

## Why a single Panel?

The Protocol-pluggable engine pattern is the architectural payload of
factor-factory. Engines should be able to consume **any** consumer's
Panel without bespoke adaptation — that's how a downstream package
gets multi-engine DiD / RDD / SCM "for free." The cost is a slightly
opinionated central contract. The benefit is that an engine added in
v0.5 works against panels built in v0.1.

## The Panel

```
MultiIndex(unit_id, period) → wide DataFrame
       +
   PanelMetadata (pydantic)
       +
   RecordView (optional)  → per-record companion
```

### Index axes

| Level | Allowed types | Constraint |
|---|---|---|
| `unit_id` | Any hashable. Common: `str` (tickers, geographies), `int` (patient IDs, plot IDs), `tuple` (composite keys). | No NaN; must be unique within `(unit_id, period)`. |
| `period` | One of four `period_kind`s: `timestamp` (calendar), `integer` (day-from-event, age in months), `float` (dose, temperature), `ordinal` (any orderable label). | Must match `metadata.period_kind`; balanced (cartesian product). |

### Outcome columns

`metadata.outcome_cols: tuple[str, ...]` — at least one. The first is
the *primary* (returned by `panel.outcome_col`). Outcome dtype must
be numeric (any int or float — count outcomes, survival indicators,
returns, yields all valid).

### Framework-aware columns (auto-attached)

When `treatment_events` are provided, the panel gains:

**Per-event columns** (always, one set per event):
- `treated_unit__<event_name>` — int8 0/1
- `post__<event_name>` — int8 0/1
- For binary events: `treatment__<event_name>` — int8 0/1
- For continuous events: `treatment__<event_name>` — float64 (mask × intensity)
- For categorical events: `arm__<event_name>` — string (`<arm>` or `"control"`)

**Aggregate columns** (when ≥1 binary or continuous event present):
- `treated_unit` — int8, OR across events
- `post` — int8, OR across events
- `treatment` — int8 (all-binary) or float64 (any continuous), summed across events

For the staggered-DiD case, fit your engine against either an aggregate
column (Bacon-decomposition caveats apply) or a per-event column via
`panel.per_event_columns(event_name)`.

### Optional weights column

`metadata.weights_col: str | None`. When set, points to a numeric
column on the panel. Used by population-weighted estimators (Theil
index, weighted regressions). Common values:
- Civic: `"population"` (decennial census + ACS yearly)
- Finance: `"market_cap"` / `"adv_30d_volume"`
- Ag: `"plot_area_ha"`
- Population health: `"person_years"` / `"sample_size"`

Access via `panel.weights` (pandas Series indexed like `panel.df`).

### Provenance metadata

`metadata.provenance: Provenance` — a structured pydantic model:

| Field | Purpose |
|---|---|
| `data_source` | URL / DOI / dataset id where the data came from |
| `license` | `"CC-BY-4.0"`, `"ODbL-1.0"`, `"public-domain"`, `"proprietary"`, etc. |
| `ethics_note` | IRB approval / data-ethics statement (population-health, sensitive data) |
| `citation` | How to cite this dataset in a paper or report |
| `creator` | Organization or author that produced the data |
| `dataset_version` | Vintage tag (e.g., `"2024Q3"`, `"v3.1"`) |
| `created_at` | When the panel was constructed (UTC) |

Tearsheet renderers surface these in METHODOLOGY.md and AUDIT.md
automatically. The publishing-best-practices ethos: every analysis
makes its data lineage legible without forcing the analyst to write
prose around it.

## TreatmentEvent

The treatment shape factor-factory commits to handle:

```python
TreatmentEvent(
    name="...",                    # short identifier; suffixes per-event columns
    treated_units=("u1", "u2"),    # tuple of hashables
    treatment_date=date(...),      # for time-based panels
    period_value=...,              # for non-time panels (mutually exclusive)
    dimension="...",               # e.g., "ticker", "patient_id", "plot_id"
    kind="binary"|"continuous"|"categorical",
    intensity=...,                 # required when kind="continuous"
    arm="...",                     # required when kind="categorical"
    metadata={...},                # free-form dict for engine consumers
)
```

Validation runs on construction; per-event column attachment runs on
`Panel.from_records` (or any direct call to `_attach_treatment_columns`).

### Worked examples

**Binary policy rollout** (NYC-civic shape):

```python
TreatmentEvent(
    name="rat_pilot_2024",
    treated_units=("MN-01", "MN-02", "BX-03"),
    treatment_date=date(2024, 6, 1),
    dimension="community_district",
)
```

**Continuous treatment intensity** (agronomic dose-response):

```python
TreatmentEvent(
    name="fertilizer_program",
    treated_units=tuple(treated_plot_ids),
    treatment_date=date(2024, 3, 1),
    dimension="plot_id",
    kind="continuous",
    intensity=80.0,                # kg/ha
)
```

**Multi-arm RCT** (one event per arm; control is implicit):

```python
events = (
    TreatmentEvent(
        name="low_dose",
        treated_units=tuple(low_dose_patients),
        treatment_date=enrolment_date,
        dimension="patient_id",
        kind="categorical",
        arm="low_dose",
    ),
    TreatmentEvent(
        name="high_dose",
        treated_units=tuple(high_dose_patients),
        treatment_date=enrolment_date,
        dimension="patient_id",
        kind="categorical",
        arm="high_dose",
    ),
)
```

**Dose-threshold on a non-time panel** (chemistry):

```python
TreatmentEvent(
    name="ic50_above_threshold",
    treated_units=tuple(potent_compound_ids),
    period_value=1.0,              # μM threshold
    dimension="compound_id",
    kind="binary",
)
```

**Staggered policy rollout** (multiple events at different dates):

```python
events = (
    TreatmentEvent(name="alpha", treated_units=cohort_a, treatment_date=date(2022, 7, 1), dimension="cd"),
    TreatmentEvent(name="beta",  treated_units=cohort_b, treatment_date=date(2023, 1, 1), dimension="cd"),
    TreatmentEvent(name="gamma", treated_units=cohort_c, treatment_date=date(2023, 7, 1), dimension="cd"),
)
panel = Panel.from_records(records, dimension="cd", treatment_events=events)
# Per-event columns: treatment__alpha / treated_unit__alpha / post__alpha (etc.)
# Aggregate columns: treated_unit / post / treatment (sum across events)
```

## RecordView

A flat per-record DataFrame that lives alongside the aggregated Panel.
Required columns: `unit_id` and `period`. Beyond that, anything goes.

The lat/lon convention is one important but optional case: when
`latitude` and `longitude` columns are present,
`RecordView.distance_to_point(lon, lat)` returns the haversine distance
in km — useful as the running variable for record-level RDD.

For non-spatial domains, the RecordView carries the analyst's own
per-record covariates: clinical visit timestamps, asset-level
metadata, sample-level QC flags, etc. The `record_view_columns` kwarg
on `Panel.from_records` controls which extras are pulled.

## Cross-domain conformance fixtures

`factor_factory.tests._fixtures.cross_domain` provides synthetic
fixtures across data shapes:

| Fixture | Domain | Generalization exercised |
|---|---|---|
| `finance_event_study_panel()` | Finance | Business-day periods (no monthly bin), multi-outcome (returns + abnormal_returns), market-cap weights |
| `rct_longitudinal_panel()` | Population health | Multi-arm categorical events (placebo / low_dose / high_dose), integer outcome (adverse_events count) |
| `agronomic_dose_response_panel()` | Agriculture | Continuous treatment intensity (kg/ha), semi-annual freq, plot-area weights |
| `chem_assay_panel()` | Chemistry | `period_kind="float"` (dose concentration), no time dimension, no treatment events |
| `staggered_did_panel()` | Multi-event policy | Three binary events at different dates; per-event columns |

Engine conformance tests should parametrize across these fixtures so
new adapters validate against every supported data shape.

## Engine Protocol invariants

The engine framework adapts; the data contract above is fixed. Each
engine family defines its own Protocol + frozen `Result` dataclass —
see [`og_context/03_specs/engine_protocol.md`](og_context/03_specs/engine_protocol.md).

The contract every engine MUST honor:

1. Accept any `Panel` matching the contract above; raise a clear error
   if a required column is missing.
2. Cite the underlying canonical method in the engine class docstring.
3. Return a frozen `Result` dataclass with at minimum the family's
   required fields.
4. Pass the family's conformance test suite against all relevant
   cross-domain fixtures.

## Versioning + backwards compatibility

The contracts in this doc are **stable surface** for v0.1+. Renames
(e.g., `geography` → `dimension`) ship with backwards-compat aliases
that pydantic validators silently translate. The aliases stay through
v1.x and may be removed in v2.0 with a one-major-version deprecation
warning cycle.

The Protocol shapes for engine families MAY evolve in v0.x as new
engines surface field requirements — locked at v1.0.
