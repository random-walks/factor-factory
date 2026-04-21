# Migration guide — v0.x → v1.0

factor-factory v1.0 is the first stable release. Most changes through the
v0.x → v1.0 journey (batches 0–16 on `feat/v1.0-roadmap`) were **additive**
and require no downstream code changes. The handful of surface changes
worth noting are below.

## Pinned floor: jellycell >= 1.4.0

If your showcase pins `jellycell`, bump to `>=1.4.0,<2`. The floor
contains every fix factor-factory's jellycell integration has ever
relied on, plus the generic `jellycell.tearsheets.*` in-notebook API
introduced in 1.4.0 (complementary to factor_factory's five fixed-
schema renderers):

- `setup`-cell never caching (jellycell #16, shipped 1.3.2) — factor_factory.jellycell.cells.setup
- `jc.figure` path-only form (jellycell #17, shipped 1.3.2) — factor_factory.jellycell.figure.from_path
- `run` / `export` honor `--project` (jellycell #18, shipped 1.3.3)
- `jc.table` ergonomics + pyarrow default (jellycell #19, shipped 1.3.4)
- tearsheet tag filtering (jellycell #20, shipped 1.3.5) — per-engine tearsheet scoping
- kernel-iopub hang diagnostics (jellycell #22, shipped 1.3.5)
- `jellycell.tearsheets.*` Python API + `deps-no-comma` lint rule (jellycell #24/#25, shipped 1.4.0)

## Additive API additions (no migration required)

The following are new public APIs. Existing code continues to work.

- `Panel.attach_treatment_columns(events, replace=False)` — promoted
  from module-private `_attach_treatment_columns`. The underscore alias
  is kept for one minor release.
- `Panel.validate(strict=True)` — new kwarg. `strict=False` skips O(n)
  data-quality checks.
- `Panel(..., validate=True)` — new kwarg on the constructor.
- `Panel.summary()` — new instance method returning a dict.
- `<Family>Result.summary_table()` — added to every `Result` dataclass
  (DiD / Survival / EventStudy / SDID / Mediation / RDD / SCM / etc.).
- `PanelBuilder` — streaming alternative to `Panel.from_records` for
  large record streams. Exposed via `factor_factory.tidy.PanelBuilder`.
- `tidy.socrata.bulk_fetch_async` — async variant of `bulk_fetch`.

## New engine families

12 new engine families landed between v0.1 and v1.0:

| Family | Adapters | Canonical citation |
|---|---|---|
| `engines.rdd` | `rd_robust` | Calonico-Cattaneo-Titiunik 2014 |
| `engines.scm` | `augmented`, `pysyncon` | Ben-Michael et al. 2021 / Abadie et al. 2010 |
| `engines.het_te` | `causal_forest` | Wager-Athey 2018 |
| `engines.dml` | `plr` | Chernozhukov et al. 2018 |
| `engines.changepoint` | `ruptures` | Truong-Oudre-Vayatis 2020 |
| `engines.stl` | `sktime_stl` | Cleveland et al. 1990 |
| `engines.panel_reg` | `pyfixest` | Correia 2016 |
| `engines.spatial` | `morans_i` | Moran 1950 / Anselin 1995 |
| `engines.inequality` | `theil_t` | Theil 1967 |
| `engines.reporting_bias` | `latent_em` | Dempster-Laird-Rubin 1977 |
| `engines.hawkes` | `tick` | Hawkes 1971 |
| `engines.climate` | `mann_kendall` | Mann 1945 / Kendall 1948 |
| `engines.diffusion` | `ndlib_sir` | — |

Each adapter carries its citation DOI + reference-implementation URL in the
class docstring. Install the extras you need:

```bash
pip install factor-factory[rdd,scm,het-te,dml,changepoint,stl,panel-reg,spatial,hawkes,climate,diffusion]
```

## Existing engine families — extensions

- `engines.did.sun_abraham` — Sun-Abraham (2021) IW estimator added.
- `engines.did.borusyak_jaravel_spiess` — BJS (2024) imputation estimator
  added (homegrown).
- `engines.survival.cox_ph` gained a `strata=` kwarg for stratified Cox PH.
- `engines.event_study.fama_french` — FF3/FF5/Carhart-4 market-model
  event study added.
- `engines.sdid.estimate(..., inference="placebo")` — placebo-test
  inference added (default remains `"jackknife"`).
- `MediationResult.sensitivity(rho_range, n_points)` — unobserved-
  confounding sensitivity analysis added.

## Contract snapshots

`docs/reference/contracts.md` pins `SNAPSHOT_VERSION = "1.0.0"` for the
Panel / Engine Protocol / Tearsheet JSON contracts. Any change that alters
these shapes must bump the snapshot version and log a `### Contracts` note
in `CHANGELOG.md`.

## Release automation

- PyPI publication via OIDC trusted-publisher — no stored tokens.
- Tags matching `v*` trigger `.github/workflows/release.yml`.
- `uv.lock` committed for reproducible installs.
- CI matrix expanded to ubuntu + macos + windows × py3.12 + py3.13.

## Deprecations

None in the v0.x → v1.0 journey. Breaking changes were deferred.

## Questions?

File an issue at https://github.com/random-walks/factor-factory/issues
with `migration:` in the title.
