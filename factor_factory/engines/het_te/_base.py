"""Heterogeneous-treatment-effects engine Protocol + Result."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

import numpy as np
import pandas as pd

from ...tidy.panel import Panel


@dataclass(frozen=True)
class HetTeResult:
    """Causal-forest / meta-learner heterogeneous-effects result."""

    method: str  # "causal_forest" | "x_learner" | "r_learner" | "bcf"
    ate: float
    ate_std_error: float
    cate_predictions: np.ndarray | None = None  # per-unit CATE
    cate_std_errors: np.ndarray | None = None
    treatment_effect_heterogeneity_pvalue: float | None = None
    feature_importances: dict[str, float] | None = None
    nuisance_learner_scores: dict[str, float] | None = None
    n_units: int = 0
    diagnostics: dict[str, Any] | None = None
    meta: dict[str, Any] | None = field(default=None, repr=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "method": self.method,
            "ate": self.ate,
            "ate_std_error": self.ate_std_error,
            "cate_summary": {
                "mean": float(np.mean(self.cate_predictions))
                if self.cate_predictions is not None
                else None,
                "std": float(np.std(self.cate_predictions))
                if self.cate_predictions is not None
                else None,
            },
            "treatment_effect_heterogeneity_pvalue": self.treatment_effect_heterogeneity_pvalue,
            "feature_importances": self.feature_importances,
            "n_units": self.n_units,
            "diagnostics": self.diagnostics,
        }

    def summary_table(self) -> pd.DataFrame:
        row = {
            "method": self.method,
            "ate": self.ate,
            "ate_se": self.ate_std_error,
            "het_p": self.treatment_effect_heterogeneity_pvalue,
            "cate_mean": (
                float(np.mean(self.cate_predictions)) if self.cate_predictions is not None else None
            ),
            "cate_std": (
                float(np.std(self.cate_predictions)) if self.cate_predictions is not None else None
            ),
            "n_units": self.n_units,
        }
        return pd.DataFrame([row]).set_index("method")


class HetTeEngine(Protocol):
    name: str

    def fit(
        self,
        panel: Panel,
        *,
        outcome: str,
        treatment: str = "treatment",
        covariates: tuple[str, ...] = (),
        **engine_specific_kwargs: Any,
    ) -> HetTeResult: ...
