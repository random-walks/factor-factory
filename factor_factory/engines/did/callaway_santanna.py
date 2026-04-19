"""Callaway-Sant'Anna staggered DiD adapter via the ``differences`` package.

The TWFE estimator collapses negatively-weighted forbidden comparisons
under staggered rollout (Goodman-Bacon 2021). Callaway-Sant'Anna (2021)
estimates ATT(g, t) by cohort × event-time, then aggregates without
contamination. This adapter is the right tool whenever a panel has
multiple treatment events at different dates.

Citation: Callaway, B., & Sant'Anna, P. H. C. (2021). Difference-in-
differences with multiple time periods. Journal of Econometrics, 225(2),
200–230.
"""

from __future__ import annotations

from math import erf, sqrt
from typing import Any

import numpy as np
import pandas as pd

from ...tidy.panel import Panel
from ._base import DidResult


class CallawaySantannaEngine:
    """Staggered-rollout DiD via Callaway & Sant'Anna 2021.

    Wraps :class:`differences.ATTgt`. Constructs a per-unit cohort
    column from the panel's ``TreatmentEvent`` set (the earliest
    treatment date for each unit). Fits with ``est_method='dr'``
    (doubly-robust) by default; pass ``est_method=...`` kwarg to
    override.

    Period handling: ``differences`` requires either pure-integer or
    pure-datetime time / cohort dtypes. Timestamp panels are
    automatically rank-encoded to integers before passing through
    (each unique period becomes ``0, 1, 2, ...``); float / ordinal
    panels raise.
    """

    name = "cs"

    def fit(
        self,
        panel: Panel,
        *,
        outcome: str,
        treatment: str = "treatment",  # unused; kept for Protocol parity
        cluster: str | None = None,
        est_method: str = "dr",
        control_group: str = "not_yet_treated",
        boot_iterations: int = 0,
        **_engine_specific_kwargs: Any,
    ) -> DidResult:
        try:
            from differences import ATTgt
        except ImportError as exc:  # pragma: no cover
            raise ImportError(
                "CallawaySantannaEngine requires the `differences` package. "
                "Install via `pip install factor-factory[did]`."
            ) from exc

        if not panel.treatment_events:
            raise ValueError(
                "CallawaySantannaEngine requires panel.treatment_events to "
                "construct per-unit cohorts. Build the panel with "
                "treatment_events=(...) or use TwfeEngine for events-free panels."
            )
        if panel.period_kind not in ("timestamp", "integer"):
            raise ValueError(
                "CallawaySantannaEngine requires period_kind in {'timestamp', "
                f"'integer'}}; got {panel.period_kind!r}. Continuous-period "
                "(dose-response) panels need a different estimator."
            )

        df, period_to_int = _rank_encode_periods(panel)
        cohort = _derive_cohort_column(panel, period_to_int)
        # Pass ATTgt only the outcome + cohort. Extra columns (per-event
        # treatment masks, etc.) confuse `differences`' internal column
        # filtering on certain panel shapes.
        df = pd.DataFrame({outcome: df[outcome], "cohort": cohort.values}, index=df.index)

        attgt = ATTgt(data=df, cohort_column="cohort")
        formula = f"{outcome} ~ 1"
        # NOTE: ``differences`` requires the cluster column to live on
        # the DataFrame passed to ATTgt — and we strip extras above for
        # robustness. To cluster, the user must include the cluster column
        # in the panel and we'd need to pass it through. Phase-2 follow-up.
        attgt.fit(
            formula=formula,
            est_method=est_method,
            control_group=control_group,
            boot_iterations=boot_iterations,
            progress_bar=False,
        )
        agg = attgt.aggregate(type_of_aggregation="simple")
        # `differences` returns a single-row DataFrame for type='simple'
        # with multi-index columns ('SimpleAggregation', metric)
        row = agg.iloc[0]

        att = float(_get_cell(row, "ATT"))
        se = float(_get_cell(row, "std_error"))
        lo = float(_get_cell(row, "lower", default=att - 1.96 * se))
        hi = float(_get_cell(row, "upper", default=att + 1.96 * se))

        z = att / se if se > 0 else float("nan")
        p_value = float(2.0 * (1.0 - _phi(abs(z)))) if not np.isnan(z) else 1.0

        return DidResult(
            method=self.name,
            att=att,
            se=se,
            ci_95=(lo, hi),
            p_value=p_value,
            n=int(len(df)),
            diagnostics={
                "est_method": est_method,
                "control_group": control_group,
                "n_cohorts": int(cohort.dropna().nunique()),
            },
            meta={"raw_aggregate": agg.to_dict(orient="records")},
        )


def _rank_encode_periods(panel: Panel) -> tuple[pd.DataFrame, dict[Any, int]]:
    """Rank-encode the panel's period axis to int (0, 1, 2, ...).

    Returns the rewritten DataFrame and a mapping from original period
    value to integer rank. Used to satisfy ``differences``' requirement
    that time + cohort columns share dtype (int or datetime).
    """
    df = panel.df.copy()
    periods = df.index.get_level_values("period").unique().sort_values()
    mapping = {p: i for i, p in enumerate(periods)}
    int_periods = df.index.get_level_values("period").map(mapping)
    df.index = pd.MultiIndex.from_arrays(
        [df.index.get_level_values("unit_id"), int_periods],
        names=["unit_id", "period"],
    )
    return df, mapping


def _derive_cohort_column(panel: Panel, period_to_int: dict[Any, int]) -> pd.Series:
    """For each unit, the integer period of earliest treatment across events.

    Units never treated by any event get NaN. The mapping argument
    converts each event's treatment_date / period_value to the same
    rank-encoded integer space as the data.
    """
    cohort_map: dict[Any, float] = {}
    for ev in panel.treatment_events:
        anchor: Any
        if ev.treatment_date is not None:
            anchor = pd.Timestamp(ev.treatment_date)
        else:
            anchor = ev.period_value
        # Find the earliest panel-period >= anchor
        anchor_int = _resolve_anchor_to_int(anchor, period_to_int)
        if anchor_int is None:
            continue  # event never lands inside the panel window
        for unit in ev.treated_units:
            existing = cohort_map.get(unit)
            if existing is None or anchor_int < existing:
                cohort_map[unit] = float(anchor_int)
    unit_ids = panel.df.index.get_level_values("unit_id")
    return pd.Series(
        [cohort_map.get(u, np.nan) for u in unit_ids],
        index=panel.df.index,
        name="cohort",
        dtype="float64",
    )


def _resolve_anchor_to_int(anchor: Any, mapping: dict[Any, int]) -> int | None:
    """Find the smallest period in the mapping that is >= anchor."""
    sorted_periods = sorted(mapping.keys())
    for p in sorted_periods:
        if p >= anchor:
            return mapping[p]
    return None


def _get_cell(row: pd.Series, name: str, default: float | None = None) -> float:
    """Read a cell from a (possibly multi-index) summary row by leaf name."""
    for key in row.index:
        if isinstance(key, tuple):
            if name in key:
                return float(row[key])
        elif key == name:
            return float(row[key])
    if default is not None:
        return float(default)
    raise KeyError(f"{name!r} not found in CS summary row (keys: {list(row.index)})")


def _phi(z: float) -> float:
    """Standard-normal CDF via erf."""
    return 0.5 * (1.0 + erf(z / sqrt(2.0)))
