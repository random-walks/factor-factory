"""High-dimensional fixed-effects panel regression engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

import pandas as pd

from ...tidy.panel import Panel


@dataclass(frozen=True)
class PanelRegResult:
    """HDFE panel-regression fit result."""

    method: str
    coefficients: dict[str, float]
    std_errors: dict[str, float]
    p_values: dict[str, float]
    confidence_intervals: dict[str, tuple[float, float]]
    r_squared: float | None
    n_observations: int
    n_fixed_effects: int
    fixed_effects: tuple[str, ...]
    cluster: str | None
    diagnostics: dict[str, Any] | None = None
    meta: dict[str, Any] | None = field(default=None, repr=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "method": self.method,
            "coefficients": self.coefficients,
            "std_errors": self.std_errors,
            "p_values": self.p_values,
            "confidence_intervals": {k: list(v) for k, v in self.confidence_intervals.items()},
            "r_squared": self.r_squared,
            "n_observations": self.n_observations,
            "n_fixed_effects": self.n_fixed_effects,
            "fixed_effects": list(self.fixed_effects),
            "cluster": self.cluster,
            "diagnostics": self.diagnostics,
        }

    def summary_table(self) -> pd.DataFrame:
        rows = [
            {
                "method": self.method,
                "variable": k,
                "coef": v,
                "se": self.std_errors.get(k),
                "p_value": self.p_values.get(k),
            }
            for k, v in self.coefficients.items()
        ]
        return pd.DataFrame(rows).set_index(["method", "variable"])


class PanelRegEngine(Protocol):
    name: str

    def fit(
        self,
        panel: Panel,
        *,
        outcome: str,
        regressors: tuple[str, ...],
        fixed_effects: tuple[str, ...] = (),
        cluster: str | None = None,
        **engine_specific_kwargs: Any,
    ) -> PanelRegResult: ...
