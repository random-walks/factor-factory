"""STL decomposition + forecasting engine Protocol + Result."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

import pandas as pd

from ...tidy.panel import Panel


@dataclass(frozen=True)
class StlResult:
    """STL decomposition + optional forecast."""

    method: str  # "sktime_stl" | "prophet"
    trend: pd.Series
    seasonal: pd.Series
    residual: pd.Series
    forecast: pd.Series | None = None
    forecast_interval: pd.DataFrame | None = None
    seasonal_period: int | None = None
    n_observations: int = 0
    diagnostics: dict[str, Any] | None = None
    meta: dict[str, Any] | None = field(default=None, repr=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "method": self.method,
            "seasonal_period": self.seasonal_period,
            "n_observations": self.n_observations,
            "trend_summary": {
                "mean": float(self.trend.mean()),
                "std": float(self.trend.std()),
            },
            "seasonal_summary": {
                "amplitude": float(self.seasonal.max() - self.seasonal.min()),
            },
            "diagnostics": self.diagnostics,
        }

    def summary_table(self) -> pd.DataFrame:
        row = {
            "method": self.method,
            "seasonal_period": self.seasonal_period,
            "trend_mean": float(self.trend.mean()),
            "seasonal_amplitude": float(self.seasonal.max() - self.seasonal.min()),
            "residual_std": float(self.residual.std()),
            "n_obs": self.n_observations,
        }
        return pd.DataFrame([row]).set_index("method")


class StlEngine(Protocol):
    name: str

    def fit(
        self,
        panel: Panel,
        *,
        outcome: str,
        seasonal_period: int,
        forecast_horizon: int = 0,
        **engine_specific_kwargs: Any,
    ) -> StlResult: ...
