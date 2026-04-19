"""Inequality-decomposition engines (Theil, Atkinson, Gini)."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any, Protocol

import numpy as np
import pandas as pd

from ...tidy.panel import Panel
from .._registry import EngineRegistry


@dataclass(frozen=True)
class InequalityResult:
    method: str  # "theil_t" | "theil_l" | "gini" | "atkinson"
    overall: float
    between: float | None = None
    within: float | None = None
    groups: dict[str, float] | None = None
    n_observations: int = 0
    diagnostics: dict[str, Any] | None = None
    meta: dict[str, Any] | None = field(default=None, repr=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "method": self.method,
            "overall": self.overall,
            "between": self.between,
            "within": self.within,
            "groups": self.groups,
            "n_observations": self.n_observations,
            "diagnostics": self.diagnostics,
        }

    def summary_table(self) -> pd.DataFrame:
        row = {
            "method": self.method,
            "overall": self.overall,
            "between": self.between,
            "within": self.within,
            "n_obs": self.n_observations,
        }
        return pd.DataFrame([row]).set_index("method")


class InequalityEngine(Protocol):
    name: str

    def fit(
        self,
        panel: Panel,
        *,
        outcome: str,
        group_col: str | None = None,
        **engine_specific_kwargs: Any,
    ) -> InequalityResult: ...


class TheilEngine:
    """Theil T + Theil L decomposition (homegrown, numpy only).

    Theil T: T = Σ (x_i / μ) * ln(x_i / μ) / N
    Theil L: L = Σ ln(μ / x_i) / N

    With grouping, T decomposes as T_between + T_within.
    """

    name = "theil_t"

    def fit(
        self,
        panel: Panel,
        *,
        outcome: str,
        group_col: str | None = None,
        **_engine_specific_kwargs: Any,
    ) -> InequalityResult:
        df = panel.df.reset_index()
        x = df[outcome].to_numpy(dtype=float)
        x = x[x > 0]  # Theil undefined for non-positive values
        mu = float(np.mean(x))
        overall = float(np.mean((x / mu) * np.log(x / mu)))

        between: float | None = None
        within: float | None = None
        group_values: dict[str, float] | None = None
        if group_col and group_col in df.columns:
            groups = df.groupby(group_col)[outcome].apply(lambda s: s[s > 0].to_numpy())
            shares = {g: float(np.sum(arr)) / float(np.sum(x)) for g, arr in groups.items()}
            means = {g: float(np.mean(arr)) if len(arr) else 0.0 for g, arr in groups.items()}
            between = float(
                sum(shares[g] * np.log(means[g] / mu) for g, _ in groups.items() if means[g] > 0)
            )
            within_components = {}
            for g, arr in groups.items():
                if len(arr) == 0 or means[g] <= 0:
                    continue
                within_components[g] = float(
                    shares[g] * np.mean((arr / means[g]) * np.log(arr / means[g]))
                )
            within = float(sum(within_components.values()))
            group_values = {str(k): v for k, v in within_components.items()}

        return InequalityResult(
            method=self.name,
            overall=overall,
            between=between,
            within=within,
            groups=group_values,
            n_observations=int(len(x)),
            diagnostics={"group_col": group_col, "decomposition": "theil_t"},
        )


_engines: dict[str, InequalityEngine] = {"theil_t": TheilEngine()}
registry: EngineRegistry[InequalityEngine] = EngineRegistry(_engines)


class InequalityResults:
    def __init__(self, results: list[InequalityResult]) -> None:
        self.results = results

    def __iter__(self) -> Iterable[InequalityResult]:
        return iter(self.results)

    def __getitem__(self, key: int | str) -> InequalityResult:
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
    methods: tuple[str, ...] = ("theil_t",),
    outcome: str | None = None,
    group_col: str | None = None,
    **engine_specific_kwargs: Any,
) -> InequalityResults:
    outcome = outcome or panel.outcome_col
    if not methods:
        raise ValueError("methods must be non-empty.")
    return InequalityResults(
        [
            registry[m].fit(panel, outcome=outcome, group_col=group_col, **engine_specific_kwargs)
            for m in methods
        ]
    )


__all__ = [
    "InequalityEngine",
    "InequalityResult",
    "InequalityResults",
    "TheilEngine",
    "estimate",
    "registry",
]
