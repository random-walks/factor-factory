# factor-factory

A domain-agnostic factor-model + analysis-pipeline framework with first-class jellycell integration, a Protocol-based pluggable engine pattern, and first-class implementations of two methods the Python ecosystem was missing entirely:

- **Synthetic Difference-in-Differences** (Arkhangelsky et al. 2021)
- **Four-way Mediation Decomposition** (VanderWeele 2014)

The same `Panel` shape hosts NYC-civic data, finance event studies, clinical trials, agronomic dose-response, chemistry assays, climate anomaly studies, education-intervention evaluations, energy-meter data, marketing A/B tests, macroeconomic country panels, ecological biodiversity surveys, and social-network diffusion cascades. Add a new domain by writing extractors; add a new method by writing a ~150-LOC engine adapter that fits the Protocol.

## Install

```bash
pip install factor-factory[did,survival,event-study]
# or everything currently shipping:
pip install factor-factory[all]
```

## Scaffold a showcase

```bash
python -m factor_factory scaffold my-showcase
cd my-showcase
python notebooks/01_load.py
```

## Where to next

```{toctree}
:maxdepth: 2
:caption: User guide

getting-started
supported-domains
design-contracts
jellycell-integration
```

```{toctree}
:maxdepth: 2
:caption: Cookbook

cookbook/did-twfe
cookbook/did-callaway-santanna
cookbook/survival-km
cookbook/survival-cox
cookbook/event-study-market-adjusted
cookbook/sdid
cookbook/mediation-four-way
```

```{toctree}
:maxdepth: 2
:caption: Reference

reference/architecture
reference/contracts
reference/piggyback-map
apidocs/index
```

```{toctree}
:maxdepth: 2
:caption: Development

development/contributing
development/adding-an-engine
development/releasing
development/dev-setup
development/testing
```

## Status at a glance

| Layer | Status |
|---|---|
| Tidy layer (Panel, TreatmentEvent, RecordView, Provenance) | ✅ |
| Diagnostics (SMD, parallel trends, residuals, assertions) | ✅ |
| Engines: DiD (TWFE + Callaway-Sant'Anna) | ✅ |
| Engines: Survival (KM + Cox PH) | ✅ |
| Engines: Event Study (market-adjusted) | ✅ |
| Engines: Synthetic DiD | ✅ |
| Engines: Four-way Mediation | ✅ |
| Jellycell integration (5 tearsheet renderers) | ✅ |
| CI (pytest 3.12 + 3.13, ruff, mypy strict) | ✅ |
| Cross-domain conformance fixtures (15 synthetic panels) | ✅ |
| Sphinx + Read the Docs site | ✅ (you're reading it) |
| PyPI release | ⏳ First tag imminent |

Engine families landing in v0.2 → v1.12: RDD, SCM (+augmented, +matrix-completion), heterogeneous treatment effects (causal forests, X/R-learner, BCF), DoubleML, changepoint, STL/Prophet, panel regression (HDFE), inequality, spatial, reporting-bias, Hawkes, climate, diffusion. See [`docs/og_context/06_post_v0.1_roadmap.md`](https://github.com/random-walks/factor-factory/blob/main/docs/og_context/06_post_v0.1_roadmap.md) for the full batch plan.
