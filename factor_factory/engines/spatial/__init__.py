"""Spatial-econometrics engines."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from ...tidy.panel import Panel
from .._registry import EngineRegistry
from ._base import SpatialEngine, SpatialResult

_engines: dict[str, SpatialEngine] = {}

try:
    from .morans_i import MoransIEngine

    _engines["morans_i"] = MoransIEngine()
except ImportError:  # pragma: no cover
    pass

registry: EngineRegistry[SpatialEngine] = EngineRegistry(_engines)


class SpatialResults:
    def __init__(self, results: list[SpatialResult]) -> None:
        self.results = results

    def __iter__(self) -> Iterable[SpatialResult]:
        return iter(self.results)

    def __getitem__(self, key: int | str) -> SpatialResult:
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
    methods: tuple[str, ...] = ("morans_i",),
    outcome: str | None = None,
    coordinates: tuple[str, str] = ("latitude", "longitude"),
    **engine_specific_kwargs: Any,
) -> SpatialResults:
    outcome = outcome or panel.outcome_col
    if not methods:
        raise ValueError("methods must be non-empty.")
    return SpatialResults(
        [
            registry[m].fit(panel, outcome=outcome, coordinates=coordinates, **engine_specific_kwargs)
            for m in methods
        ]
    )


__all__ = ["SpatialEngine", "SpatialResult", "SpatialResults", "estimate", "registry"]
