"""Canonical synthetic panels used by every engine conformance test.

Three primary fixtures (small effect, null effect, large effect with
spillover) plus an intentionally-invalid one for ``validate()`` error
paths.

All fixtures use a fixed RNG seed so engine tests have reproducible
ground truth.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ...tidy import Panel, TreatmentEvent
from ...tidy.contracts import PanelMetadata

_SEED = 20260419
_N_UNITS = 50
_N_PERIODS = 24
_TREATMENT_PERIOD_INDEX = 12  # half pre, half post


def _build(
    *,
    att: float,
    noise: float = 1.5,
    spillover: float = 0.0,
    null_treatment: bool = False,
    seed: int = _SEED,
) -> Panel:
    """Build a synthetic balanced panel with a known ATT."""
    rng = np.random.default_rng(seed)
    units = [f"unit-{i:02d}" for i in range(_N_UNITS)]
    periods = pd.date_range("2023-01-31", periods=_N_PERIODS, freq="ME")
    treatment_date = periods[_TREATMENT_PERIOD_INDEX].date()
    treated_units = tuple(units[: _N_UNITS // 2])
    spillover_units = tuple(units[_N_UNITS // 2 : _N_UNITS // 2 + 5])

    rows: list[dict[str, object]] = []
    for unit in units:
        unit_fe = float(rng.normal(0.0, 1.0))
        is_treated = unit in treated_units
        is_spillover = unit in spillover_units
        for i, p in enumerate(periods):
            time_fe = 0.05 * i
            base = 10.0 + unit_fe + time_fe + rng.normal(0.0, noise)
            post = i >= _TREATMENT_PERIOD_INDEX
            effect = 0.0
            if not null_treatment:
                if is_treated and post:
                    effect = att
                if is_spillover and post:
                    effect = spillover
            outcome = base + effect
            rows.append({"unit_id": unit, "period": p, "outcome": float(outcome)})

    df = pd.DataFrame(rows).set_index(["unit_id", "period"]).sort_index()

    metadata = PanelMetadata(
        geography="synthetic_unit",
        freq="ME",
        treatment_events=(
            TreatmentEvent(
                name="synthetic_treatment",
                treated_units=treated_units,
                treatment_date=treatment_date,
                geography="synthetic_unit",
            ),
        ),
        outcome_col="outcome",
        record_count=len(rows),
    )

    # Attach treatment columns the same way Panel.from_records would
    from ...tidy.panel import _attach_treatment_columns

    df = _attach_treatment_columns(df, metadata.treatment_events)

    return Panel(df, metadata)


def small_treatment_effect_panel() -> Panel:
    """50 units × 24 months, ATT = 5.0, low noise."""
    return _build(att=5.0, noise=1.0)


def null_effect_panel() -> Panel:
    """Same shape as small_treatment_effect_panel but ATT = 0."""
    return _build(att=0.0, noise=1.0, null_treatment=True, seed=_SEED + 1)


def large_treatment_effect_with_spillover_panel() -> Panel:
    """Same shape, ATT = 20.0, treated units' five neighbors also see effect."""
    return _build(att=20.0, noise=1.5, spillover=8.0, seed=_SEED + 2)


def unbalanced_panel() -> pd.DataFrame:
    """Intentionally invalid (returns the raw DataFrame, not a Panel).

    Used to exercise ``Panel.validate()`` error paths.
    """
    base = small_treatment_effect_panel().df
    return base.iloc[:-3]  # drop last 3 rows: now unbalanced


__all__ = [
    "large_treatment_effect_with_spillover_panel",
    "null_effect_panel",
    "small_treatment_effect_panel",
    "unbalanced_panel",
]
