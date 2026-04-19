# Contract snapshots

This file is the **gate** for the three factor-factory contract invariants. Any change that alters the shape documented here requires a `SNAPSHOT_VERSION` bump + a CHANGELOG `### Contracts` note.

Current snapshot: **`SNAPSHOT_VERSION = "1.0.0"`** (frozen at first stable release — Batch 3).

## Contract 1 — Panel

Full prose: [`design-contracts.md`](../design-contracts.md).

Invariant summary:

- **Columns, in order**: `unit_id`, `period`, `<outcome_col>` (or `<outcome_col_1>`, `<outcome_col_2>`, ...), `weight` (optional), per-event treatment columns, `<user-supplied passthrough columns>`.
- **`period_kind`** ∈ `{"timestamp", "integer", "float"}`.
- **Treatment columns**, per `TreatmentEvent` (let `e` be the event name):
  - `treated_<e>` — bool: this row is in a treated unit
  - `post_<e>` — bool: this row is at or after the treatment date
  - `treatment_<e>` — bool (binary events) OR float (continuous) OR category (multi-arm)
  - `arm_<e>` (only for categorical events): the treatment-arm string
- **Provenance** (`Panel.provenance`): `source`, `fetched_at`, `notes`, `annotations: dict[str, Any]`. The `annotations` dict is the free-form slot for things like `ground_truth_att`.
- **Validation**: `Panel.validate()` runs on construction. Cost is O(n) in the record count. Batch 4 adds `validate(strict=False)` for a fast-path that skips O(n) checks.

## Contract 2 — Engine Protocol

Full prose: [`../og_context/03_specs/engine_protocol.md`](../og_context/03_specs/engine_protocol.md).

Every `<Family>` shipping today:

### DiD

```python
@dataclass(frozen=True)
class DidResult:
    estimate: float
    std_error: float
    method: str          # "twfe" | "cs"
    cluster: str | None
    n_treated: int
    n_control: int
    extra: dict[str, Any]

class DidEngine(Protocol):
    def estimate(self, panel: Panel, **kwargs: Any) -> DidResult: ...
```

### Survival

```python
@dataclass(frozen=True)
class SurvivalResult:
    method: str          # "kaplan_meier" | "cox_ph"
    survival_function: pd.DataFrame | None
    hazard_ratios: dict[str, float] | None
    confidence_interval: pd.DataFrame | None
    extra: dict[str, Any]
```

### Event Study

```python
@dataclass(frozen=True)
class EventStudyResult:
    method: str          # "market_adjusted" | "fama_french"
    abnormal_returns: pd.DataFrame
    car: pd.Series
    t_stat: float
    p_value: float
    extra: dict[str, Any]
```

### SDID

```python
@dataclass(frozen=True)
class SdidResult:
    att: float
    std_error: float
    inference: str       # "jackknife" | "placebo"
    unit_weights: pd.Series
    time_weights: pd.Series
    extra: dict[str, Any]
```

### Mediation

```python
@dataclass(frozen=True)
class MediationResult:
    cde: float
    int_ref: float
    int_med: float
    pie: float
    std_errors: dict[str, float]
    confidence_intervals: dict[str, tuple[float, float]]
    outcome_family: str   # "linear" | "logistic" (Batch 5)
    mediator_family: str  # "linear" | "logistic" (Batch 5)
    extra: dict[str, Any]
```

## Contract 3 — Tearsheet JSON

Each engine family emits a JSON file consumed by jellycell templates:

- `did_results.json` — one object per adapter fit, list
- `survival_results.json` — one object per adapter fit, list
- `event_study_results.json` — one object per adapter fit, list
- `sdid_results.json` — one object per adapter fit, list
- `mediation_results.json` — one object per adapter fit, list

The schema for each is `Result.to_dict()` output. Additive keys are safe; renaming or removing is breaking.

## Ceremony on touch

1. Change `<Family>Result` or `<Family>Engine` Protocol.
2. Update the block above.
3. Bump `SNAPSHOT_VERSION` (patch for additive, minor for new family, **major for breaking**).
4. CHANGELOG `### Contracts` note referencing this snapshot.
5. For breaking changes: RFC under `docs/og_context/rfcs/<slug>.md`.

The `contract-auditor` Claude agent checks this automatically on `/contract-check`.
