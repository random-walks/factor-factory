"""Changepoint-detection engine Protocol + Result."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

import pandas as pd

from ...tidy.panel import Panel


@dataclass(frozen=True)
class ChangepointResult:
    """Changepoint-detection fit result."""

    method: str
    changepoints: list[int]  # period indices at detected breaks
    regime_means: list[float]  # mean outcome within each regime
    n_regimes: int
    model: str  # "l1" | "l2" | "rbf" | "bayesian_online"
    penalty: float | None = None
    confidence: list[float] | None = None  # per-changepoint confidence score
    diagnostics: dict[str, Any] | None = None
    meta: dict[str, Any] | None = field(default=None, repr=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "method": self.method,
            "changepoints": self.changepoints,
            "regime_means": self.regime_means,
            "n_regimes": self.n_regimes,
            "model": self.model,
            "penalty": self.penalty,
            "confidence": self.confidence,
            "diagnostics": self.diagnostics,
        }

    def summary_table(self) -> pd.DataFrame:
        row = {
            "method": self.method,
            "n_changepoints": len(self.changepoints),
            "n_regimes": self.n_regimes,
            "model": self.model,
            "penalty": self.penalty,
        }
        return pd.DataFrame([row]).set_index("method")


class ChangepointEngine(Protocol):
    name: str

    def fit(
        self,
        panel: Panel,
        *,
        outcome: str,
        **engine_specific_kwargs: Any,
    ) -> ChangepointResult: ...
