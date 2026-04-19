"""Regression-Discontinuity engines + ``estimate()`` dispatcher.

Domain: any setting where treatment assignment is a deterministic
function of a running variable crossing a threshold (test-score
cutoffs for scholarships, vote-share cutoffs in close elections,
clinical-dosing thresholds, geographic discontinuities at borders).

Adapters (v0.2+):
- ``rd_robust`` — wraps ``rdrobust`` (Calonico-Cattaneo-Titiunik 2014).
  MSE-optimal bandwidth + robust bias-corrected SEs. Sharp + fuzzy.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from ...tidy.panel import Panel
from .._registry import EngineRegistry
from ._base import RddEngine, RddResult

_engines: dict[str, RddEngine] = {}

try:
    from .rd_robust import RdRobustEngine

    _engines["rd_robust"] = RdRobustEngine()
except ImportError:  # pragma: no cover
    pass

registry: EngineRegistry[RddEngine] = EngineRegistry(_engines)


class RddResults:
    def __init__(self, results: list[RddResult]) -> None:
        self.results = results

    def __iter__(self) -> Iterable[RddResult]:
        return iter(self.results)

    def __getitem__(self, key: int | str) -> RddResult:
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
    methods: tuple[str, ...] = ("rd_robust",),
    outcome: str | None = None,
    running_variable: str,
    cutoff: float = 0.0,
    design: str = "sharp",
    treatment: str | None = None,
    **engine_specific_kwargs: Any,
) -> RddResults:
    """Estimate the RDD effect under one or more adapters."""
    outcome = outcome or panel.outcome_col
    if not methods:
        raise ValueError("methods must be non-empty.")
    results: list[RddResult] = []
    for m in methods:
        engine = registry[m]
        results.append(
            engine.fit(
                panel,
                outcome=outcome,
                running_variable=running_variable,
                cutoff=cutoff,
                design=design,
                treatment=treatment,
                **engine_specific_kwargs,
            )
        )
    return RddResults(results)


__all__ = ["RddEngine", "RddResult", "RddResults", "estimate", "registry"]
