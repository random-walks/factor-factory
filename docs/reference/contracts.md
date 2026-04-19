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
    method: str              # "twfe" | "cs"
    att: float
    se: float
    ci_95: tuple[float, float]
    p_value: float
    n: int
    cohort_atts: dict[int, float] | None = None
    cohort_ses: dict[int, float] | None = None
    diagnostics: dict[str, Any] | None = None
    meta: dict[str, Any] | None = None  # excluded from to_dict()


class DidEngine(Protocol):
    name: str
    def fit(
        self,
        panel: Panel,
        *,
        outcome: str,
        treatment: str = "treatment",
        cluster: str | None = None,
        **kwargs: Any,
    ) -> DidResult: ...
```

### Survival

```python
@dataclass(frozen=True)
class SurvivalResult:
    method: str              # "kaplan_meier" | "cox_ph"
    median_survival: float | None
    n_subjects: int
    n_events: int
    coefficients: dict[str, float] | None = None
    hazard_ratios: dict[str, float] | None = None
    p_values: dict[str, float] | None = None
    confidence_intervals: dict[str, tuple[float, float]] | None = None
    survival_curve: pd.DataFrame | None = None
    proportional_hazards_test: dict[str, float] | None = None
    diagnostics: dict[str, Any] | None = None
    meta: dict[str, Any] | None = None
```

### Event Study

```python
@dataclass(frozen=True)
class EventStudyResult:
    method: str              # "market_adjusted" | "fama_french"
    n_events: int
    average_abnormal_return: float
    car_event_window: float
    car_se: float
    car_t_stat: float
    car_p_value: float
    abnormal_return_curve: pd.DataFrame | None = None
    per_unit_car: dict[str, float] | None = None
    estimation_window: tuple[int, int] | None = None
    event_window: tuple[int, int] | None = None
    diagnostics: dict[str, Any] | None = None
    meta: dict[str, Any] | None = None
```

### SDID

```python
@dataclass(frozen=True)
class SdidResult:
    method: str              # "sdid"
    att: float
    se: float
    p_value: float
    n: int
    unit_weights: dict[Any, float] | None = None
    time_weights: dict[Any, float] | None = None
    n_treated: int | None = None
    n_control: int | None = None
    n_pre: int | None = None
    n_post: int | None = None
    diagnostics: dict[str, Any] | None = None
    meta: dict[str, Any] | None = None
```

### Mediation

```python
@dataclass(frozen=True)
class MediationResult:
    method: str              # "four_way"
    n_subjects: int
    treatment: str
    mediator: str
    outcome: str
    total_effect: float
    cde: float
    int_ref: float
    int_med: float
    pie: float
    decomposition_residual: float
    total_effect_se: float | None = None
    cde_se: float | None = None
    int_ref_se: float | None = None
    int_med_se: float | None = None
    pie_se: float | None = None
    confidence_intervals: dict[str, tuple[float, float]] | None = None
    proportion_eliminated: float | None = None
    proportion_mediated: float | None = None
    diagnostics: dict[str, Any] | None = None
    meta: dict[str, Any] | None = None
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
