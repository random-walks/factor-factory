"""STL decomposition + forecasting engines."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from ...tidy.panel import Panel
from .._registry import EngineRegistry
from ._base import StlEngine, StlResult

_engines: dict[str, StlEngine] = {}

try:
    from .sktime_stl import SktimeStlEngine

    _engines["sktime_stl"] = SktimeStlEngine()
except ImportError:  # pragma: no cover
    pass

registry: EngineRegistry[StlEngine] = EngineRegistry(_engines)


class StlResults:
    def __init__(self, results: list[StlResult]) -> None:
        self.results = results

    def __iter__(self) -> Iterable[StlResult]:
        return iter(self.results)

    def __getitem__(self, key: int | str) -> StlResult:
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
    methods: tuple[str, ...] = ("sktime_stl",),
    outcome: str | None = None,
    seasonal_period: int = 12,
    forecast_horizon: int = 0,
    **engine_specific_kwargs: Any,
) -> StlResults:
    outcome = outcome or panel.outcome_col
    if not methods:
        raise ValueError("methods must be non-empty.")
    return StlResults(
        [
            registry[m].fit(
                panel,
                outcome=outcome,
                seasonal_period=seasonal_period,
                forecast_horizon=forecast_horizon,
                **engine_specific_kwargs,
            )
            for m in methods
        ]
    )


__all__ = ["StlEngine", "StlResult", "StlResults", "estimate", "registry"]
