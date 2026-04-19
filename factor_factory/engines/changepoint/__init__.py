"""Changepoint-detection engines."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from ...tidy.panel import Panel
from .._registry import EngineRegistry
from ._base import ChangepointEngine, ChangepointResult

_engines: dict[str, ChangepointEngine] = {}

try:
    from .ruptures_adapter import RupturesEngine

    _engines["ruptures"] = RupturesEngine()
except ImportError:  # pragma: no cover
    pass

registry: EngineRegistry[ChangepointEngine] = EngineRegistry(_engines)


class ChangepointResults:
    def __init__(self, results: list[ChangepointResult]) -> None:
        self.results = results

    def __iter__(self) -> Iterable[ChangepointResult]:
        return iter(self.results)

    def __getitem__(self, key: int | str) -> ChangepointResult:
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
    methods: tuple[str, ...] = ("ruptures",),
    outcome: str | None = None,
    **engine_specific_kwargs: Any,
) -> ChangepointResults:
    outcome = outcome or panel.outcome_col
    if not methods:
        raise ValueError("methods must be non-empty.")
    return ChangepointResults(
        [registry[m].fit(panel, outcome=outcome, **engine_specific_kwargs) for m in methods]
    )


__all__ = [
    "ChangepointEngine",
    "ChangepointResult",
    "ChangepointResults",
    "estimate",
    "registry",
]
