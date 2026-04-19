# factor-factory

A shared factor-model + analysis-pipeline framework for the
`random-walks` NYC OSS ecosystem (`nyc311`, `subway-access`, and
sibling toolkits), with **first-class jellycell integration**.

## Status

`v0.1.0` — **Phase 1 skeleton + first DiD engine + jellycell MVP**.
The tidy / diagnostics / jellycell layers ship today; engine fan-out
(Callaway-Sant'Anna, rdrobust, pysyncon, ruptures, …) lands in
v0.2+ per the [implementation plan](docs/og_context/02_implementation_plan.md).
The complete design rationale, API specs, and roadmap live in
[`docs/og_context/`](docs/og_context/).

User docs:
- [`docs/getting-started.md`](docs/getting-started.md) — install,
  build a Panel, run a DiD, render manuscripts.
- [`docs/jellycell-integration.md`](docs/jellycell-integration.md) —
  cell conventions, the upstream-bug workarounds, the `scaffold`
  command.

## What it does (elevator pitch)

```
raw records
  ↓ tidying              factor_factory.tidy   (Socrata + ACS + geography + period binning)
tidied panel
  ↓ factor construction  factor_factory.factors  (volume, recurrence, HHI, resolution, reliability)
factor panel
  ↓ diagnostics          factor_factory.diagnostics  (SMD, parallel-trends, residuals, balance)
diagnostic-annotated panel
  ↓ modeling             factor_factory.engines       (DiD / RDD / SCM / changepoint / STL / inequality / spatial / ...)
modeling results
  ↓ reporting            factor_factory.jellycell    (tearsheets + four canonical manuscripts + scaffold cmd)
```

Both `nyc311` and `subway-access` re-implement slices of this pipeline
with slightly different APIs. `factor-factory` extracts the shared
scaffolding so new toolkits inherit it for free, and adopts a
**Protocol-based pluggable-engine pattern** so multiple canonical
implementations (Callaway-Sant'Anna, rdrobust, pysyncon, ruptures,
...) all return comparable result dataclasses.

## Quick start

```bash
pip install factor-factory[did]              # default + linearmodels (TWFE engine)

# scaffold a new showcase against jellycell
python -m factor_factory scaffold my-showcase
cd my-showcase
python notebooks/01_load.py                  # builds a synthetic panel + runs DiD + renders manuscripts

# inside a notebook
from factor_factory.jellycell.cells import setup
ns = setup(also=("matplotlib.pyplot as plt",))
jc, pd, np, plt, Image = ns["jc"], ns["pd"], ns["np"], ns["plt"], ns["Image"]

from factor_factory.tidy import Panel, TreatmentEvent
from factor_factory.engines.did import estimate

panel = Panel.from_records(records, geography="community_district", freq="ME",
                            treatment_events=(TreatmentEvent(...),))
results = estimate(panel, methods=("twfe",),                       # v0.1: twfe only
                   outcome="complaint_count", cluster="unit_id")   # v0.2+: ("twfe","cs","sa","bjs")
print(results.summary_table())
```

## Where to start (for new agents)

1. **Read** [`docs/og_context/README.md`](docs/og_context/README.md) — orientation
2. **Read in order:**
   - `00_design_rationale.md` — why this exists
   - `01_architecture.md` — directory layout + Protocol pattern
   - `02_implementation_plan.md` — phase-by-phase roadmap with acceptance gates
3. **Pick a spec** in `03_specs/` and start there
4. **Reference** `04_downstream_changes.md` to understand what consumers
   will need after factor-factory ships
5. **Use** `05_rfc_template.md` when starting a new engine-family RFC

## License

MIT — same as sibling random-walks packages.
