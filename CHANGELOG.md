# Changelog

## v0.1.0 — Phase 1 skeleton (in progress)

### Added

- **Tidy layer**:
  - `factor_factory.tidy.Panel` with the strict
    `MultiIndex(unit_id, period)` schema, pydantic
    `PanelMetadata` + `TreatmentEvent`, full `validate()` invariants,
    parquet round-trip via `to_parquet` / `from_parquet`.
  - `Panel.from_records` builds balanced panels from dict records (or
    any object exposed by custom extractor callables) with treatment
    events derived into `treatment` / `treated_unit` / `post`
    columns.
  - `factor_factory.tidy.RecordView` companion view for record-level
    analyses that need lat/lon (RDD via rdrobust, within-unit
    spatial heterogeneity).
  - `factor_factory.tidy.geography` — `BoundaryCollection` /
    `BoundaryFeature` data types, registerable boundary-source
    adapters, `centroids_from_boundaries`, pairwise haversine
    `distance_matrix`.
  - `factor_factory.tidy.socrata` — `SocrataAdapter` Protocol +
    `bulk_fetch` convenience wrapper (concrete adapters live in
    domain packages).
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
- **Repo scaffolding**:
  - `pyproject.toml` with optional extras stubbed for every Phase-2
    engine family.
  - GitHub Actions: `pytest` (3.12 + 3.13), `ruff` (lint + format
    check), `mypy` (strict).
  - 41 tests across panel contract, diagnostics, geography, DiD
    conformance, and jellycell integration.
- **Documentation**:
  - `docs/getting-started.md`
  - `docs/jellycell-integration.md`
  - This CHANGELOG.

### Acceptance gate (Phase 1)

- ✅ `python -m factor_factory scaffold <name>` produces a runnable
  project that builds a Panel, estimates DiD via TWFE, and emits all
  five canonical manuscripts.
- ⏳ `showcase-starter` rewrite in `blaise-website` against
  factor-factory v0.1 — proposed shape documented in
  `docs/getting-started.md` § "Proposed showcase-starter rewrite";
  actual rewrite happens in a follow-up PR in the consumer repo.

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
