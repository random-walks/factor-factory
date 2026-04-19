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
| **NYC-civic / public policy** | `staggered_did_panel`, `synthetic_panels.*` | community-district × month-end | binary, multi-event staggered | DiD: `twfe`, `cs` |
| **Finance / event study** | `finance_event_study_panel` | ticker × business day, multi-outcome (returns, abnormal) | binary event with weights (market cap) | DiD `twfe`, EventStudy `market_adjusted` |
| **Population health / RCTs** | `rct_longitudinal_panel`, `survival_oncology_panel` | patient × visit-week (longitudinal), patient × single-row (survival) | categorical multi-arm; right-censored | Survival `kaplan_meier`, `cox_ph`; DiD `twfe` per arm |
| **Agriculture / dose-response** | `agronomic_dose_response_panel` | plot × season, area weights | continuous intensity (kg/ha) | DiD `twfe` (continuous treatment column) |
| **Chemistry / pharmacology** | `chem_assay_panel` | compound × concentration (μM, float period_kind) | optional dose-threshold binary event | (analyst-fit dose-response curves; engine fan-out v0.2+) |
| **Climate / environmental science** | `climate_anomaly_panel` | station × month-end, anomalies vs. baseline | binary "heat dome" / regime-shift event | DiD `twfe`, `cs` |
| **Education / value-added** | `education_value_added_panel` | student × quarterly assessment | binary intervention (tutoring, curriculum change) | DiD `twfe`, `cs` |
| **Energy / utilities** | `energy_consumption_panel` | household × month, kWh outcome | binary opt-in program (rebate, smart-thermostat) | DiD `twfe`, `cs` |
| **Marketing / A-B testing** | `marketing_uplift_panel` | user × week, conversion outcome | categorical multi-arm (control / variant_a / variant_b) | per-arm `twfe` (uplift-test adapter v0.2+) |
| **Macroeconomics / cross-country** | `macroeconomic_country_panel` | country × year, GDP-growth outcome, population weights | binary policy adoption (fiscal, monetary) | DiD `twfe`, `cs` |
| **Ecology / conservation** | `ecology_biodiversity_panel` | site × year, species-richness outcome, area weights | binary conservation intervention | DiD `twfe`, `cs` |
| **Network / social diffusion** | `network_diffusion_panel` | user × week, binary adoption outcome | seed cohort spreading via SI cascade | DiD `twfe`; diffusion engines `ndlib` v0.2+ |

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

Stubbed in `pyproject.toml` extras + reserved engine namespaces:

| Extra | Engine namespace | What it adds | Status |
|---|---|---|---|
| `factor-factory[het-te]` | `engines.het_te` | EconML / causalml — causal forests, X/T/S/R-learners, IV forests | reserved |
| `factor-factory[dml]` | `engines.dml` | DoubleML — cross-fit double ML over arbitrary nuisance learners | reserved |
| (no extra) | `engines.sdid` | Synthetic DiD (Arkhangelsky 2021) — homegrown cvxpy adapter, no mature Python pkg yet | experimental |
| (no extra) | `engines.mediation` | NDE / NIE / total-effect via `statsmodels.stats.mediation` (in default install) | reserved |
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

- **GWAS / biobank-scale genetics.** Different ops world: HPC,
  BGEN/VCF formats, JVM-backed `hail`. The panel pattern doesn't
  pay off when row count is in the billions. Use `hail`, `pysnptools`,
  or `BOLT-LMM` directly.
- **Streaming / online algorithms.** factor-factory assumes
  finite, materializable panels.
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
