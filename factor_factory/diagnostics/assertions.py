"""Structural integrity checks usable as defensive guardrails in notebooks."""

from __future__ import annotations

import pandas as pd

from ..tidy.panel import Panel


def multi_index_assertions(panel: Panel) -> None:
    """Raise ``AssertionError`` if the panel violates structural invariants.

    Idempotent — safe to call at the top of any analysis cell.

    Checks:
    - Index is MultiIndex with names ('unit_id', 'period')
    - unit_id is string-typed
    - period is pd.Timestamp-typed
    - Index is sorted
    - Panel is balanced (every unit has every period)
    - Outcome column exists
    """
    df = panel.df
    idx = df.index

    assert isinstance(idx, pd.MultiIndex), "Panel index must be MultiIndex."
    assert list(idx.names) == ["unit_id", "period"], (
        f"Panel index names must be ['unit_id', 'period'], got {list(idx.names)}."
    )

    units = idx.get_level_values("unit_id")
    periods = idx.get_level_values("period")
    assert units.dtype == object or pd.api.types.is_string_dtype(units), (
        f"unit_id index must be string-typed, got {units.dtype}."
    )
    assert isinstance(periods, pd.DatetimeIndex), "period index must be DatetimeIndex."

    assert idx.is_monotonic_increasing, "Panel index must be sorted."

    n_units = len(units.unique())
    n_periods = len(periods.unique())
    assert len(df) == n_units * n_periods, (
        f"Panel is unbalanced: {len(df)} rows vs expected {n_units * n_periods} "
        f"({n_units} units × {n_periods} periods)."
    )

    assert panel.outcome_col in df.columns, (
        f"Outcome column {panel.outcome_col!r} missing from panel."
    )
