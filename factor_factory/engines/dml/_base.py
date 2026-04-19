"""Double/debiased machine learning engine Protocol + Result."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

import pandas as pd

from ...tidy.panel import Panel


@dataclass(frozen=True)
class DmlResult:
    """DoubleML fit result."""

    method: str  # "plr" | "irm"
    coef: float
    std_error: float
    t_stat: float
    p_value: float
    ci_95: tuple[float, float]
    n_units: int
    n_folds: int
    nuisance_rmse: dict[str, float] | None = None
    diagnostics: dict[str, Any] | None = None
    meta: dict[str, Any] | None = field(default=None, repr=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "method": self.method,
            "coef": self.coef,
            "std_error": self.std_error,
            "t_stat": self.t_stat,
            "p_value": self.p_value,
            "ci_95_lower": self.ci_95[0],
            "ci_95_upper": self.ci_95[1],
            "n_units": self.n_units,
            "n_folds": self.n_folds,
            "nuisance_rmse": self.nuisance_rmse,
            "diagnostics": self.diagnostics,
        }

    def summary_table(self) -> pd.DataFrame:
        row = {
            "method": self.method,
            "coef": self.coef,
            "se": self.std_error,
            "t_stat": self.t_stat,
            "p_value": self.p_value,
            "ci_lo": self.ci_95[0],
            "ci_hi": self.ci_95[1],
            "n": self.n_units,
        }
        return pd.DataFrame([row]).set_index("method")


class DmlEngine(Protocol):
    name: str

    def fit(
        self,
        panel: Panel,
        *,
        outcome: str,
        treatment: str = "treatment",
        covariates: tuple[str, ...] = (),
        **engine_specific_kwargs: Any,
    ) -> DmlResult: ...
