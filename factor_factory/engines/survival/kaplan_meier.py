"""Kaplan-Meier non-parametric survival estimator via ``lifelines``.

Citation: Kaplan, E. L., & Meier, P. (1958). Nonparametric estimation
from incomplete observations. Journal of the American Statistical
Association, 53(282), 457–481.
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from ...tidy.panel import Panel
from ._base import SurvivalResult


class KaplanMeierEngine:
    """Non-parametric Kaplan-Meier survival curve.

    Returns the median survival time + the full survival curve in
    ``result.survival_curve``. Ignores covariates (use CoxPH for
    covariate-adjusted analysis).
    """

    name = "kaplan_meier"

    def fit(
        self,
        panel: Panel,
        *,
        duration_col: str = "duration",
        event_col: str = "event",
        covariates: tuple[str, ...] = (),
        cluster: str | None = None,
        alpha: float = 0.05,
        **_engine_specific_kwargs: Any,
    ) -> SurvivalResult:
        try:
            from lifelines import KaplanMeierFitter
        except ImportError as exc:  # pragma: no cover
            raise ImportError(
                "KaplanMeierEngine requires the `lifelines` package. "
                "Install via `pip install factor-factory[survival]`."
            ) from exc

        df = _flatten_to_subject_table(panel, duration_col, event_col)
        durations = df[duration_col].astype(float)
        events = df[event_col].astype(int)

        kmf = KaplanMeierFitter(alpha=alpha)
        kmf.fit(durations, event_observed=events)

        # Build the survival-curve DataFrame
        sf = kmf.survival_function_
        ci = kmf.confidence_interval_
        curve = pd.DataFrame(
            {
                "timeline": sf.index.astype(float),
                "survival_prob": sf.iloc[:, 0].astype(float).to_numpy(),
                "ci_lower": ci.iloc[:, 0].astype(float).to_numpy(),
                "ci_upper": ci.iloc[:, 1].astype(float).to_numpy(),
            }
        )

        median = float(kmf.median_survival_time_)
        n_subjects = int(len(df))
        n_events = int(events.sum())

        return SurvivalResult(
            method=self.name,
            median_survival=median if pd.notna(median) else None,
            n_subjects=n_subjects,
            n_events=n_events,
            survival_curve=curve,
            diagnostics={"alpha": alpha, "censoring_rate": 1.0 - n_events / n_subjects},
            meta={"label": kmf.label},
        )


def _flatten_to_subject_table(panel: Panel, duration_col: str, event_col: str) -> pd.DataFrame:
    """Collapse a Panel to one row per subject for survival analysis.

    If the panel has multiple periods per unit, take the row at the
    largest period (the latest observation). If the panel has one row
    per unit already, return as-is.
    """
    df = panel.df
    if duration_col not in df.columns:
        raise ValueError(
            f"Panel missing duration column {duration_col!r}. Got: {list(df.columns)}."
        )
    if event_col not in df.columns:
        raise ValueError(f"Panel missing event column {event_col!r}. Got: {list(df.columns)}.")
    # If only one row per unit, drop the period level and return.
    if df.index.get_level_values("unit_id").nunique() == len(df):
        return df.reset_index(level="period", drop=True)
    # Multiple periods per unit — take the latest observation per unit.
    return (
        df.groupby(level="unit_id", group_keys=False).tail(1).reset_index(level="period", drop=True)
    )
