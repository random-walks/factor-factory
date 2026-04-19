# Downstream changes

What `nyc311`, `subway-access`, and downstream showcase suites must
do once factor-factory v1.0 ships. Read this once factor-factory is
at v0.4+ (Phase 2 in flight) and you're starting to plan downstream
adoption.

## Summary

Three downstream consumers, each with a specific migration plan:

| Consumer | What changes | When |
|---|---|---|
| `random-walks/nyc311` | Add factor-factory dep; deprecate homegrown `nyc311.stats.*` behind warnings; port one example folder fully | Phase 4 (factor-factory v0.5+) |
| `random-walks/subway-access` | Same pattern: add dep, port one example folder, deprecate stats | Phase 4 |
| Downstream showcase suites | Rewrite the dogfood-target showcase projects against factor-factory | Phase 3 (parallel with late Phase 2) |

## `nyc311` migration

### Before factor-factory

`nyc311.stats` is a substantial homegrown stats module:

- `staggered_did` (Callaway-Sant'Anna only)
- `synthetic_control` (Abadie original only)
- `regression_discontinuity` (homegrown local-poly)
- `seasonal_decompose` (statsmodels wrapper)
- `detect_changepoints` (ruptures wrapper)
- `theil_index`, `oaxaca_blinder_decomposition`
- `global_morans_i`, `local_morans_i`, `spatial_lag_model`
- `latent_reporting_bias_em`
- `fit_hawkes_process`
- `bym2_smooth`
- `panel_fixed_effects`, `panel_random_effects`
- `geographically_weighted_regression`

Plus a thin tidy layer (`nyc311.io`, `nyc311.temporal`,
`nyc311.geographies`) that overlaps with what factor-factory ships.

### After factor-factory v1.0

#### Phase 4 — soft migration (~minor version bump)

Add `factor-factory>=0.5` as a dep. Update `nyc311.stats.*`
functions to be **thin backwards-compat wrappers** that delegate
to factor-factory adapters:

```python
# nyc311/stats/__init__.py (post-migration)
import warnings
from factor_factory.engines.did import estimate as ff_estimate_did

def staggered_did(*args, **kwargs):
    warnings.warn(
        "nyc311.stats.staggered_did is deprecated. "
        "Use factor_factory.engines.did.estimate(panel, methods=('cs',), ...) "
        "instead. This wrapper will be removed in nyc311 1.0.",
        DeprecationWarning,
        stacklevel=2,
    )
    # Adapt the old-style args to the new estimate() call
    return ff_estimate_did(...)
```

Same for every other function in `nyc311.stats`.

The tidy layer (`nyc311.io`, `temporal`, `geographies`) gets a
similar treatment:

```python
# nyc311/temporal/__init__.py (post-migration)
def build_complaint_panel(*args, **kwargs):
    warnings.warn(
        "nyc311.temporal.build_complaint_panel is deprecated. "
        "Use factor_factory.tidy.Panel.from_records(...) with the "
        "nyc311 SocrataAdapter instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    # Delegate to factor-factory's Panel.from_records
    ...
```

`nyc311.io.load_service_requests` stays as a domain-specific helper
(it knows about NYC 311's CSV schema). It returns
`ServiceRequestRecord` objects that factor-factory's
`Panel.from_records` consumes.

Port `nyc311/examples/case_studies/rat_containerization` to use
factor-factory directly — this is the dogfood signal that the
deprecation shims are sufficient.

Bump nyc311 to a minor version (e.g., `0.4.0` if currently
`0.3.x`) reflecting the new dep + deprecations.

#### Phase 5 — major-version bump

`nyc311 1.0.0`: drop the deprecated wrappers. `factor-factory`
becomes a hard dep. Document the migration path in the CHANGELOG.

End state: `nyc311` is a thin domain-specific package owning:

- `nyc311.io.NYC311SocrataAdapter` (Socrata adapter for the 311 dataset)
- `nyc311.io.ServiceRequestRecord` (the schema)
- `nyc311.geographies.NYCGeographyAdapter` (NYC-specific boundaries)
- `nyc311.examples/` (case studies showing factor-factory usage)
- `nyc311.factors.*` (NYC-311-specific factor definitions if any —
  most are domain-agnostic enough to live in factor-factory)

The bulk of the original code (the `stats` module) is gone.

## `subway-access` migration

Same shape as nyc311 but smaller surface area. The package's
homegrown stats stack is parallel-but-not-identical to nyc311's;
factor-factory unifies them.

#### Phase 4 — soft migration

Add factor-factory dep. Wrap the homegrown stats with deprecation
warnings. Port `subway-access/examples/accessibility-change-over-time`
to use factor-factory's Panel + DiD + Moran's I + RDD adapters.

Reliability-weighted coverage modeling (the subway-specific factor)
stays in `subway-access`'s factor module — but the framework
scaffolding (panel building, diagnostic helpers, tearsheet
generation) all moves to factor-factory.

#### Phase 5 — major bump

`subway-access 1.0.0`: drop the wrappers. End state mirrors nyc311.

## Downstream showcase migration

This happens DURING Phase 3 (parallel with late Phase 2 of
factor-factory's engine fan-out). Once factor-factory hits v0.4
(DiD + RDD + SCM available), rewrite the three dogfood showcases:

### Rat containerization showcase

The biggest win — most stats. Expected changes:

- `_helpers.py` shrinks to ~30 lines (just the NYC311 adapter
  registration + treatment-event definition)
- Main-effects notebook: becomes ~50% shorter — multi-engine DiD via
  `factor_factory.engines.did.estimate(panel, methods=("twfe", "cs", "sa", "bjs"))`
- Diagnostics notebook: residual diagnostics via
  `factor_factory.diagnostics.residual_diagnostics`; bootstrap CIs
  via `factor_factory.diagnostics.block_bootstrap` (new helper)
- Robustness notebook: HTE / placebo / seasonal-demeaned patterns
  formalized as factor-factory diagnostic helpers
- RDD + spatial notebook: RDD via
  `factor_factory.engines.rdd.rdrobust`; spatial-lag DiD via
  `factor_factory.engines.spatial.spatial_lag`
- Extended robustness notebook: MDE via
  `factor_factory.diagnostics.mde`; multi-year pretrends via
  `factor_factory.diagnostics.multi_year_parallel_trends`;
  reporting-bias EM via
  `factor_factory.engines.reporting_bias.latent_em` (with the
  identification-constraint doc baked in)
- Manuscripts: `METHODOLOGY.md`, `DIAGNOSTICS_CHECKLIST.md`,
  `FINDINGS.md` all auto-generated via
  `factor_factory.jellycell.tearsheets.*`. Only `MANUSCRIPT.md`
  stays hand-authored.

Expected line count: ~50% reduction across the notebook source +
elimination of the four hand-authored manuscript scaffolds.

### Resolution equity showcase

Similar reduction. The synthetic-panel synthesizer in `_helpers.py`
goes away — replaced by factor-factory's
`Panel.from_records(records, ..., synthesize_periods=24)` (or a
similar opt-in extension method).

The Moran's I sensitivity sweep, Theil decomposition,
Oaxaca-Blinder all become single-line calls into
factor-factory's engines.

### Subway accessibility showcase

Smallest delta — verbatim mirror, mostly tearsheet-template
adoption. The five notebooks become essentially:

```python
# %% tags=["jc.load", "name=panel"]
from factor_factory.jellycell.cells import setup
from factor_factory.jellycell.figure import from_path
ns = setup()
jc, pd, np, Image = ns["jc"], ns["pd"], ns["np"], ns["Image"]

# %% tags=["jc.figure", "name=fig1"]
from_path("artifacts/figures/figure-1.png",
          caption="Coverage rate by borough")
```

Cleaner than the current `Image("...")` pattern.

## Future toolkits

Any new toolkit (`nyc-mesh`, `nyc-permits`, hypothetical `chicago-311`)
inherits the framework for free. The bootstrap experience:

```bash
mkdir my-new-toolkit
cd my-new-toolkit
uv init
uv add factor-factory[all]

# Write your domain adapter (e.g., your_toolkit/io.py with a SocrataAdapter
# implementation specific to your data source)

# Use factor-factory's scaffold to spin up an example folder:
python -m factor_factory scaffold my-first-analysis
```

In ~30 minutes, a new toolkit author has a working example folder
with the canonical jellycell + factor-factory conventions in place.
That's the multiplier this whole effort buys.

## Backwards-compatibility timeline

| Date | factor-factory | nyc311 | subway-access |
|---|---|---|---|
| Today | n/a | v0.3.x (homegrown stats) | v0.x (homegrown stats) |
| End of Phase 1 | v0.1 (skeleton) | unchanged | unchanged |
| End of Phase 2 | v0.10 (full engines) | unchanged | unchanged |
| Phase 3 mid | v0.10 + showcase rewrites done | unchanged | unchanged |
| Phase 4 start | v1.0 (or wait until consumers stabilize) | v0.4 (deprecated wrappers) | v0.x+1 (deprecated wrappers) |
| Phase 5 | v1.x (stable SemVer) | v1.0 (drops wrappers) | v1.0 (drops wrappers) |

End-users on `nyc311 < 1.0` keep working code. Migration is
opt-in via `import factor_factory` until they're ready.

## Open questions

- **Naming compatibility**: factor-factory's `Panel` vs.
  `nyc311.temporal.PanelDataset`. The deprecation shim should
  accept either name. Default: factor-factory uses `Panel`;
  PanelDataset becomes a deprecated alias in `nyc311`.
- **Result-object compatibility**: nyc311's `StaggeredDiDResult`
  vs. factor-factory's `DidResult`. Different fields. The
  deprecation shim translates one into the other; document the
  field mapping in nyc311's CHANGELOG.
- **Public-API surface in nyc311 1.0**: how thin should it get?
  Default: nyc311 1.0 is JUST the domain adapter +
  ServiceRequestRecord schema + example folders. Everything else
  is factor-factory.
