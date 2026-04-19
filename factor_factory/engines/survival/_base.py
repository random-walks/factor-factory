"""Survival-analysis engine Protocol + frozen result dataclass."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

import pandas as pd

from ...tidy.panel import Panel


@dataclass(frozen=True)
class SurvivalResult:
    """Result of a single survival-analysis fit.

    Domain: oncology trials, churn prediction, hardware failure,
    pharmacokinetics, equipment reliability — anywhere you have a
    duration column + event indicator (1 = event observed, 0 =
    censored).

    Required-for-all-engines fields are first; optional Cox-PH /
    AFT-style coefficients live in ``coefficients`` and ``hazard_ratios``.
    """

    method: str
    median_survival: float | None
    n_subjects: int
    n_events: int

    # Optional: per-covariate coefficients (Cox PH / AFT)
    coefficients: dict[str, float] | None = None
    hazard_ratios: dict[str, float] | None = None
    p_values: dict[str, float] | None = None
    confidence_intervals: dict[str, tuple[float, float]] | None = None

    # Optional: KM survival curve as a DataFrame (timeline, survival_prob, ci_lower, ci_upper)
    survival_curve: pd.DataFrame | None = None

    # Cox PH proportional-hazards Schoenfeld test: per-covariate p-values
    proportional_hazards_test: dict[str, float] | None = None

    diagnostics: dict[str, Any] | None = None
    meta: dict[str, Any] | None = field(default=None, repr=False)

    def to_dict(self) -> dict[str, Any]:
        """JSON-serializable dict (excludes ``survival_curve`` + ``meta``)."""
        return {
            "method": self.method,
            "median_survival": self.median_survival,
            "n_subjects": self.n_subjects,
            "n_events": self.n_events,
            "coefficients": self.coefficients,
            "hazard_ratios": self.hazard_ratios,
            "p_values": self.p_values,
            "confidence_intervals": (
                {k: list(v) for k, v in self.confidence_intervals.items()}
                if self.confidence_intervals
                else None
            ),
            "proportional_hazards_test": self.proportional_hazards_test,
            "diagnostics": self.diagnostics,
        }

    def summary_table(self) -> pd.DataFrame:
        """One-row summary table for tearsheet rendering.

        Mirrors the ``DidResults.summary_table()`` shape for engine-family
        parity (added in v1.1.0, Batch 4).
        """
        row: dict[str, Any] = {
            "method": self.method,
            "median_survival": self.median_survival,
            "n_subjects": self.n_subjects,
            "n_events": self.n_events,
        }
        if self.hazard_ratios:
            for k, v in self.hazard_ratios.items():
                row[f"hr[{k}]"] = v
                if self.p_values and k in self.p_values:
                    row[f"p[{k}]"] = self.p_values[k]
        return pd.DataFrame([row]).set_index("method")


class SurvivalEngine(Protocol):
    """Protocol every survival-analysis engine must satisfy.

    Survival panels have one row per subject (or one row per
    subject-interval for time-varying covariates). Required columns:

    - ``duration`` (numeric): observed time from baseline to event /
      censoring.
    - ``event`` (int 0/1): 1 if the event was observed at ``duration``,
      0 if right-censored at ``duration``.

    Covariates are any additional numeric columns. The engine consumes
    them depending on the underlying method (KM ignores them; Cox PH
    fits coefficients).
    """

    name: str

    def fit(
        self,
        panel: Panel,
        *,
        duration_col: str = "duration",
        event_col: str = "event",
        covariates: tuple[str, ...] = (),
        cluster: str | None = None,
        **engine_specific_kwargs: Any,
    ) -> SurvivalResult:
        """Fit the survival model on ``panel``."""
        ...
