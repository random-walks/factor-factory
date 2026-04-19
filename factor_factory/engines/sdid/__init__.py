"""Synthetic Difference-in-Differences engines.

Closes a long-standing Python-ecosystem gap: SDID (Arkhangelsky et
al. 2021, *American Economic Review*) has no mature first-class
Python implementation. The reference R package is ``synthdid`` from
the Stanford team; this module ports the math directly.

Use for: panel-data settings where parallel-trends is suspect but
multiple units share a single treatment date (joint policy adoption,
multi-state regulatory shifts). For staggered rollout, use
``engines.did.callaway_santanna`` instead.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from ...tidy.panel import Panel
from .._registry import EngineRegistry
from ._base import SdidEngine, SdidResult
from .arkhangelsky import SyntheticDidEngine

_engines: dict[str, SdidEngine] = {"sdid": SyntheticDidEngine()}

registry: EngineRegistry[SdidEngine] = EngineRegistry(_engines)


class SdidResults:
    def __init__(self, results: list[SdidResult]) -> None:
        self.results = results

    def __iter__(self) -> Iterable[SdidResult]:
        return iter(self.results)

    def __getitem__(self, key: int | str) -> SdidResult:
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
    methods: tuple[str, ...] = ("sdid",),
    outcome: str | None = None,
    treatment: str = "treatment",
    cluster: str | None = None,
    **engine_specific_kwargs: Any,
) -> SdidResults:
    """Estimate Synthetic DiD ATT under one or more methods."""
    outcome = outcome or panel.outcome_col
    if not methods:
        raise ValueError("methods must be non-empty.")
    results: list[SdidResult] = []
    for m in methods:
        engine = registry[m]
        results.append(
            engine.fit(
                panel,
                outcome=outcome,
                treatment=treatment,
                cluster=cluster,
                **engine_specific_kwargs,
            )
        )
    return SdidResults(results)


__all__ = [
    "SdidEngine",
    "SdidResult",
    "SdidResults",
    "estimate",
    "registry",
]
