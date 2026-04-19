"""Synthetic-Control Method engine Protocol + Result dataclass."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

import pandas as pd

from ...tidy.panel import Panel


@dataclass(frozen=True)
class ScmResult:
    """Synthetic-control fit result."""

    method: str  # "pysyncon" | "augmented"
    att: float
    std_error: float | None
    pre_period_rmspe: float
    post_period_rmspe: float
    donor_weights: dict[Any, float]
    predictor_weights: dict[str, float] | None = None
    placebo_pvalue: float | None = None
    n_donor: int = 0
    n_pre: int = 0
    n_post: int = 0
    diagnostics: dict[str, Any] | None = None
    meta: dict[str, Any] | None = field(default=None, repr=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "method": self.method,
            "att": self.att,
            "std_error": self.std_error,
            "pre_period_rmspe": self.pre_period_rmspe,
            "post_period_rmspe": self.post_period_rmspe,
            "donor_weights": {str(k): v for k, v in self.donor_weights.items()},
            "predictor_weights": self.predictor_weights,
            "placebo_pvalue": self.placebo_pvalue,
            "n_donor": self.n_donor,
            "n_pre": self.n_pre,
            "n_post": self.n_post,
            "diagnostics": self.diagnostics,
        }

    def summary_table(self) -> pd.DataFrame:
        row = {
            "method": self.method,
            "att": self.att,
            "se": self.std_error,
            "pre_rmspe": self.pre_period_rmspe,
            "post_rmspe": self.post_period_rmspe,
            "placebo_p": self.placebo_pvalue,
            "n_donor": self.n_donor,
        }
        return pd.DataFrame([row]).set_index("method")


class ScmEngine(Protocol):
    name: str

    def fit(
        self,
        panel: Panel,
        *,
        outcome: str,
        treatment: str = "treatment",
        **engine_specific_kwargs: Any,
    ) -> ScmResult: ...
