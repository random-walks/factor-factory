# factor-factory

A domain-agnostic factor-model + analysis-pipeline framework with
**first-class jellycell integration**, a **Protocol-based pluggable
engine pattern**, and **first-class implementations of two methods
the Python ecosystem was missing entirely** (Synthetic DiD,
Arkhangelsky 2021; Four-way Mediation Decomposition,
VanderWeele 2014).

The same `Panel` shape hosts NYC-civic data, finance event studies,
clinical trials, agronomic dose-response, chemistry assays, climate
anomaly studies, education-intervention evaluations, energy-meter
data, marketing A/B tests, macroeconomic country panels, ecological
biodiversity surveys, and social-network diffusion cascades. Add a
new domain by writing extractors; add a new method by writing a
~150-LOC engine adapter that fits the Protocol.

## Status

`v0.1.0` (in development). **Not yet released to PyPI.**

What ships today:

| Layer | Status |
|---|---|
| Tidy layer (`Panel`, `TreatmentEvent`, `RecordView`, `Provenance`) | ✅ Domain-agnostic data contracts, parquet round-trip with self-describing metadata |
| Diagnostics (the four required ones) | ✅ `multi_index_assertions`, `standardized_mean_differences`, `parallel_trends_plot`, `residual_diagnostics` |
| Engine: DiD | ✅ `TwfeEngine` (linearmodels), `CallawaySantannaEngine` (differences) |
| Engine: Survival | ✅ `KaplanMeierEngine`, `CoxPHEngine` (lifelines) |
| Engine: Event Study | ✅ `MarketAdjustedEngine` (homegrown, no deps) |
| Engine: Synthetic DiD | ✅ `SyntheticDidEngine` — **closes a Python-ecosystem gap** (Arkhangelsky 2021) |
| Engine: Mediation | ✅ `FourWayMediationEngine` — **closes a Python-ecosystem gap** (VanderWeele 2014) |
| Jellycell integration | ✅ `cells.setup()`, `figure.from_path()`, 5 tearsheet renderers, `scaffold` CLI |
| CI: pytest 3.12 + 3.13, ruff, mypy strict | ✅ 112 tests passing |
| Cross-domain conformance fixtures | ✅ 15 synthetic panels covering every supported domain |
| Sphinx / Read the Docs site | ⏳ Planned after the next cleanup pass |
| PyPI release | ⏳ Pending the cleanup pass + first downstream adopter |

Engine families planned for v0.2+: `rdd` (rdrobust), `scm` (pysyncon),
`changepoint` (ruptures + bayesloop), `stl` (sktime + prophet),
`panel-reg` (pyfixest), `inequality` (theil decompositions),
`spatial` (esda + libpysal + spreg), `reporting-bias` (latent EM),
`hawkes` (tick), `het-te` (econml causal forests), `dml` (DoubleML),
`climate` (xclim), `diffusion` (ndlib). See
[`docs/supported-domains.md`](docs/supported-domains.md) for the full
matrix + reserved engine namespaces.

GWAS / biobank-scale genetics is **deliberately** out of scope —
[rationale documented](docs/supported-domains.md#gwas--biobank-scale-quantitative-genetics).

## Quick start

```bash
# Default install + the engine families you need
pip install factor-factory[did,survival,event-study]
# or everything currently shipping:
pip install factor-factory[all]

# Scaffold a new showcase
python -m factor_factory scaffold my-showcase
cd my-showcase
python notebooks/01_load.py
```

The scaffolded notebook builds a synthetic panel, runs a TWFE DiD
via `factor_factory.engines.did.estimate`, saves a parallel-trends
figure, and regenerates all five canonical manuscripts
(`METHODOLOGY.md`, `DIAGNOSTICS_CHECKLIST.md`, `FINDINGS.md`,
`MANUSCRIPT.md`, `AUDIT.md`).

In a notebook, the canonical pattern:

```python
from factor_factory.jellycell.cells import setup
ns = setup(also=("matplotlib.pyplot as plt",))
jc, pd, np, plt, Image = ns["jc"], ns["pd"], ns["np"], ns["plt"], ns["Image"]

from datetime import date
from factor_factory.tidy import Panel, TreatmentEvent
from factor_factory.engines.did import estimate as did_estimate
from factor_factory.engines.survival import estimate as surv_estimate

panel = Panel.from_records(
    records,
    dimension="community_district",
    freq="ME",
    treatment_events=(TreatmentEvent(
        name="rat_pilot",
        treated_units=("MN-01", "MN-02"),
        treatment_date=date(2024, 6, 1),
        dimension="community_district",
    ),),
    outcome_col="complaint_count",
)

# Multi-engine DiD (TWFE + Callaway-Sant'Anna in one call)
results = did_estimate(panel, methods=("twfe", "cs"), cluster="unit_id")
print(results.summary_table())
```

See [`docs/getting-started.md`](docs/getting-started.md) for cross-
domain examples (finance event study, multi-arm RCT, agronomic
dose-response, chemistry IC₅₀ assay, etc.).

## Architecture in one diagram

```
raw records
  ↓ tidying              factor_factory.tidy        (Panel + TreatmentEvent + Provenance + RecordView)
tidied panel
  ↓ factor construction  factor_factory.factors     (volume, recurrence, HHI, resolution, reliability — Phase 2)
factor panel
  ↓ diagnostics          factor_factory.diagnostics (SMD, parallel-trends, residuals, balance)
diagnostic-annotated panel
  ↓ modeling             factor_factory.engines     (did / survival / event_study / sdid / mediation today;
                                                     rdd / scm / changepoint / stl / panel_reg / inequality /
                                                     spatial / reporting_bias / hawkes / het_te / dml / climate /
                                                     diffusion in v0.2+)
modeling results
  ↓ reporting            factor_factory.jellycell   (5 tearsheet renderers + scaffold CLI + #J1/#J2 workarounds)
```

Every engine family follows the same shape: a frozen `Result`
dataclass + an `Engine` Protocol + a registry-backed `estimate()`
dispatcher. Adapters wrap external packages (linearmodels,
differences, lifelines, …) or roll their own math when no canonical
package exists. See [`docs/design-contracts.md`](docs/design-contracts.md)
for the data contract and
[`docs/og_context/03_specs/engine_protocol.md`](docs/og_context/03_specs/engine_protocol.md)
for the engine-family contract.

## Python-ecosystem gaps closed

Two methods that the Python data-science ecosystem was missing
entirely (canonical R packages, no maintained Python equivalent).
Both shipped as first-class engines with the canonical paper +
reference R-package linked in the engine docstring.

### `engines.sdid` — Synthetic Difference-in-Differences

> Arkhangelsky, D., Athey, S., Hirshberg, D. A., Imbens, G. W., &
> Wager, S. (2021). Synthetic Difference-in-Differences. *American
> Economic Review*, 111(12), 4088–4118.
> <https://doi.org/10.1257/aer.20190159>
>
> Reference R implementation: <https://synth-inference.github.io/synthdid/>

SDID combines unit weights (synthetic-control style) with time
weights and a weighted DiD estimator. It's a 2021 advance that
addresses the parallel-trends fragility of vanilla DiD when units
have heterogeneous trends. Until this commit, the only
production-grade implementation was the R `synthdid` package; partial
Python ports like `pysdid` were lightly maintained.

Our adapter:

- Solves the unit-weights and time-weights QPs via `scipy.optimize.minimize` (SLSQP), no `cvxpy` dependency
- Uses the regularization ζ = (N_tr · T_post)^(1/4) · σ̂ from AER §3.3
- Computes the closed-form weighted-DiD ATT for binary block treatment
- Provides jackknife inference (per AER §3.4, recommended for n_treated ≥ 2)
- Returns unit weights + time weights so analysts can interrogate the synthetic control

Validated against a known-ATT=4.0 fixture: recovers ATT=4.535 (SE=0.245).

### `engines.mediation.FourWayMediationEngine` — VanderWeele's four-way decomposition

> VanderWeele, T. J. (2014). A unification of mediation and
> interaction: A four-way decomposition. *Epidemiology*, 25(5),
> 749–761. <https://doi.org/10.1097/EDE.0000000000000121>
>
> Reference R implementation: <https://bs1125.github.io/CMAverse/>

Decomposes a treatment's total effect into:

- **CDE** (Controlled Direct Effect)
- **INTref** (Reference Interaction)
- **INTmed** (Mediated Interaction)
- **PIE** (Pure Indirect Effect)

`statsmodels.stats.mediation` only provides the simpler
Imai-Keele-Tingley two-component decomposition (NDE / NIE). The
`mediation` package on PyPI is stale. Our adapter ports the
linear-linear case from the Epidemiology paper directly with
bootstrap inference (1000 resamples by default).

Validates against a fixture with known components — recovers all
four within 1 SE:

| Component | True | Estimated | SE |
|---|---|---|---|
| CDE | 2.00 | 2.004 | 0.087 |
| PIE | 1.50 | 1.514 | 0.070 |
| INTmed | 0.45 | 0.397 | 0.085 |
| INTref | 0.15 | 0.137 | 0.030 |

## Domain coverage

15 cross-domain conformance fixtures exercise the Panel contract
across data shapes from NYC-civic to chemistry. Brief table —
[`docs/supported-domains.md`](docs/supported-domains.md) is the full
matrix.

| Domain | Fixture | Engines that fit |
|---|---|---|
| NYC-civic / public policy | `staggered_did_panel` | DiD `twfe`, `cs`, `sdid` |
| Finance event study | `finance_event_study_panel` | DiD `twfe`, EventStudy `market_adjusted` |
| Population health (longitudinal) | `rct_longitudinal_panel` | DiD per-arm |
| Population health (survival) | `survival_oncology_panel` | Survival `kaplan_meier`, `cox_ph` |
| Population health (mediation) | `mediation_panel` | Mediation `four_way` |
| Agriculture / dose-response | `agronomic_dose_response_panel` | DiD `twfe` w/ continuous treatment |
| Chemistry / pharmacology | `chem_assay_panel` | (analyst-fit dose-response) |
| Climate anomaly | `climate_anomaly_panel` | DiD `twfe`, `cs`, `sdid` |
| Education / value-added | `education_value_added_panel` | DiD `twfe`, `cs`; Mediation |
| Energy / utilities | `energy_consumption_panel` | DiD `twfe`, `cs`, `sdid` |
| Marketing / A-B testing | `marketing_uplift_panel` | per-arm `twfe`, Mediation |
| Macroeconomics | `macroeconomic_country_panel` | DiD `twfe`, `cs`, `sdid` |
| Ecology / conservation | `ecology_biodiversity_panel` | DiD `twfe`, `cs`, `sdid` |
| Network / social diffusion | `network_diffusion_panel` | DiD `twfe` (diffusion engines v0.2+) |
| Multi-state policy block | `sdid_block_treatment_panel` | DiD `twfe`, **`sdid`** (the headline use-case) |

## Documentation

| File | Purpose |
|---|---|
| [`docs/getting-started.md`](docs/getting-started.md) | Install, scaffold, build a Panel with cross-domain examples, run estimators, render manuscripts |
| [`docs/design-contracts.md`](docs/design-contracts.md) | The canonical data-shape contract factor-factory commits to (the source of truth, supersedes the og-context spec) |
| [`docs/jellycell-integration.md`](docs/jellycell-integration.md) | Cell conventions, the upstream-jellycell-bug workarounds (#J1, #J2), the `scaffold` command |
| [`docs/supported-domains.md`](docs/supported-domains.md) | Domain matrix + extension patterns + GWAS-exclusion rationale |
| [`docs/og_context/`](docs/og_context/) | Original design rationale, architecture, implementation plan, per-layer specs, downstream-change roadmap, RFC template |
| [`CHANGELOG.md`](CHANGELOG.md) | Per-version changelog with citations |

The plan is to consolidate the user-facing docs above into a Sphinx
+ Read the Docs site after the next cleanup pass settles. Until then
the markdown is the source of truth.

## Known issues + limitations

Honest list to inform the next cleanup pass.

### Engine-family caveats

- **SDID jackknife** holds `omega` and `lam` fixed across leave-one-out
  iterations (matching the R `synthdid` default). Re-solving them
  per iteration is correct but ~N_tr × slower; we trade a small
  amount of accuracy for tractability. For single-treated-unit
  panels, the jackknife is degenerate and we fall back to a
  placebo-style sigma estimate from control first-differences —
  proper placebo inference is a v0.2 follow-up.
- **CS adapter** silently drops the `cluster=` kwarg. The
  `differences` package needs the cluster column on the data passed
  in, but we strip extras before passing for robustness against the
  package's internal column-filtering. Workaround: include the
  cluster column manually in `df` if you need clustered SEs.
- **CS adapter** rejects panels where `period_kind` ∉ {`timestamp`,
  `integer`}. Float / ordinal-period staggered DiD is out of scope
  (the math doesn't naturally apply).
- **Mediation `four_way`** only handles linear outcome + linear
  mediator. Logistic outcome and logistic mediator extensions need
  Monte-Carlo integration over the mediator distribution (per
  VanderWeele 2014 §3) — planned for v0.2.
- **Mediation** has no sensitivity analysis to unobserved
  confounding (the rho-test in `CMAverse`). Planned v0.2.
- **Event Study** ships only the simple market-adjusted baseline
  (cross-sectional control mean as benchmark). The proper market
  model (FF3 / FF5 / Carhart-4 residuals) with Patell-z + BMP
  tests is v0.2.
- **Cox PH** wrapper doesn't surface `lifelines`' `strata=`
  parameter yet — needed for stratified analysis.
- **TWFE** under staggered rollout has the well-known Goodman-Bacon
  bias. Use `cs` or `sdid` instead — flagged in the engine
  docstring + `getting-started.md`.

### Framework caveats

- **Per-event treatment columns** generate a lot of columns when
  many events are present (3 per event for binary, 4 for categorical).
  For panels with >50 events this could become memory-intensive.
  Consider a lazy / on-demand alternative.
- **Panel `validate()`** runs on every construction and is O(n).
  For very large panels users may want a `validate=False` opt-out.
  Currently always runs.
- **`_attach_treatment_columns`** is exposed only via underscored
  module-private path. Should be made public (`Panel.attach_treatment_columns`)
  for users who build panels manually via the `__init__` constructor.
- **`Panel.from_records`** assumes records fit in memory. Streaming
  / chunked construction is deferred (panel_contract.md flags this
  as Phase-2 work).
- **`record_view_columns`** has no schema validation — users can
  request columns that don't exist on records and get silent `None`s.
- **Tearsheet renderers** read `did_results.json` exclusively for
  the engines table. Other engine families (Survival, Event Study,
  SDID, Mediation) don't yet have a templated table — currently they
  surface as generic JSON via the `headline_artifacts` block.

### Repo / ops

- **No PyPI release yet.** Install via `pip install -e .` from a
  clone for now. PyPI publication after the cleanup pass.
- **No `uv.lock` checked in.** CI uses `uv pip install -e .[…]`
  rather than `uv sync`. Locking is deferred until first PyPI
  release so dependency churn during v0.1 development doesn't
  bloat lockfile diffs.
- **No CONTRIBUTING.md** yet — RFC template in
  `docs/og_context/05_rfc_template.md` is the closest thing.
- **CI matrix** is only Linux (Ubuntu) + Python 3.12 / 3.13.
  Mac / Windows / older Python aren't tested.
- **Mypy strict** passes but `differences`, `lifelines` lack stubs
  (we ignore-missing-imports for them). Same for `scipy`,
  `matplotlib`, `shapely`, `linearmodels`.
- **Test runtime** is ~3 s locally, ~30 s in CI. Acceptable for now;
  watch as more engines land.

## What to work on next

A handoff for the next cleanup + enhancement pass.

### Priority 1 — release readiness

1. **Sphinx + Read the Docs site.** Consolidate the user-facing
   markdown into a Sphinx project. Auto-generate API docs from
   docstrings. Pin the Sphinx version in `pyproject.toml` extras.
2. **PyPI publication.** Set up `python -m build` + `twine upload`,
   tag releases, and add a release-automation GitHub Action.
3. **`CONTRIBUTING.md`** + a short PR template. Reference the RFC
   pattern in `docs/og_context/05_rfc_template.md` for new engine
   families.
4. **`uv.lock`** at the first PyPI release.
5. **Cross-platform CI matrix.** Add macOS + Windows runners,
   maybe Python 3.14 once it lands.

### Priority 2 — engine completeness

6. **Sun-Abraham** + **Borusyak-Jaravel-Spiess** DiD adapters
   alongside the CS adapter. Both have Python implementations
   (`differences` may already wrap them; check).
7. **rdrobust adapter** in `engines.rdd`. The package is mature
   (Calonico-Cattaneo-Titiunik); pin a version and ship a
   conformance test against synthetic kink + jump fixtures.
8. **pysyncon SCM adapter** in `engines.scm`. Plus the augmented
   SCM (Ben-Michael-Feller-Rothstein 2021) since it's a research
   frontier.
9. **Causal forests** via `econml.dml.CausalForestDML` in
   `engines.het_te`. High-value frontier method; install size is
   non-trivial (~200 MB).
10. **DoubleML** via the `DoubleML` package in `engines.dml`.
    Lighter dep than econml; cross-fit double ML over arbitrary
    sklearn nuisance learners.
11. **Logistic-outcome + logistic-mediator extension** for the
    Mediation engine. Math is the same but needs Monte-Carlo
    integration over the mediator distribution; see VanderWeele
    2014 §3.
12. **Mediation sensitivity analysis** (rho-test for unobserved
    confounding) — port the relevant code from `CMAverse`.
13. **SDID placebo inference** for single-treated-unit case +
    placebo-test option as an alternative to jackknife for
    multi-treated-unit case.
14. **Fama-French market-model** Event Study adapter (FF3 / FF5 /
    Carhart-4 residuals + Patell-z + BMP tests). Pair with a
    `pandas-datareader` factor loader (cached aggressively because
    the upstream endpoints are flaky).
15. **Stratified Cox PH** — surface `lifelines` `strata=` in the
    wrapper.

### Priority 3 — framework polish

16. **Public `Panel.attach_treatment_columns`** method (currently
    underscored module-private).
17. **`Panel.validate(strict=False)`** opt-out for very large panels.
18. **Streaming `Panel.from_records`** for >10M records (chunked
    builder pattern; flagged as v0.2 in `panel_contract.md`).
19. **Schema validation for `record_view_columns`** in `from_records`
    — surface a clear error when requested columns don't exist.
20. **Cross-engine tearsheet templates.** Currently `findings.md.j2`
    only renders DiD results. Add per-family blocks for Survival,
    Event Study, SDID, Mediation.
21. **`SurvivalResults.summary_table()`** + `EventStudyResults.summary_table()`
    + `SdidResults.summary_table()` + `MediationResults.summary_table()`
    — match the `DidResults` API for engine-family parity.
22. **`Panel.summary()`** convenience method for tearsheet generation
    (n_units, n_periods, treatment-event count, etc., as a dict).

### Priority 4 — testing + docs

23. **Property-based tests** with `hypothesis` for the panel-contract
    invariants (random panels should always validate, malformed
    panels should always fail).
24. **Snapshot tests** for tearsheet renderers — guard against
    template drift.
25. **Performance benchmarks** for `Panel.from_records` and engine
    fits on synthetic 100k-record panels. `pytest-benchmark` plus
    a CI job that flags >2× regressions.
26. **Per-engine cookbook** in the Sphinx site with ~10 worked
    examples per engine family (one per major use case).
27. **Migration guide** for `nyc311` / `subway-access` adopters
    (Phase 4 in the implementation plan). Concrete before/after PR
    snippets.
28. **Validate the SDID port against the canonical Prop 99 example**
    from the AER paper. Should recover the published ATT to within
    numerical tolerance.

### Priority 5 — nice-to-haves

29. **Async fetch** in `tidy.socrata.bulk_fetch` for very long
    fetches.
30. **Multi-geography panels** (a panel with both CD-level and
    station-level units). Currently unsupported; users build two
    panels.
31. **Continuous-time SCM** / matrix-completion estimators
    (`engines.scm.matrix_completion`).
32. **Bayesian causal forests** (BCF) in `engines.het_te` — research
    frontier.
33. **Quarto / RMarkdown report generator** as an alternative to
    jellycell tearsheets — different rendering pipeline, may pay
    off for consumers who don't want jellycell.

### Where this commit gets beefy

This branch has grown substantially past the original Phase-1 scope
(skeleton + first DiD engine). It now includes the full v0.1 surface
plus four Phase-2 engine families (CS, Survival, Event Study, SDID,
Mediation) and 15 cross-domain fixtures. Future PRs should split
along engine-family lines per the RFC template — one family per PR.

## Where to start (for new agents)

1. **Read** [`docs/getting-started.md`](docs/getting-started.md) — install + first scaffold + first DiD
2. **Read** [`docs/design-contracts.md`](docs/design-contracts.md) — what data shapes the framework commits to
3. **Read** [`docs/supported-domains.md`](docs/supported-domains.md) — what domains are covered today + what's deferred + what's deliberately out of scope
4. **Browse** [`factor_factory/engines/`](factor_factory/engines/) — pick a family that interests you and read its `_base.py` (Protocol + Result) followed by an adapter
5. **For new engine families**, copy the `engines/sdid/` or `engines/mediation/` shape — Result dataclass, Protocol, registry-backed dispatcher, conformance tests, fixture
6. **For new data domains**, add a fixture under `factor_factory/tests/_fixtures/cross_domain.py` and parametrize the cross-domain conformance test over it
7. **For framework changes**, follow the RFC pattern in [`docs/og_context/05_rfc_template.md`](docs/og_context/05_rfc_template.md)

## License

MIT. Same as sibling random-walks packages.
