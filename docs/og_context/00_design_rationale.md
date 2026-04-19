# Design rationale

## The pattern we observed

Writing three jellycell showcase projects in
[`blaise-website/packages/python-showcase/`](https://github.com/random-walks/blaise-website/tree/main/packages/python-showcase)
that consume both `nyc311` and `subway-access` surfaced an unmistakable
pattern. Every analysis pipeline — across both libraries, across all
three case studies — followed the same shape:

```
raw records
  ↓ tidying              dedup, geography join, period binning
tidied panel
  ↓ factor construction  volume, recurrence, HHI, resolution, reliability
factor panel
  ↓ diagnostics          distribution, missingness, outliers, balance, parallel-trends
diagnostic-annotated panel
  ↓ modeling             DiD / RDD / SCM / changepoint / STL / inequality / spatial / ...
modeling results
  ↓ reporting            tearsheets + manuscripts + checklists
```

And every consumer of that pattern (whether `nyc311.examples.case_studies.*`,
`subway-access.examples.*`, or one of the blaise-website showcases) had
to:

- Reimplement panel-building scaffolding with slightly different APIs
- Roll its own jellycell-friendly notebook conventions (cell-tag
  patterns, import boilerplate, figure handling)
- Hand-author the same four-document manuscript set (METHODOLOGY,
  DIAGNOSTICS_CHECKLIST, FINDINGS, MANUSCRIPT) per project
- Write its own multi-estimator comparison code when running multiple
  DiD variants — because nyc311 ships only one engine per stats method
- Fall back to manual implementations when a canonical external
  package wasn't usable (rddensity on pandas 2.x, rdrobust not
  integrated)

## The two consumers today, the future ones tomorrow

Today's consumers:

1. **`nyc311`** — Socrata 311 complaint analysis. Has:
   `nyc311.io`, `nyc311.temporal`, `nyc311.geographies`, `nyc311.stats`
   (a substantial homegrown stats module covering DiD, RDD, SCM,
   STL, changepoints, Theil, Oaxaca-Blinder, Moran's I, Hawkes, EM,
   BYM2). All single-engine implementations.

2. **`subway-access`** — MTA station accessibility analysis. Has:
   parallel-but-different versions of tidying + factor-construction +
   reliability-weighted coverage modeling. Independent stats stack.

Future consumers (planned or plausible):

- `nyc-mesh` (3D NYC source data → web-ready geodata) — will need
  the same tidy + geography layer
- `nyc-permits` / `nyc-housing` (DOB + ACS + rezoning analyses) —
  would benefit from the same factor-construction primitives
- Any consultancy / research-toolkit pattern that uses the same data
  shape (panel × time, treatment events, spatial weights)

Each new consumer that comes online today re-pays the cost of the
shared scaffolding. `factor-factory` extracts it once.

## Why a new package, not in-place refactoring

Three reasons:

### 1. The pattern is genuinely cross-cutting

If the pattern only appeared in one library, in-place refactoring
would be the right answer. It appears in two with near-identical
shape, and will almost certainly appear in any third. That's the
classical extract-shared-package signal.

### 2. The Protocol-based pluggable engine pattern is architecturally significant

The single largest improvement we want to make to the OSS stack is
**multi-engine support across every stats method** — DiD, RDD, SCM,
changepoint, STL, panel regression. Doing this in-place inside `nyc311`
means designing the Protocol pattern there, then re-doing it in
`subway-access`, then re-doing it in every future toolkit.

Doing it in `factor-factory` once means:
- One Protocol design, reused everywhere
- One `EngineRegistry` for downstream consumers to extend
- One conformance test pattern that catches regressions across all
  consumers
- Adding a new engine = one PR to one repo, available everywhere

### 3. The jellycell integration is the multiplier

Every showcase + example folder we've written has duplicated:

- The `# %% tags=["jc.setup"]` cell with imports
- The path-only figure-loading workaround for pre-rendered PNGs
- The four manuscript templates (METHODOLOGY etc.)
- The cell-cache footgun workaround (inline imports in every cell)
- The `pnpm showcase:*` wrapper script shape

Putting these in `factor_factory.jellycell.*` means:

- One `setup()` helper that workarounds the upstream jellycell bug
  (filed as `random-walks/jellycell` #J1 issue)
- One `figure.from_path()` that handles the pre-rendered case
  (jellycell #J2)
- Four template render functions for the manuscript set
- A `python -m factor_factory scaffold <name>` command that
  generates a working showcase skeleton in 5 seconds

That last one — the scaffold command — is the multiplier. Going
from "I want to write a new analysis showcase" to "I have a
working notebook" is currently a half-day exercise (lots of
manuscript boilerplate, jellycell.toml setup, gitignore tweaks).
With factor-factory's scaffold it should be a coffee-break exercise.

## Alternatives considered

### A. Keep iterating in-place on `nyc311` + `subway-access`

The path of least resistance. Adds multi-engine support to each
package's stats module. Pros: less coordination, no new repo.
Cons: every new toolkit re-pays the cost; jellycell integration
stays scattered; no scaffold command.

**Verdict**: works for one more case study, breaks down at three.

### B. A narrower package — `nyc-tidy` covering only the tidy/geography layer

Smaller scope, easier to ship. Pros: incremental. Cons: doesn't
solve the multi-engine problem; doesn't bake jellycell in;
gives us 30% of the benefit for 50% of the work.

**Verdict**: shallow.

### C. A wider package — `random-walks-stack` doing tidying + engines + jellycell + UI components

Maximally ambitious. Pros: one dep to rule them all. Cons:
domain-coupling drift; harder to version; harder for outsiders to
adopt (they want one piece, not the whole stack).

**Verdict**: too wide.

### D. The chosen scope: `factor-factory`

Tidying + factors + diagnostics + pluggable engines + first-class
jellycell. Domain-agnostic. Outside consumers (anyone doing
panel-data + treatment-event analysis with jellycell) can adopt
without inheriting NYC-specific assumptions.

## What this is NOT trying to be (anti-goals)

Documented explicitly because scope-creep is the highest risk:

- **Not a Bayesian framework.** We adapt PyMC or `bayesloop` for
  Bayesian engines but don't pick a side.
- **Not a one-stop econometrics package.** We don't reimplement
  what `linearmodels`, `rdrobust`, `pysyncon`, etc. already do —
  we adapt them with consistent result dataclasses.
- **Not a viz library.** We use matplotlib + seaborn + plotnine.
  We ship factor-specific helpers (parallel-trends plot, balance
  plot) but not a chart library.
- **Not a data-loading toolkit.** We adapt Socrata / Census /
  geographic data through plug-in adapters; the loading primitives
  themselves stay domain-specific in `nyc311` / `subway-access`.
- **Not a CI/MLOps platform.** Reproducibility comes from
  jellycell + uv + lockfiles, not from a custom orchestrator.

## Why now

Three reasons:

1. **We have three concrete consumers** (the blaise-website
   showcases) plus two existing libraries (`nyc311`, `subway-access`)
   that have surfaced the pattern unambiguously.
2. **No one is currently consuming the upstream packages downstream
   of the author** — major-version bumps in `nyc311` / `subway-access`
   are low-cost. If we wait until they have external users,
   coordinated migration becomes harder.
3. **Jellycell 1.3.x ships the conventions we want to standardize
   against.** Rebuilding showcases against jellycell + factor-factory
   produces a canonical pattern future contributors can learn from
   one place rather than reverse-engineer from scattered examples.
