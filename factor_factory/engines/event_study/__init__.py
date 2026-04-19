"""Event-study engines + ``estimate()`` dispatcher.

Domain: corporate finance (M&A, earnings, IPO), policy events (rate
hikes, regulatory announcements), pharmaceutical news (FDA approval),
any "single-date jolt around a known event".
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from ...tidy.panel import Panel
from .._registry import EngineRegistry
from ._base import EventStudyEngine, EventStudyResult
from .fama_french import FamaFrenchEngine
from .market_adjusted import MarketAdjustedEngine

_engines: dict[str, EventStudyEngine] = {
    "market_adjusted": MarketAdjustedEngine(),
    "fama_french": FamaFrenchEngine(),
}

registry: EngineRegistry[EventStudyEngine] = EngineRegistry(_engines)


class EventStudyResults:
    def __init__(self, results: list[EventStudyResult]) -> None:
        self.results = results

    def __iter__(self) -> Iterable[EventStudyResult]:
        return iter(self.results)

    def __getitem__(self, key: int | str) -> EventStudyResult:
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
    methods: tuple[str, ...] = ("market_adjusted",),
    outcome: str | None = None,
    event_window: tuple[int, int] = (-1, 1),
    estimation_window: tuple[int, int] = (-120, -20),
    **engine_specific_kwargs: Any,
) -> EventStudyResults:
    """Estimate abnormal returns under one or more methods."""
    outcome = outcome or panel.outcome_col
    if not methods:
        raise ValueError("methods must be non-empty.")
    results = []
    for m in methods:
        engine = registry[m]
        results.append(
            engine.fit(
                panel,
                outcome=outcome,
                event_window=event_window,
                estimation_window=estimation_window,
                **engine_specific_kwargs,
            )
        )
    return EventStudyResults(results)


__all__ = [
    "EventStudyEngine",
    "EventStudyResult",
    "EventStudyResults",
    "estimate",
    "registry",
]
