# Spec: Panel contract

The `factor_factory.tidy.Panel` is the central data structure that
every layer of the framework consumes and produces. This spec pins
its schema, invariants, and lifecycle.

## Schema

`Panel` wraps a `pandas.DataFrame` with a **strict** structure:

### Index

`MultiIndex(unit_id: str, period: pd.Timestamp)` — required.

- `unit_id`: opaque string identifier for the analytic unit
  (community district, station, tract, etc.). Stable across periods.
- `period`: month-end timestamp by default; configurable via
  `freq` parameter on construction.

### Required columns

- `outcome` (float64): the analytic target. Names like
  `complaint_count`, `coverage_pct`, etc. — the spec doesn't pin
  the column name, just that one column is designated `outcome` via
  `Panel.outcome_col` attribute.

### Framework-aware columns (optional but conventional)

The framework treats these specially when present:

- `treatment` (int8, 0/1): binary treatment indicator (`1` if unit
  is treated AND period >= treatment_date)
- `treated_unit` (int8, 0/1): time-invariant unit-level treatment
  membership (`1` for any unit in `treated_units`)
- `post` (int8, 0/1): time-only post-treatment indicator (period >=
  treatment_date)
- `population` (int): unit population, used for population-weighted
  analyses (Theil index, etc.)

When any of these are missing, the framework falls back to:
- `treatment` is computed on demand from `treated_unit × post` if
  both are present
- `population` analyses are unavailable; they raise a clear error

### Free-form factor columns

Beyond the framework-aware columns above, any number of float64
columns can live on the panel as factors. By convention, factor
columns are NOT prefixed (no `factor_*` namespace). The factor name
IS the column name.

## Pydantic schema

```python
# factor_factory/tidy/contracts.py
from datetime import date
from typing import Annotated, Literal
from pydantic import BaseModel, Field
import pandas as pd

class TreatmentEvent(BaseModel, frozen=True):
    """A single treatment event applied to a specified set of units."""
    name: str
    description: str = ""
    treated_units: tuple[str, ...]
    treatment_date: date
    geography: Literal["community_district", "tract", "station"]

class PanelMetadata(BaseModel, frozen=True):
    """Provenance and structure metadata for a Panel."""
    geography: Literal["community_district", "tract", "station"]
    freq: str  # pandas freq string: "ME" (month-end), "QE" (quarter-end), etc.
    treatment_events: tuple[TreatmentEvent, ...] = ()
    outcome_col: str
    record_count: int  # raw record count before tidying
```

The `Panel` class wraps a DataFrame + metadata:

```python
# factor_factory/tidy/panel.py
import pandas as pd
from .contracts import PanelMetadata, TreatmentEvent
from .record_view import RecordView

class Panel:
    """Tidied panel: MultiIndex(unit_id, period) DataFrame + metadata."""

    def __init__(self, df: pd.DataFrame, metadata: PanelMetadata,
                 record_view: RecordView | None = None):
        self.df = df
        self.metadata = metadata
        self._record_view = record_view
        self.validate()

    @property
    def outcome_col(self) -> str:
        return self.metadata.outcome_col

    @property
    def record_view(self) -> RecordView:
        """Companion lat/lon-preserving view. Required for record-level RDD."""
        if self._record_view is None:
            raise ValueError(
                "This Panel was built without record_view=True. "
                "Re-run Panel.from_records(..., record_view=True) for "
                "lat/lon-preserving views."
            )
        return self._record_view

    @classmethod
    def from_records(cls,
                     records,
                     *,
                     geography: str,
                     freq: str = "ME",
                     treatment_events: tuple[TreatmentEvent, ...] = (),
                     outcome_col: str = "complaint_count",
                     record_view: bool = False) -> "Panel":
        """Build a balanced panel from a sequence of records."""
        ...

    def validate(self) -> None:
        """Raise ValueError if the panel violates any invariant."""
        # see Invariants below
        ...

    def to_dataframe(self) -> pd.DataFrame:
        """Returns the underlying DataFrame. Mutating it bypasses validation."""
        return self.df.copy()
```

## Invariants

`Panel.validate()` raises on any of:

1. **Index shape**: must be `MultiIndex(unit_id: str, period: pd.Timestamp)`.
   No duplicates. No nulls in either level.
2. **Balanced**: every `unit_id` has the same set of periods (cartesian
   product). Missing cells fail validation. Use `Panel.balance(fill_value=...)`
   to opt-in to filling.
3. **Outcome present**: `outcome_col` must exist as a float64 column.
4. **Period sorted**: index sorted by `unit_id` first, then `period`.
5. **Treatment consistency**: if any of `treatment` / `treated_unit` /
   `post` are present, they must be consistent with each other AND with
   `metadata.treatment_events` if any.
6. **No NaN in framework columns**: `treatment`, `treated_unit`, `post`
   columns are int8 with no nulls.

## Companion `RecordView`

For analyses that need individual-record lat/lon (record-level RDD,
within-unit spatial heterogeneity), the `Panel` carries an optional
companion `RecordView`:

```python
# factor_factory/tidy/record_view.py
from dataclasses import dataclass
import pandas as pd

@dataclass(frozen=True)
class RecordView:
    """Per-record DataFrame retaining lat/lon, period, unit_id."""
    df: pd.DataFrame  # columns: latitude, longitude, unit_id, period, ...
    schema_version: int = 1

    def filter(self, *, period_start=None, period_end=None,
               unit_ids=None) -> "RecordView":
        """Sub-select records by period range or unit ID set."""
        ...

    def distance_to_boundary(self, boundary, *, signed=True) -> pd.Series:
        """Compute haversine distance from each record to a boundary polygon.
        Used as the running variable for record-level RDD."""
        ...
```

## Construction patterns

```python
# Basic: aggregated panel only
panel = Panel.from_records(
    records,
    geography="community_district",
    freq="ME",
    outcome_col="complaint_count",
)

# With treatment event
panel = Panel.from_records(
    records,
    geography="community_district",
    freq="ME",
    outcome_col="complaint_count",
    treatment_events=(TreatmentEvent(
        name="rat_containerization_pilot",
        treated_units=("MANHATTAN 01", "MANHATTAN 02", ...),
        treatment_date=date(2024, 6, 1),
        geography="community_district",
    ),),
)

# With record view (enables record-level RDD)
panel = Panel.from_records(
    records,
    geography="community_district",
    freq="ME",
    outcome_col="complaint_count",
    record_view=True,
)
```

## Loading from disk

```python
# Save: writes panel.parquet + .meta.json sidecar
panel.to_parquet("data/panel.parquet")

# Load: reconstructs the metadata
panel = Panel.from_parquet("data/panel.parquet")
```

The `.meta.json` sidecar holds the `PanelMetadata` so loading is
lossless.

## Performance expectations

- `Panel.from_records` should handle ~1M records in <30s on a laptop.
  Beyond that, recommend a chunked builder pattern (TODO: implement
  in v0.2 if needed).
- `Panel.validate()` should be O(n) on the row count; <100ms for
  typical panels (~1000 cells).

## Test fixtures

`factor_factory/tests/_fixtures/synthetic_panels.py` exposes:

- `small_treatment_effect_panel()` — 50 units × 24 months,
  ATT = 5.0, low noise
- `null_effect_panel()` — same shape, ATT = 0, treatment indicator
  random
- `large_treatment_effect_with_spillover_panel()` — same shape,
  ATT = 20.0, treated units' neighbors also see effect (for
  spatial-lag testing)
- `unbalanced_panel()` — intentionally invalid, used to test
  `validate()` error paths

Every engine conformance test runs against all relevant fixtures.

## Open questions

- **Multi-treatment events**: panels with more than one
  `TreatmentEvent` (staggered rollout, multiple policies) — how does
  the `treatment` column decompose? Default: separate
  `treatment_<event_name>` columns. Confirm during Phase 1
  implementation.
- **Continuous treatment**: do we support panels where `treatment`
  is float (intensity, dose)? Defer to Phase 2; v0.1 = binary only.
- **Time-varying covariates**: how are time-varying ACS-style
  controls represented? Default: as additional float columns on the
  panel; engines that consume them check for column presence.
