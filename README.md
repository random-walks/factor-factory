# factor-factory

[![PyPI version](https://img.shields.io/pypi/v/factor-factory.svg)](https://pypi.org/project/factor-factory/)
[![Python versions](https://img.shields.io/pypi/pyversions/factor-factory.svg)](https://pypi.org/project/factor-factory/)
[![Documentation Status](https://readthedocs.org/projects/factor-factory/badge/?version=latest)](https://factor-factory.readthedocs.io/en/latest/)
[![CI](https://github.com/random-walks/factor-factory/actions/workflows/ci.yml/badge.svg)](https://github.com/random-walks/factor-factory/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![mypy: strict](https://img.shields.io/badge/mypy-strict-blue)](https://mypy.readthedocs.io/en/stable/config_file.html#confval-strict)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

A domain-agnostic factor-model + analysis-pipeline framework with a Protocol-based pluggable engine pattern, first-class [jellycell](https://github.com/random-walks/jellycell) integration, and the only production-grade Python implementations of **Synthetic Difference-in-Differences** (Arkhangelsky et al. 2021, AER) and the **Four-way Mediation Decomposition** (VanderWeele 2014, Epidemiology).

The same `Panel` shape hosts NYC-civic data, finance event studies, clinical trials, agronomic dose-response, chemistry assays, climate anomaly studies, education-intervention evaluations, energy-meter data, marketing A/B tests, macroeconomic country panels, ecological biodiversity surveys, and social-network diffusion cascades. Add a new domain by writing extractors; add a new method by writing a ~150-LOC engine adapter that fits the Protocol.

---

## Install

```bash
# Default install — tidy layer + diagnostics + jellycell (no engines)
pip install factor-factory

# With specific engine families
pip install factor-factory[did,survival,event-study]

# Everything currently shipping
pip install factor-factory[all]
```

Supports **Python 3.12+**. Dependency manager of choice is [`uv`](https://github.com/astral-sh/uv); `pip` works the same way.

## Quick start

Scaffold a showcase, run it, render tearsheets:

```bash
python -m factor_factory scaffold my-showcase
cd my-showcase
python notebooks/01_load.py
```

The scaffolded notebook builds a synthetic panel, runs a TWFE DiD via `factor_factory.engines.did.estimate`, saves a parallel-trends figure, and regenerates all five canonical manuscripts (`METHODOLOGY.md`, `DIAGNOSTICS_CHECKLIST.md`, `FINDINGS.md`, `MANUSCRIPT.md`, `AUDIT.md`).

The canonical pattern inside a notebook:

```python
from datetime import date
from factor_factory.tidy import Panel, TreatmentEvent
from factor_factory.engines.did import estimate as did_estimate

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

# Multi-engine DiD in one call — TWFE + Callaway-Sant'Anna side-by-side
results = did_estimate(panel, methods=("twfe", "cs"), cluster="unit_id")
print(results.summary_table())
```

See the [getting-started guide](https://factor-factory.readthedocs.io/en/latest/getting-started.html) for cross-domain examples (finance event study, multi-arm RCT, agronomic dose-response, chemistry IC₅₀ assay, etc.).

---

## Architecture

```
raw records
  ↓ tidying              factor_factory.tidy         Panel + TreatmentEvent + Provenance + RecordView
tidied panel
  ↓ diagnostics          factor_factory.diagnostics  SMD, parallel-trends, residuals, balance
diagnostic-annotated panel
  ↓ modeling             factor_factory.engines      17 engine families (see below)
modeling results
  ↓ reporting            factor_factory.jellycell    5 tearsheet renderers + scaffold CLI
                         factor_factory.reporting    Quarto (.qmd) alternative
```

Every engine family follows the same shape: a frozen `Result` dataclass + an `Engine` Protocol + a registry-backed `estimate()` dispatcher. Adapters wrap external packages (`linearmodels`, `differences`, `lifelines`, `rdrobust`, `pysyncon`, `econml`, `DoubleML`, `ruptures`, `sktime`, `pyfixest`, `esda`, `tick`, `ndlib`, …) or roll their own math when no canonical package exists.

See the [design contracts](https://factor-factory.readthedocs.io/en/latest/design-contracts.html) for the data contract and the [reference architecture](https://factor-factory.readthedocs.io/en/latest/reference/architecture.html) page for the full engine-family contract.

---

## Shipping engine families

Install the extras you need; unlisted adapters fail-fast with a crisp `ImportError` pointing at the right `pip install factor-factory[<family>]`.

| Family | Adapters | Extra | Canonical citation |
|---|---|---|---|
| **DiD** | `twfe`, `callaway_santanna`, `sun_abraham`, `borusyak_jaravel_spiess` | `[did]` | Goodman-Bacon 2021 / Callaway-Sant'Anna 2021 / Sun-Abraham 2021 / Borusyak et al. 2024 |
| **Survival** | `kaplan_meier`, `cox_ph` (+ `strata=`) | `[survival]` | Kaplan-Meier 1958 / Cox 1972 |
| **Event Study** | `market_adjusted`, `fama_french` (FF3/FF5/Carhart-4) | `[event-study]` | MacKinlay 1997 / Fama-French 1993 & 2015 |
| **Synthetic DiD** | `sdid` — jackknife + placebo inference | (built-in) | **[Arkhangelsky et al. 2021 (AER)](https://doi.org/10.1257/aer.20190159)** — Python-ecosystem gap closed |
| **Mediation** | `four_way` — CDE / INTref / INTmed / PIE + `sensitivity()` | (built-in) | **[VanderWeele 2014 (Epidemiology)](https://doi.org/10.1097/EDE.0000000000000121)** — Python-ecosystem gap closed |
| **RDD** | `rd_robust` (sharp + fuzzy) | `[rdd]` | Calonico-Cattaneo-Titiunik 2014 |
| **SCM** | `pysyncon`, `augmented`, `matrix_completion` | `[scm]` | Abadie et al. 2010 / Ben-Michael et al. 2021 / Athey et al. 2021 |
| **Heterogeneous TE** | `causal_forest`, `bcf` | `[het-te]` | Wager-Athey 2018 / Hahn-Murray-Carvalho 2020 |
| **DoubleML** | `plr` | `[dml]` | Chernozhukov et al. 2018 |
| **Changepoint** | `ruptures` (Pelt / BinSeg / Window) | `[changepoint]` | Truong-Oudre-Vayatis 2020 |
| **STL** | `sktime_stl` | `[stl]` | Cleveland et al. 1990 |
| **Panel regression** | `pyfixest` (HDFE) | `[panel-reg]` | Correia 2016 |
| **Spatial** | `morans_i` | `[spatial]` | Moran 1950 / Anselin 1995 |
| **Inequality** | `theil_t` (+ between/within decomposition) | (built-in) | Theil 1967 |
| **Reporting bias** | `latent_em` (two-class EM) | (built-in) | Dempster-Laird-Rubin 1977 |
| **Hawkes** | `tick` | `[hawkes]` | Hawkes 1971 / Bacry et al. 2013 |
| **Climate** | `mann_kendall` (+ Sen's slope) | (built-in) | Mann 1945 / Kendall 1948 |
| **Diffusion** | `ndlib_sir` | `[diffusion]` | — |

**17 engine families / 30+ adapters.** Use the `/engine-status` Claude Code slash-command (or inspect `factor_factory.engines.<family>.registry`) to see the live state.

---

## Python-ecosystem gaps closed

Two methods the Python ecosystem was missing entirely (canonical R packages, no maintained Python equivalent). Both shipped as first-class engines with the canonical paper + reference R-package linked in the engine docstring.

### `engines.sdid` — Synthetic Difference-in-Differences

> Arkhangelsky, D., Athey, S., Hirshberg, D. A., Imbens, G. W., & Wager, S. (2021). Synthetic Difference-in-Differences. *American Economic Review*, 111(12), 4088–4118. [doi:10.1257/aer.20190159](https://doi.org/10.1257/aer.20190159)
>
> Reference R implementation: [synthdid](https://synth-inference.github.io/synthdid/)

SDID combines unit weights (synthetic-control style) with time weights and a weighted DiD estimator. It's a 2021 advance that addresses the parallel-trends fragility of vanilla DiD when units have heterogeneous trends. The R `synthdid` package is canonical; partial Python ports like `pysdid` are lightly maintained.

Our adapter:

- Solves the unit- and time-weights QPs via `scipy.optimize.minimize` (SLSQP), no `cvxpy` dependency
- Uses the regularization `ζ = (N_tr · T_post)^(1/4) · σ̂` from AER §3.3
- Computes the closed-form weighted-DiD ATT for binary block treatment
- Supports **both** jackknife (AER §3.4 default) **and** placebo inference (preferred for single-treated-unit panels)
- Returns unit weights + time weights so analysts can interrogate the synthetic control

Validated against a known-ATT=4.0 fixture: recovers ATT=4.535 (SE=0.245).

### `engines.mediation.FourWayMediationEngine` — VanderWeele's four-way decomposition

> VanderWeele, T. J. (2014). A unification of mediation and interaction: A four-way decomposition. *Epidemiology*, 25(5), 749–761. [doi:10.1097/EDE.0000000000000121](https://doi.org/10.1097/EDE.0000000000000121)
>
> Reference R implementation: [CMAverse](https://bs1125.github.io/CMAverse/)

Decomposes a treatment's total effect into:

- **CDE** (Controlled Direct Effect)
- **INTref** (Reference Interaction)
- **INTmed** (Mediated Interaction)
- **PIE** (Pure Indirect Effect)

`statsmodels.stats.mediation` only provides the simpler Imai-Keele-Tingley two-component decomposition (NDE / NIE). The `mediation` package on PyPI is stale. Our adapter ports the linear-linear case from the Epidemiology paper directly with bootstrap inference (1000 resamples by default), and adds an unobserved-confounding sensitivity analysis (`.sensitivity(rho_range, n_points)`) ported from CMAverse's rho-test.

Validates against a fixture with known components — recovers all four within 1 SE:

| Component | True | Estimated | SE |
|---|---|---|---|
| CDE | 2.00 | 2.004 | 0.087 |
| PIE | 1.50 | 1.514 | 0.070 |
| INTmed | 0.45 | 0.397 | 0.085 |
| INTref | 0.15 | 0.137 | 0.030 |

---

## Domain coverage

Cross-domain conformance fixtures exercise the Panel contract across data shapes from NYC-civic to chemistry. See the [supported-domains page](https://factor-factory.readthedocs.io/en/latest/supported-domains.html) for the full matrix.

| Domain | Fixture | Engines that fit |
|---|---|---|
| NYC-civic / public policy | `staggered_did_panel` | DiD (twfe, cs, sa, bjs, sdid) |
| Finance event study | `finance_event_study_panel` | DiD twfe, Event Study (market_adjusted, fama_french) |
| Population health — longitudinal | `rct_longitudinal_panel` | DiD per-arm |
| Population health — survival | `survival_oncology_panel` | Survival (kaplan_meier, cox_ph, stratified) |
| Population health — mediation | `mediation_panel` | Mediation four_way |
| Agriculture / dose-response | `agronomic_dose_response_panel` | DiD twfe (continuous treatment) |
| Chemistry / pharmacology | `chem_assay_panel` | Analyst-fit dose-response |
| Climate anomaly | `climate_anomaly_panel` | DiD, Climate (mann_kendall) |
| Education / value-added | `education_value_added_panel` | DiD, Mediation |
| Energy / utilities | `energy_consumption_panel` | DiD, STL |
| Marketing / A-B testing | `marketing_uplift_panel` | Per-arm TWFE, Mediation, Het-TE (causal_forest) |
| Macroeconomics | `macroeconomic_country_panel` | DiD, SDID, Panel regression (HDFE) |
| Ecology / conservation | `ecology_biodiversity_panel` | DiD, Spatial (morans_i) |
| Network / social diffusion | `network_diffusion_panel` | Diffusion (ndlib_sir) |
| Multi-state policy block | `sdid_block_treatment_panel` | DiD twfe, SDID (the headline use-case) |
| Test-score cutoff | `rdd_sharp_cutoff_panel` | RDD rd_robust |
| Single treated state | `scm_single_treated_state_panel` | SCM (augmented, matrix_completion) |

GWAS / biobank-scale genetics is **deliberately out of scope** — scale, file formats, and inference shape all mismatch. Use [hail](https://hail.is/), [pysnptools](https://fastlmm.github.io/PySnpTools/), [PLINK 2.0](https://www.cog-genomics.org/plink/2.0/), or [BOLT-LMM](https://alkesgroup.broadinstitute.org/BOLT-LMM/) instead. Full rationale on the supported-domains page.

---

## Documentation

Full docs at **[factor-factory.readthedocs.io](https://factor-factory.readthedocs.io/)** (Sphinx + Furo + autodoc2).

| Page | Purpose |
|---|---|
| [Getting started](https://factor-factory.readthedocs.io/en/latest/getting-started.html) | Install, scaffold, build a Panel, run estimators, render manuscripts |
| [Cookbook](https://factor-factory.readthedocs.io/en/latest/cookbook/did-twfe.html) | Per-adapter worked examples (DiD, Survival, Event Study, SDID, Mediation, RDD, SCM) |
| [Supported domains](https://factor-factory.readthedocs.io/en/latest/supported-domains.html) | Domain matrix + extension patterns + GWAS-exclusion rationale |
| [Design contracts](https://factor-factory.readthedocs.io/en/latest/design-contracts.html) | The canonical Panel data-shape contract |
| [Jellycell integration](https://factor-factory.readthedocs.io/en/latest/jellycell-integration.html) | Cell conventions + tearsheet renderers |
| [Reference / architecture](https://factor-factory.readthedocs.io/en/latest/reference/architecture.html) | 6-layer pipeline + dependency order |
| [Reference / contracts](https://factor-factory.readthedocs.io/en/latest/reference/contracts.html) | Locked Panel / Engine Protocol / Tearsheet JSON snapshots |
| [Reference / piggyback-map](https://factor-factory.readthedocs.io/en/latest/reference/piggyback-map.html) | Which upstream packages each adapter wraps |
| [Migration v0 → v1](https://factor-factory.readthedocs.io/en/latest/migration/v0-to-v1.html) | Upgrade guide for downstream adopters |
| [Contributing](CONTRIBUTING.md) | Dev setup + contract ceremony + PR checklist |

---

## Contributing

PRs welcome — especially new engine families. Factor-factory is an **adapter-first** framework: before writing engine math from scratch, consult the [piggyback map](https://factor-factory.readthedocs.io/en/latest/reference/piggyback-map.html). See [CONTRIBUTING.md](CONTRIBUTING.md) for the full workflow.

Claude Code users get slash-commands for common operations:

```
/engine-status    # 17-family status report
/add-engine <family>   # scaffold a new engine family end-to-end
/contract-check   # audit a diff against the three contract invariants
/bump [patch|minor|major]   # bump version + roll CHANGELOG
/release-check    # preflight before a tag push
```

## Citing

If you use factor-factory in academic work, please cite:

- **The engine-specific canonical paper(s)** — each adapter's docstring carries the DOI + reference R-package URL.
- **This software record** — via [CITATION.cff](CITATION.cff) (Zenodo-compatible).

## License

MIT. See [LICENSE](LICENSE). Same license as sibling `random-walks` packages ([jellycell](https://github.com/random-walks/jellycell), [nyc311](https://github.com/random-walks/nyc311), [nyc-geo-toolkit](https://github.com/random-walks/nyc-geo-toolkit)).
