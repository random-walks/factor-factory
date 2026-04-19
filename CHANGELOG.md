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
- **Engine families (v0.2 brought forward into v0.1):**
  - `engines.did.callaway_santanna` — Callaway-Sant'Anna staggered-DiD
    adapter via the `differences` package. The right tool when TWFE
    suffers from negative-weights bias (Goodman-Bacon 2021).
    Auto-converts timestamp panels to integer rank-encoded periods.
    *Citation: Callaway, B., & Sant'Anna, P. H. C. (2021). Difference-
    in-differences with multiple time periods. Journal of
    Econometrics, 225(2), 200–230.*
  - `engines.survival.kaplan_meier` — non-parametric Kaplan-Meier
    survival curve with median + confidence bands via `lifelines`.
    Returns the full curve in `result.survival_curve`.
    *Citation: Kaplan, E. L., & Meier, P. (1958). Nonparametric
    estimation from incomplete observations. JASA, 53(282), 457–481.*
  - `engines.survival.cox_ph` — Cox proportional-hazards regression
    with hazard ratios, Wald p-values, 95% CIs, plus per-covariate
    Schoenfeld residual proportional-hazards test. Robust SEs
    available via `cluster=`. *Citation: Cox, D. R. (1972).
    Regression models and life-tables. JRSS:B, 34(2), 187–202.*
  - `engines.event_study.market_adjusted` — abnormal returns / CAR /
    cross-sectional t-test using never-treated units as the
    benchmark. Domain-agnostic (works for any "single-date jolt"
    analysis: M&A, FDA approvals, regulatory announcements,
    earnings). *Citation: MacKinlay, A. C. (1997). Event Studies in
    Economics and Finance. JEL, 35(1), 13–39.*
  - `engines.event_study` Result dataclass exposes per-event-time AR
    curves and per-unit cumulative abnormal returns.
- **Two Python-ecosystem gap-closers:** novel adapters that
  implement methods with no maintained Python equivalent.
  - `engines.sdid.SyntheticDidEngine` — **Synthetic
    Difference-in-Differences** (Arkhangelsky, Athey, Hirshberg,
    Imbens, Wager 2021, *American Economic Review*). Homegrown
    implementation via scipy QP for unit + time weights, weighted DiD
    for the ATT, and jackknife inference (per AER §3.4). The R
    `synthdid` package is canonical; before this commit no first-class
    Python implementation existed (only partial ports like `pysdid`).
    *Citation: Arkhangelsky, D., Athey, S., Hirshberg, D. A., Imbens,
    G. W., & Wager, S. (2021). AER, 111(12), 4088–4118.
    https://doi.org/10.1257/aer.20190159*
  - `engines.mediation.FourWayMediationEngine` — **Four-way mediation
    decomposition** (VanderWeele 2014, *Epidemiology*). Decomposes the
    total effect into Controlled Direct Effect / Reference Interaction
    / Mediated Interaction / Pure Indirect Effect, with bootstrap
    inference. The R `CMAverse` package is the reference; no
    maintained Python equivalent existed before this commit
    (`mediation` on PyPI is stale; `statsmodels.stats.mediation` only
    handles the simpler Imai-Keele-Tingley two-component decomposition).
    *Citation: VanderWeele, T. J. (2014). Epidemiology, 25(5),
    749–761. https://doi.org/10.1097/EDE.0000000000000121*
- **Cross-domain conformance fixtures** —
  `factor_factory.tests._fixtures.cross_domain` ships **thirteen**
  synthetic panels covering nearly every analytical domain:
  - `finance_event_study_panel()` — multi-outcome (returns + abnormal
    returns), business-day periods, market-cap weights.
  - `rct_longitudinal_panel()` — multi-arm categorical events,
    integer outcome (adverse-events count), IRB ethics note.
  - `agronomic_dose_response_panel()` — continuous treatment
    intensity, plot-area weights, semi-annual freq.
  - `chem_assay_panel()` — `period_kind="float"` (μM concentrations),
    no time, no treatment events.
  - `staggered_did_panel()` — three binary events at different dates
    + never-treated controls, exercises per-event columns.
  - `survival_oncology_panel()` — 200-patient cohort with
    right-censored survival, age + ECOG covariates.
  - `climate_anomaly_panel()` — station × month, temperature
    anomalies, "heat dome" regime-shift event.
  - `education_value_added_panel()` — student × quarterly
    assessment, tutoring intervention.
  - `energy_consumption_panel()` — household × month, kWh, opt-in
    rebate program.
  - `marketing_uplift_panel()` — user × week A/B test, multi-arm
    categorical (control / variant_a / variant_b), conversion outcome.
  - `macroeconomic_country_panel()` — country × year GDP growth,
    population weights, fiscal-policy event.
  - `ecology_biodiversity_panel()` — site × year species richness,
    site-area weights, conservation-program event.
  - `network_diffusion_panel()` — user × week SI cascade with seed
    cohort, spreading via random social network.
  - `sdid_block_treatment_panel()` — 50 units × 30 years with 5
    treated units adopting a policy at year 20; heterogeneous unit
    trends so vanilla DiD is biased and SDID's re-weighting earns
    its keep.
  - `mediation_panel()` — 1000-subject cross-section with binary
    treatment, continuous mediator, continuous outcome, one
    covariate; constructed with **known** ground-truth components
    (CDE=2.0, PIE=1.5, INTmed=0.45, INTref≈0.15) so the four-way
    decomposition can be sanity-checked.
- **Repo scaffolding**:
  - `pyproject.toml` with optional extras for all current + planned
    engine families: `did`, `rdd`, `scm`, `changepoint`, `stl`,
    `panel-reg`, `inequality`, `spatial`, `reporting-bias`, `hawkes`,
    `survival`, `event-study`, `het-te`, `dml`, `mediation`, `climate`,
    `diffusion`. Reserved namespaces in `engines/` for each.
  - GitHub Actions: `pytest` (3.12 + 3.13), `ruff` (lint + format
    check), `mypy` (strict).
  - **112 tests** across panel contract, diagnostics, geography, DiD
    conformance (TWFE + CS), survival (KM + Cox PH), event study,
    SDID, four-way mediation, jellycell integration, fifteen
    cross-domain fixtures, and multi-event treatment semantics.
- **Documentation**:
  - `docs/getting-started.md` — install, scaffold, build a Panel
    (with cross-domain examples for finance, RCT, ag, chem), run
    DiD, render manuscripts.
  - `docs/design-contracts.md` — the canonical data-shape contract
    factor-factory commits to.
  - `docs/supported-domains.md` — explicit matrix of supported
    domains, partial-fit domains, frontier-method extension slots,
    SDID + Four-way Mediation flagged as Python-ecosystem
    gap-closers, plus a detailed rationale for why GWAS / biobank-
    scale genetics is **deliberately** out of scope.
  - `docs/jellycell-integration.md`.
  - Per-engine docstrings include the canonical paper citation +
    DOI + reference-implementation URLs (R `synthdid`, R `CMAverse`)
    so analysts can verify the math.
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
  scaffolding). `factor-factory[did]` adds linearmodels + differences
  for the TWFE + Callaway-Sant'Anna engines; `factor-factory[survival]`
  adds lifelines for KM + Cox PH; `factor-factory[event-study]` is
  dependency-free.
- Phase-2 engine fan-out is partially shipped already: CS DiD,
  Survival (KM, Cox PH), and Event Study were pulled forward into
  v0.1 since v0.1 isn't released yet. Remaining Phase-2 families
  (Sun-Abraham, BJS, rdrobust, pysyncon, ruptures, sktime/prophet,
  pyfixest, theil, esda/libpysal/spreg, reporting-bias EM, Hawkes,
  het-te causal forests, DoubleML, SDID, mediation, climate, diffusion)
  land per-release in v0.2+, one family at a time, per the
  [implementation plan](docs/og_context/02_implementation_plan.md).
- See [`docs/supported-domains.md`](docs/supported-domains.md) for
  the full matrix of which domains the framework covers today, which
  fit partially, and which are deliberately out of scope (GWAS,
  streaming, deep learning).

## v0.0.0 — Phase 0 design (2026)

- `docs/og_context/` — design rationale, architecture, implementation
  plan, per-layer specs, downstream-change roadmap, RFC template.
- LICENSE (MIT), `pyproject.toml` placeholder, `README.md`,
  `AGENTS.md`, `CLAUDE.md` (delegating to AGENTS.md).
