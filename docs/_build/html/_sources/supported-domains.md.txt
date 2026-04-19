# Supported domains + extension patterns

factor-factory's central abstraction is **domain-agnostic**: the same
`Panel` shape, the same engine Protocol pattern, and the same
jellycell tearsheet pipeline serve every analytical domain that maps
naturally to "units × periods + treatments + outcomes." This doc lays
out which domains the framework already covers, where new frontier
methods plug in, and which areas are deliberately out of scope.

If you're building an analysis in a domain not listed below, the
extension patterns at the bottom should let you wire it up in an
afternoon — and a one-PR contribution back makes it canonical for
the next consumer.

## Domains shipped today

Every row below has a synthetic fixture under
`factor_factory.tests._fixtures.cross_domain` and a worked example
in [`getting-started.md`](getting-started.md).

| Domain | Fixture | Panel shape | Treatment shape | Engines |
|---|---|---|---|---|
| **NYC-civic / public policy** | `staggered_did_panel`, `synthetic_panels.*` | community-district × month-end | binary, multi-event staggered | DiD: `twfe`, `cs`, `sdid` |
| **Finance / event study** | `finance_event_study_panel` | ticker × business day, multi-outcome (returns, abnormal) | binary event with weights (market cap) | DiD `twfe`, EventStudy `market_adjusted` |
| **Population health / RCTs** | `rct_longitudinal_panel`, `survival_oncology_panel`, `mediation_panel` | patient × visit-week (longitudinal), patient × single-row (survival), subject × baseline (mediation) | categorical multi-arm; right-censored; binary + mediator | Survival `kaplan_meier`, `cox_ph`; Mediation `four_way`; DiD `twfe` per arm |
| **Agriculture / dose-response** | `agronomic_dose_response_panel` | plot × season, area weights | continuous intensity (kg/ha) | DiD `twfe` (continuous treatment column) |
| **Chemistry / pharmacology** | `chem_assay_panel` | compound × concentration (μM, float period_kind) | optional dose-threshold binary event | (analyst-fit dose-response curves; engine fan-out v0.2+) |
| **Climate / environmental science** | `climate_anomaly_panel` | station × month-end, anomalies vs. baseline | binary "heat dome" / regime-shift event | DiD `twfe`, `cs`, `sdid` |
| **Education / value-added** | `education_value_added_panel` | student × quarterly assessment | binary intervention (tutoring, curriculum change) | DiD `twfe`, `cs`; Mediation `four_way` |
| **Energy / utilities** | `energy_consumption_panel` | household × month, kWh outcome | binary opt-in program (rebate, smart-thermostat) | DiD `twfe`, `cs`, `sdid` |
| **Marketing / A-B testing** | `marketing_uplift_panel` | user × week, conversion outcome | categorical multi-arm (control / variant_a / variant_b) | per-arm `twfe`, Mediation `four_way` |
| **Macroeconomics / cross-country** | `macroeconomic_country_panel`, `sdid_block_treatment_panel` | country × year, GDP-growth outcome, population weights | binary policy adoption (fiscal, monetary) | DiD `twfe`, `cs`, `sdid` |
| **Ecology / conservation** | `ecology_biodiversity_panel` | site × year, species-richness outcome, area weights | binary conservation intervention | DiD `twfe`, `cs`, `sdid` |
| **Network / social diffusion** | `network_diffusion_panel` | user × week, binary adoption outcome | seed cohort spreading via SI cascade | DiD `twfe`; diffusion engines `ndlib` v0.2+ |
| **Causal mediation (any domain)** | `mediation_panel` | subject × single-row with A, M, Y, C | binary treatment + mediator (binary or continuous) | Mediation `four_way` (VanderWeele 2014) |

## Domains where the framework partially fits today

These work today via the generic Panel + engine pattern but lack a
dedicated engine adapter. Pull requests welcome.

| Domain | What's missing | v0.2+ slot |
|---|---|---|
| **Manufacturing / SPC** | Control-chart engine (Shewhart, EWMA, CUSUM) | `engines.process_control/` |
| **Sports analytics** | Player-impact + plus-minus regression adapters | `engines.panel_reg/` covers most cases |
| **Real estate / hedonic** | Hedonic-pricing helpers, repeat-sales index | `engines.panel_reg/` + custom helpers |
| **Transportation** | Traffic OD-matrix factor primitives | `engines.spatial/` covers Moran's I; OD-specific helpers TBD |
| **Genomics / quant genetics** | Mixed-model GWAS scale isn't a fit (HPC + biobank world); see "Out of scope" below | — |
| **Astronomy / spectroscopy** | Period-axis fits (`period_kind="float"` with wavelength); engine fan-out for spectral decomposition would be new ground | — |
| **Behavioral neuroscience** | Subject × trial × condition; fits the panel shape if reshaped to `(subject, trial)` | — |

## Frontier-method extension slots

Stubbed in `pyproject.toml` extras + reserved engine namespaces. The
two highlighted SDID and Mediation slots ship today: they close
genuine Python-ecosystem gaps where no maintained equivalent exists.

| Extra | Engine namespace | What it adds | Status |
|---|---|---|---|
| (no extra) | `engines.sdid` | **Synthetic DiD** (Arkhangelsky, Athey, Hirshberg, Imbens, Wager, *AER* 2021) — homegrown via scipy QP + jackknife inference; no mature Python pkg before this | **shipped (`SyntheticDidEngine`)** |
| (no extra) | `engines.mediation` | **Four-way mediation decomposition** (VanderWeele, *Epidemiology* 2014) — CDE / INTref / INTmed / PIE for linear-linear models with bootstrap inference; no maintained Python equivalent before this | **shipped (`FourWayMediationEngine`)** |
| `factor-factory[het-te]` | `engines.het_te` | EconML / causalml — causal forests, X/T/S/R-learners, IV forests | reserved |
| `factor-factory[dml]` | `engines.dml` | DoubleML — cross-fit double ML over arbitrary nuisance learners | reserved |
| `factor-factory[climate]` | `engines.climate` | xclim climatological-baseline helpers, Mann-Kendall trend test | reserved |
| `factor-factory[diffusion]` | `engines.diffusion` | ndlib SI / SIR / threshold-model / Bass-diffusion fits | reserved |

## Adding a new engine family

The framework's design pivot. To add a new engine family
(`my_family/`), create:

```
factor_factory/engines/my_family/
├── __init__.py        # registry + estimate() dispatcher
├── _base.py           # MyFamilyResult dataclass + MyFamilyEngine Protocol
├── adapter_a.py       # one engine adapter
├── adapter_b.py       # another adapter
└── ...
```

The Result dataclass commits to a small set of required fields
(method, point estimate, SE, n) plus optional method-specific
diagnostics. The Protocol pins the `fit(panel, *, ...) -> Result`
signature. Adapters wrap external packages or roll their own
math. Conformance tests parametrize over `registry.available()` to
validate every adapter against the same fixture set.

See `factor_factory/engines/did/` for the canonical example;
`engines/survival/` for a non-DiD shape (per-subject rather than
panel-aggregated); `engines/event_study/` for a single-event
(rather than DiD) family.

## Extending the data contract

Most domain-specific needs fit within the existing contract:

- **New cross-sectional dimension?** Just pass `dimension="ticker"` /
  `"patient_id"` / `"plot_id"`. No code changes needed.
- **Non-time period axis?** Pass `period_kind="integer"` (days from
  event), `"float"` (concentration / dose), or `"ordinal"` (any
  orderable label).
- **Multi-outcome panel?** Pass `outcome_cols=("primary", "secondary")`.
- **Continuous / multi-arm treatment?** Use `kind="continuous"` with
  `intensity=` or `kind="categorical"` with `arm=` on `TreatmentEvent`.
- **Per-record covariates?** Pass `record_view=True` plus
  `record_view_columns=(...)`.
- **Provenance / publishing metadata?** Pass `provenance=Provenance(...)`.
- **Observation weights?** Pass `weights_col="population"` (or
  `"market_cap"`, `"plot_area_ha"`, etc.).

If your domain doesn't fit any of those — for example, a panel where
units have *time-varying membership* (a stock that joins/leaves an
index, a patient who switches arms) — open an issue. The likely
resolution is adding a new `period_kind` or extending `TreatmentEvent`
rather than forking the panel concept.

## Out of scope (deliberately)

Listed so the absence is explicit, not accidental.

### GWAS / biobank-scale quantitative genetics

**Decision: do not ship a first-class engine.**

Statistical genetics at biobank scale is a fundamentally different
ops world from the analyses factor-factory targets:

- **Data scale.** A modern GWAS analyzes ~10⁶–10⁷ SNPs across
  ~10⁵–10⁶ subjects. The (subject × SNP) "panel" is in the tens of
  billions of cells; the in-memory `Panel` abstraction is wrong by
  three to five orders of magnitude. Materializing it would either
  OOM or require a chunked-iterator design that doesn't match the
  rest of the framework.
- **File formats.** Inputs are PLINK BED/BIM/FAM, BGEN, VCF, or
  more recently sparse pgen — none of which the existing
  `Panel.from_records` ingestion path is designed to handle. PLINK
  files alone require a C-extension reader (`pysnptools`,
  `bed-reader`).
- **Runtime ops.** Linkage-disequilibrium pruning, principal-component
  adjustment for population structure, and per-SNP mixed-model
  regression are typically run on HPC clusters with multi-day
  walltimes. The dominant production stack is `hail` (Spark/JVM, ~2 GB
  install, distributed by design) and `BOLT-LMM` (single-binary C++
  with custom file formats). Wrapping these inside a Python framework
  doesn't add value over calling them directly.
- **Inference shape.** The genetics community has converged on
  per-SNP summary statistics + post-hoc meta-analysis (`METAL`,
  `LDSC`, `MR-Base`), not per-study Result dataclasses. The
  factor-factory Result-class pattern doesn't fit.

**What we recommend instead.** For small-N quantitative-trait analysis
that fits in memory (~hundreds of variants, ~thousands of subjects),
use `statsmodels.regression.mixed_linear_model.MixedLM` directly. For
biobank-scale work, use the established stack:

- [`hail`](https://hail.is/) — Broad Institute, Spark-backed, the
  modern de-facto standard for biobank GWAS.
- [`pysnptools`](https://github.com/fastlmm/PySnpTools) — Microsoft
  Research, lightweight PLINK BED reader; pairs well with
  `MixedLM` for teaching-scale analyses.
- [`limix`](https://github.com/limix/limix) — single-trait and
  multi-trait mixed-model GWAS, lightly maintained but a reasonable
  Python-native option for small-to-medium N.
- [`scikit-allel`](https://scikit-allel.readthedocs.io/) —
  population-genetics summary stats (allele frequencies, LD,
  haplotype diversity).
- [PLINK 2.0](https://www.cog-genomics.org/plink/2.0/) and
  [BOLT-LMM](https://alkesgroup.broadinstitute.org/BOLT-LMM/) —
  industry-standard CLI tools for production runs.

If a future analysis bridges the two worlds (e.g., post-GWAS
mediation analysis on summary statistics), the right pattern is to
load summary stats into a flat factor-factory `Panel` of (variant,
trait) and apply the existing engines — not to push native genetic
file formats inside the framework.

### Other deliberate exclusions

- **Streaming / online algorithms.** factor-factory assumes finite,
  materializable panels.
- **Deep learning.** PyTorch / JAX / TensorFlow stay separate. Engines
  may *call* into these (e.g., DoubleML with neural nuisance learners
  via econml) but factor-factory itself is statistical / classical.
- **Custom IDE / live viewer.** That's jellycell's job.
- **Bayesian-everything.** We adapt PyMC / bayesloop where it makes
  sense (changepoints, hierarchical priors) but don't pick a
  Bayesian-vs-frequentist side per se.

## Coordinating engine PRs

Follow the [RFC template](og_context/05_rfc_template.md) for new
engine families. One family per RFC, one PR per adapter within the
family. The conformance tests + cross-domain fixtures should catch
regressions automatically once your adapter is registered in the
family's `__init__.py`.
