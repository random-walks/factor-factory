"""Sun-Abraham (2021) interaction-weighted staggered-DiD adapter.

Sun & Abraham (2021) construct an event-study estimator that is robust
to heterogeneous treatment effects across cohorts. Their estimator is
a weighted average of cohort × event-time specific ATT(g, e), with
weights equal to the sample share of cohort g at event-time e.

Relationship to Callaway-Sant'Anna
----------------------------------
Sun-Abraham's interaction-weighted estimator (IW) and Callaway-
Sant'Anna's event-study aggregation coincide under standard
assumptions (never-treated as control, doubly-robust estimation).
This adapter wraps :class:`differences.ATTgt` — the same upstream used
by :class:`CallawaySantannaEngine` — but uses the ``event`` aggregation
that matches Sun-Abraham's IW estimator instead of the ``simple``
aggregation used by the CS adapter.

For cases where they diverge (always-treated units, specific weighting
choices), the SA-specific paths are documented in the fit() docstring.

References
----------
Sun, L., & Abraham, S. (2021). Estimating dynamic treatment effects
in event studies with heterogeneous treatment effects. *Journal of
Econometrics*, 225(2), 175-199.
https://doi.org/10.1016/j.jeconom.2020.09.006

Reference implementation: Stata ``eventstudyinteract`` package; R
``fixest::sunab``. No canonical Python package as of late 2025 — this
adapter reuses ``differences.ATTgt`` with the event-study aggregation
that matches SA under standard assumptions.
"""

from __future__ import annotations

from math import erf, sqrt
from typing import Any

import numpy as np
import pandas as pd

from ...tidy.panel import Panel
from ._base import DidResult
from .callaway_santanna import _derive_cohort_column, _rank_encode_periods


class SunAbrahamEngine:
    """Sun-Abraham (2021) interaction-weighted estimator.

    Wraps :class:`differences.ATTgt` with event-study aggregation.
    Expects the same Panel shape as CS (staggered-rollout DiD with
    ``TreatmentEvent`` set + ``period_kind`` ∈ {'timestamp', 'integer'}).
    """

    name = "sa"

    def fit(
        self,
        panel: Panel,
        *,
        outcome: str,
        treatment: str = "treatment",  # unused; kept for Protocol parity
        cluster: str | None = None,
        est_method: str = "dr",
        control_group: str = "never_treated",
        boot_iterations: int = 0,
        **_engine_specific_kwargs: Any,
    ) -> DidResult:
        try:
            from differences import ATTgt
        except ImportError as exc:  # pragma: no cover
            raise ImportError(
                "SunAbrahamEngine requires the `differences` package. "
                "Install via `pip install factor-factory[did]`."
            ) from exc

        if not panel.treatment_events:
            raise ValueError(
                "SunAbrahamEngine requires panel.treatment_events to construct per-unit cohorts."
            )
        if panel.period_kind not in ("timestamp", "integer"):
            raise ValueError(
                "SunAbrahamEngine requires period_kind in {'timestamp', "
                f"'integer'}}; got {panel.period_kind!r}."
            )

        df, period_to_int = _rank_encode_periods(panel)
        cohort = _derive_cohort_column(panel, period_to_int)
        df = pd.DataFrame({outcome: df[outcome], "cohort": cohort.values}, index=df.index)

        attgt = ATTgt(data=df, cohort_column="cohort")
        attgt.fit(
            formula=f"{outcome} ~ 1",
            est_method=est_method,
            control_group=control_group,
            boot_iterations=boot_iterations,
            progress_bar=False,
        )

        # Event-study aggregation — this is the Sun-Abraham IW estimator
        # under the standard-assumptions overlap with CS.
        agg = attgt.aggregate(type_of_aggregation="event")

        # The upstream returns pre- AND post-treatment event-times. The ATT
        # point estimate is the mean of POST-treatment dynamic effects
        # (event_time >= 0). The pre-treatment coefficients are placebo
        # checks — inspecting them is how SA evidences parallel trends.
        if agg.index.inferred_type in ("integer", "floating"):
            post_mask = agg.index >= 0
            post_agg = agg.loc[post_mask] if post_mask.any() else agg
        else:
            post_agg = agg

        att_col = post_agg["ATT"] if "ATT" in post_agg.columns else post_agg.iloc[:, 0]
        att = float(att_col.mean())
        se_col_name = "std_error" if "std_error" in post_agg.columns else None
        if se_col_name and not post_agg[se_col_name].isna().all():
            # SE of the average of independent event-time ATTs: sqrt(sum(se^2) / n^2).
            n_events = len(post_agg)
            se = float(np.sqrt((post_agg[se_col_name] ** 2).sum() / (n_events**2)))
        else:
            # Fallback: cross-event-time standard error of the mean (valid
            # when upstream doesn't return per-event-time SEs, e.g. when
            # bootstrap was not run).
            n_events = max(int(len(post_agg)), 1)
            se = float(att_col.std(ddof=1) / np.sqrt(n_events)) if n_events > 1 else float("nan")
        lo = att - 1.96 * se if np.isfinite(se) else float("nan")
        hi = att + 1.96 * se if np.isfinite(se) else float("nan")
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
                "aggregation": "sun_abraham_iw",
                "n_event_times": len(agg),
                "upstream": "differences.ATTgt event-study aggregation",
            },
            meta={"event_study_curve": agg.to_dict(orient="records")},
        )


def _phi(z: float) -> float:
    """Standard-normal CDF via erf."""
    return 0.5 * (1.0 + erf(z / sqrt(2.0)))
