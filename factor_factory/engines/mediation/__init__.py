"""Mediation-analysis engines.

Closes a Python-ecosystem gap: the four-way mediation decomposition
(VanderWeele 2014) has no maintained Python implementation as of late
2025. The reference R package is ``CMAverse``; this module ports the
linear-linear case directly. Logistic-outcome / logistic-mediator
extensions ship in v0.2.

For the simpler Imai-Keele-Tingley two-component decomposition
(NDE / NIE), use ``statsmodels.stats.mediation.Mediation`` directly.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from ...tidy.panel import Panel
from .._registry import EngineRegistry
from ._base import MediationEngine, MediationResult
from .four_way import FourWayMediationEngine

_engines: dict[str, MediationEngine] = {"four_way": FourWayMediationEngine()}

registry: EngineRegistry[MediationEngine] = EngineRegistry(_engines)


class MediationResults:
    def __init__(self, results: list[MediationResult]) -> None:
        self.results = results

    def __iter__(self) -> Iterable[MediationResult]:
        return iter(self.results)

    def __getitem__(self, key: int | str) -> MediationResult:
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
    methods: tuple[str, ...] = ("four_way",),
    outcome: str | None = None,
    treatment: str = "treatment",
    mediator: str = "mediator",
    covariates: tuple[str, ...] = (),
    n_bootstrap: int = 1000,
    **engine_specific_kwargs: Any,
) -> MediationResults:
    """Estimate the four-way mediation decomposition under one or more methods."""
    outcome = outcome or panel.outcome_col
    if not methods:
        raise ValueError("methods must be non-empty.")
    results: list[MediationResult] = []
    for m in methods:
        engine = registry[m]
        results.append(
            engine.fit(
                panel,
                outcome=outcome,
                treatment=treatment,
                mediator=mediator,
                covariates=covariates,
                n_bootstrap=n_bootstrap,
                **engine_specific_kwargs,
            )
        )
    return MediationResults(results)


__all__ = [
    "MediationEngine",
    "MediationResult",
    "MediationResults",
    "estimate",
    "registry",
]
