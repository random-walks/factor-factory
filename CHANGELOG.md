# Changelog

## v0.1.0 — Phase 1 skeleton (in progress)

### Added

- **Tidy layer** — domain-agnostic from the start; the same `Panel`
  shape hosts NYC-civic, finance event-study, RCT longitudinal,
  agronomic dose-response, and chemistry assay data:
  - `factor_factory.tidy.Panel` with `MultiIndex(unit_id, period)`,
    pydantic `PanelMetadata` + `TreatmentEvent` + `Provenance`, full
    `validate()` invariants, parquet round-trip.
  - `unit_id` accepts any hashable (string, int, tuple).
  - `period` supports four kinds via `period_kind=`: `"timestamp"`
    (calendar), `"integer"` (days-from-event, age-in-months),
    `"float"` (dose, temperature, concentration), `"ordinal"` (any
    orderable label). Non-time panels skip `freq`.
  - Multi-outcome panels via `outcome_cols=("primary", "secondary",
    ...)`; `Panel.outcome_col` returns the primary, `outcome_cols`
    the full tuple. Outcomes can be int (counts, indicators) or float
    (returns, yields).
  - Optional weights column via `weights_col=` (e.g., `"population"`,
    `"market_cap_mm"`, `"plot_area_ha"`).
  - `Panel.from_records` builds balanced panels from dict records or
    any object exposed by custom extractor callables; passes through
    a `provenance=` kwarg for self-describing panels.
  - `factor_factory.tidy.RecordView` — required columns just `unit_id`
    + `period`; `latitude` + `longitude` are conventional but
    optional. `distance_to_point()` raises a clear error when
    lat/lon absent.
  - `factor_factory.tidy.geography` — `BoundaryCollection` /
    `BoundaryFeature` data types, registerable boundary-source
    adapters, `centroids_from_boundaries`, pairwise haversine
    `distance_matrix`. **Optional**: panels without geography
    (finance, chemistry, RCT) skip this layer entirely.
  - `factor_factory.tidy.socrata` — `SocrataAdapter` Protocol +
    `bulk_fetch` convenience wrapper (concrete adapters live in
    domain packages).
- **TreatmentEvent** — supports three treatment kinds, multi-event
  panels, and non-time anchors:
  - `kind="binary"` (default) — classic DiD treatment.
  - `kind="continuous"` with `intensity=` — dose-response, treatment
    intensity (kg/ha, mg/kg, ad-spend dollars).
  - `kind="categorical"` with `arm=` — multi-arm RCT; produces
    `arm__<event_name>` columns instead of binary `treatment__<event_name>`.
  - `period_value=` for non-time panels (dose threshold,
    days-from-event), mutually exclusive with `treatment_date=`.
  - `dimension=` field replaces `geography=` (which stays as a
    backwards-compat alias).
- **Per-event columns** — multi-event panels generate
  `treatment__<event_name>` / `treated_unit__<event_name>` /
  `post__<event_name>` per event (or `arm__<event_name>` for
  categorical), plus aggregate columns. Use
  `panel.per_event_columns("event_name")` to fetch the trio for a
  specific event when fitting an engine.
- **Provenance metadata** (`PanelMetadata.provenance`) — pydantic
  `Provenance` model with `data_source`, `license`, `ethics_note`,
  `citation`, `creator`, `dataset_version`, `created_at`. Surfaces
  in METHODOLOGY tearsheet automatically. Round-trips through the
  parquet `.meta.json` sidecar.
- **Diagnostics layer** — the four required-for-v0.1 primitives:
  - `multi_index_assertions(panel)` — structural-integrity check.
  - `standardized_mean_differences(panel, ...)` — pooled-SD SMDs +
    Stuart-2010 imbalance flags.
  - `parallel_trends_plot(panel, ...)` — pre-DiD visual.
  - `residual_diagnostics(residuals, ...)` — Jarque-Bera +
    Shapiro-Wilk + (when `fitted_values=` supplied) a manual
    Breusch-Pagan via squared-residual regression.
- **Engine framework**:
  - `factor_factory.engines.EngineRegistry[E]` — generic, lazy,
    runtime-extensible.
  - `factor_factory.engines.did.DidResult` (frozen dataclass) +
    `DidEngine` Protocol + `estimate()` dispatcher returning a
    `DidResults` wrapper with `summary_table()`.
  - `factor_factory.engines.did.twfe.TwfeEngine` — TWFE adapter via
    `linearmodels.PanelOLS`, the only Phase-1 DiD adapter.
- **Jellycell integration MVP**:
  - `factor_factory.jellycell.cells.setup()` — workaround for
    [jellycell #J1](https://github.com/random-walks/jellycell/issues/10).
  - `factor_factory.jellycell.figure.from_path()` — workaround for
    [jellycell #J2](https://github.com/random-walks/jellycell/issues/11).
  - Five tearsheet renderers (`tearsheets.methodology` /
    `diagnostics` / `findings` / `manuscript` / `audit`) with Jinja2
    templates and a `<!-- tearsheet:freeze -->` marker that preserves
    below-the-marker prose across re-renders.
  - `python -m factor_factory scaffold <name>` — generates a working
    showcase skeleton (jellycell.toml, notebook stub, manuscripts,
    data plan).
  - `factor-factory` console script as a shorter alias.
- **Cross-domain conformance fixtures** —
  `factor_factory.tests._fixtures.cross_domain` ships five synthetic
  panels exercising every generalization axis:
  - `finance_event_study_panel()` — multi-outcome (returns + abnormal
    returns), business-day periods, market-cap weights.
  - `rct_longitudinal_panel()` — multi-arm categorical events,
    integer outcome (adverse-events count).
  - `agronomic_dose_response_panel()` — continuous treatment
    intensity, plot-area weights.
  - `chem_assay_panel()` — `period_kind="float"`, no time, no
    treatment events.
  - `staggered_did_panel()` — three binary events at different dates,
    exercises per-event columns.
- **Repo scaffolding**:
  - `pyproject.toml` with optional extras stubbed for every Phase-2
    engine family.
  - GitHub Actions: `pytest` (3.12 + 3.13), `ruff` (lint + format
    check), `mypy` (strict).
  - 76 tests across panel contract, diagnostics, geography, DiD
    conformance, jellycell integration, cross-domain fixtures, and
    multi-event treatment semantics.
- **Documentation**:
  - `docs/getting-started.md` — install, scaffold, build a Panel
    (with cross-domain examples for finance, RCT, ag, chem), run
    DiD, render manuscripts.
  - `docs/design-contracts.md` — the canonical data-shape contract
    factor-factory commits to.
  - `docs/jellycell-integration.md`.
  - This CHANGELOG.

### Fixed

- Tearsheet freeze marker is line-anchored. Doc text quoting the
  literal marker string no longer matches the splice regex (which
  previously caused all auto-generated content above the in-prose
  reference to be frozen as "stale" forever).

### Backwards compatibility

- `TreatmentEvent(geography=...)` and `PanelMetadata(geography=...)`
  / `outcome_col=...` accept the legacy kwargs and silently translate
  to `dimension=` and `outcome_cols=(...)`. Aliases stay through
  v1.x.

### Acceptance gate (Phase 1)

- ✅ `python -m factor_factory scaffold <name>` produces a runnable
  project that builds a Panel, estimates DiD via TWFE, and emits all
  five canonical manuscripts.
- ⏳ Downstream dogfood — a scaffolded starter showcase running
  cleanly under `jellycell run` / `render` / `lint`, with the four
  manuscripts auto-generated by `factor_factory.jellycell.tearsheets.*`
  and at least one `DidResult` produced via
  `factor_factory.engines.did.estimate(panel, methods=("twfe",))`.
  Validation happens in the consumer repo that adopts factor-factory
  first.

### Notes

- Default install ships only tidy + diagnostics + jellycell (plus
  scaffolding). `factor-factory[did]` adds linearmodels for the TWFE
  engine.
- Engine fan-out (Callaway-Sant'Anna, Sun-Abraham,
  Borusyak-Jaravel-Spiess for DiD; rdrobust for RDD; pysyncon for
  SCM; etc.) lands per-release in v0.2+, one family at a time, per
  the [implementation plan](docs/og_context/02_implementation_plan.md).

## v0.0.0 — Phase 0 design (2026)

- `docs/og_context/` — design rationale, architecture, implementation
  plan, per-layer specs, downstream-change roadmap, RFC template.
- LICENSE (MIT), `pyproject.toml` placeholder, `README.md`,
  `AGENTS.md`, `CLAUDE.md` (delegating to AGENTS.md).
