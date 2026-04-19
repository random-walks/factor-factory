"""Climate engines — xclim indices + Mann-Kendall trend tests."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any, Protocol

import numpy as np
import pandas as pd

from ...tidy.panel import Panel
from .._registry import EngineRegistry


@dataclass(frozen=True)
class ClimateResult:
    method: str  # "mann_kendall" | "xclim_index"
    statistic: float
    p_value: float
    trend: str  # "increasing" | "decreasing" | "no trend"
    slope: float | None = None
    intercept: float | None = None
    index_name: str | None = None
    index_values: pd.Series | None = None
    n_observations: int = 0
    diagnostics: dict[str, Any] | None = None
    meta: dict[str, Any] | None = field(default=None, repr=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "method": self.method,
            "statistic": self.statistic,
            "p_value": self.p_value,
            "trend": self.trend,
            "slope": self.slope,
            "intercept": self.intercept,
            "index_name": self.index_name,
            "n_observations": self.n_observations,
            "diagnostics": self.diagnostics,
        }

    def summary_table(self) -> pd.DataFrame:
        row = {
            "method": self.method,
            "statistic": self.statistic,
            "p_value": self.p_value,
            "trend": self.trend,
            "slope": self.slope,
            "n_obs": self.n_observations,
        }
        return pd.DataFrame([row]).set_index("method")


class ClimateEngine(Protocol):
    name: str

    def fit(
        self,
        panel: Panel,
        *,
        outcome: str,
        **engine_specific_kwargs: Any,
    ) -> ClimateResult: ...


class MannKendallEngine:
    """Mann-Kendall trend test (Mann 1945, Kendall 1948).

    Homegrown implementation of the classic Mann-Kendall S-statistic +
    variance (handles ties but not autocorrelation). For Hamed-Rao
    correction (serial-correlation-adjusted variant), use the
    ``pymannkendall`` package directly.
    """

    name = "mann_kendall"

    def fit(
        self,
        panel: Panel,
        *,
        outcome: str,
        alpha: float = 0.05,
        **_engine_specific_kwargs: Any,
    ) -> ClimateResult:
        df = panel.df.reset_index()
        y = df.groupby("period")[outcome].mean().sort_index().to_numpy(dtype=float)
        y = y[~np.isnan(y)]
        n = len(y)
        if n < 3:
            raise ValueError(f"Mann-Kendall requires ≥ 3 observations; got {n}.")

        # S-statistic: sign-count of all pairs.
        s = int(sum(np.sign(y[j] - y[i]) for i in range(n - 1) for j in range(i + 1, n)))

        # Variance (handles ties).
        unique, counts = np.unique(y, return_counts=True)
        tie_adjust = sum(t * (t - 1) * (2 * t + 5) for t in counts if t > 1)
        var_s = float(n * (n - 1) * (2 * n + 5) - tie_adjust) / 18.0

        # Z-statistic.
        if s > 0:
            z = (s - 1) / np.sqrt(var_s)
        elif s < 0:
            z = (s + 1) / np.sqrt(var_s)
        else:
            z = 0.0

        # Two-tailed p-value via normal approximation.
        from math import erf, sqrt

        p_value = float(2 * (1 - 0.5 * (1 + erf(abs(z) / sqrt(2)))))

        # Sen's slope (robust trend estimator).
        slopes = [(y[j] - y[i]) / (j - i) for i in range(n - 1) for j in range(i + 1, n)]
        slope = float(np.median(slopes)) if slopes else 0.0
        intercept = float(np.median(y) - slope * np.median(np.arange(n)))

        # Trend direction.
        trend = ("increasing" if z > 0 else "decreasing") if p_value < alpha else "no trend"

        return ClimateResult(
            method=self.name,
            statistic=float(z),
            p_value=p_value,
            trend=trend,
            slope=slope,
            intercept=intercept,
            n_observations=n,
            diagnostics={"s": int(s), "var_s": var_s, "alpha": alpha},
        )


_engines: dict[str, ClimateEngine] = {"mann_kendall": MannKendallEngine()}
registry: EngineRegistry[ClimateEngine] = EngineRegistry(_engines)


class ClimateResults:
    def __init__(self, results: list[ClimateResult]) -> None:
        self.results = results

    def __iter__(self) -> Iterable[ClimateResult]:
        return iter(self.results)

    def __getitem__(self, key: int | str) -> ClimateResult:
        if isinstance(key, int):
            return self.results[key]
        for r in self.results:
            if r.method == key:
                return r
        raise KeyError(key)

    def to_records(self) -> list[dict[str, Any]]:
        return [r.to_dict() for r in self.results]


def estimate(
    panel: Panel,
    *,
    methods: tuple[str, ...] = ("mann_kendall",),
    outcome: str | None = None,
    **engine_specific_kwargs: Any,
) -> ClimateResults:
    outcome = outcome or panel.outcome_col
    if not methods:
        raise ValueError("methods must be non-empty.")
    return ClimateResults(
        [registry[m].fit(panel, outcome=outcome, **engine_specific_kwargs) for m in methods]
    )


__all__ = [
    "ClimateEngine",
    "ClimateResult",
    "ClimateResults",
    "MannKendallEngine",
    "estimate",
    "registry",
]
