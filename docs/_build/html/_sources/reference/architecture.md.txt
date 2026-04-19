# Architecture

The 6-layer pipeline. Higher layers import lower layers; never the reverse.

```
raw records
  ↓ tidying              factor_factory.tidy        (Panel + TreatmentEvent + Provenance + RecordView)
tidied panel
  ↓ factor construction  factor_factory.factors     (volume, recurrence, HHI, resolution, reliability — Phase 2)
factor panel
  ↓ diagnostics          factor_factory.diagnostics (SMD, parallel trends, residuals, balance)
diagnostic-annotated panel
  ↓ modeling             factor_factory.engines     (did / survival / event_study / sdid / mediation + 13 more v0.2+)
modeling results
  ↓ reporting            factor_factory.jellycell   (5 tearsheet renderers + scaffold CLI)
```

## Dependency order

The layers map onto a strict import order. `factor_factory.tidy` imports only stdlib + pandas + numpy + pyarrow + pydantic. `factor_factory.diagnostics` may import `tidy` but not `engines`. `factor_factory.engines.<family>` may import `tidy` + `diagnostics` + the family's optional upstream package. `factor_factory.jellycell` may import any of them.

The engine registry pattern means `engines.__init__` **does not** transitively import every family's upstream package. Each family's `__init__.py` has a try/except around the adapter imports so a missing extra dep fails gracefully (registry has fewer entries) rather than breaking unrelated code.

## Engine-family shape (the Protocol contract)

Every family under `factor_factory.engines.<family>/` follows the same shape:

```
engines/<family>/
├── __init__.py           # exports estimate, <Family>Result, <Family>Results, registry
├── _base.py              # <Family>Result dataclass + <Family>Engine Protocol + registry
├── <adapter_1>.py        # first adapter (e.g. twfe.py)
├── <adapter_2>.py        # second adapter (optional)
└── ...
```

The frozen `<Family>Result` dataclass is the Tearsheet JSON contract. The `<Family>Engine` Protocol is the Engine Protocol contract. Both are locked per [§0.2](../og_context/06_post_v0.1_roadmap.md#02-contract-invariants-lock-these-before-we-scale) of the roadmap.

## Piggyback-first

See [`reference/piggyback-map.md`](piggyback-map.md). Factor-factory wraps mature upstream packages; we port from scratch only when no maintained Python equivalent exists. Two current anti-piggybacks: `engines.sdid` (Arkhangelsky 2021) and `engines.mediation` (VanderWeele 2014).

## The jellycell boundary

Factor-factory produces JSON-serializable `Result.to_dict()` outputs. The jellycell integration layer (`factor_factory.jellycell`) reads these JSONs and renders 5 canonical manuscripts (METHODOLOGY, DIAGNOSTICS_CHECKLIST, FINDINGS, MANUSCRIPT, AUDIT). The JSON shape is the **Tearsheet JSON contract** — adding keys is additive, renaming or removing is breaking.

## What's deliberately NOT in the architecture

- **Streaming engine fits** — all estimators assume the Panel fits in memory. `Panel.from_records` streaming (Batch 13) is the data-loading side; engine fits stay in-memory.
- **Distributed execution** — factor-factory is a single-machine tool. Scale out via the domain layer (pre-aggregate upstream, feed a smaller Panel in).
- **Model serving / inference endpoints** — out of scope; use a downstream FastAPI/MLflow project.
- **GUI** — the jellycell viewer is the UI. No standalone factor-factory GUI.
