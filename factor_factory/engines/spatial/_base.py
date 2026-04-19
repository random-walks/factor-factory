"""Spatial econometrics engine Protocol + Result."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

import pandas as pd

from ...tidy.panel import Panel


@dataclass(frozen=True)
class SpatialResult:
    """Spatial-analysis fit result."""

    method: str  # "morans_i" | "spreg_ols" | "geary_c"
    statistic: float
    p_value: float
    z_score: float | None = None
    local_statistics: pd.Series | None = None  # e.g., Local Moran's I per unit
    n_units: int = 0
    weights_type: str | None = None
    diagnostics: dict[str, Any] | None = None
    meta: dict[str, Any] | None = field(default=None, repr=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "method": self.method,
            "statistic": self.statistic,
            "p_value": self.p_value,
            "z_score": self.z_score,
            "n_units": self.n_units,
            "weights_type": self.weights_type,
            "diagnostics": self.diagnostics,
        }

    def summary_table(self) -> pd.DataFrame:
        row = {
            "method": self.method,
            "statistic": self.statistic,
            "p_value": self.p_value,
            "z_score": self.z_score,
            "n_units": self.n_units,
        }
        return pd.DataFrame([row]).set_index("method")


class SpatialEngine(Protocol):
    name: str

    def fit(
        self,
        panel: Panel,
        *,
        outcome: str,
        coordinates: tuple[str, str] = ("latitude", "longitude"),
        **engine_specific_kwargs: Any,
    ) -> SpatialResult: ...
