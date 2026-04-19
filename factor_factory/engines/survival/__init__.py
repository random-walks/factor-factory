"""Survival-analysis engines + ``estimate()`` dispatcher.

Engines: KaplanMeier (non-parametric), CoxPH (semi-parametric).

Domain coverage: oncology trials, churn prediction, hardware
failure, pharmacokinetics, equipment reliability, customer
retention — anywhere the outcome is "time until event" with
right-censoring.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from ...tidy.panel import Panel
from .._registry import EngineRegistry
from ._base import SurvivalEngine, SurvivalResult

_engines: dict[str, SurvivalEngine] = {}

try:
    from .kaplan_meier import KaplanMeierEngine

    _engines["kaplan_meier"] = KaplanMeierEngine()
except ImportError:  # pragma: no cover
    pass

try:
    from .cox_ph import CoxPHEngine

    _engines["cox_ph"] = CoxPHEngine()
except ImportError:  # pragma: no cover
    pass

registry: EngineRegistry[SurvivalEngine] = EngineRegistry(_engines)


class SurvivalResults:
    """Wrapper around a list of ``SurvivalResult`` for side-by-side comparison."""

    def __init__(self, results: list[SurvivalResult]) -> None:
        self.results = results

    def __iter__(self) -> Iterable[SurvivalResult]:
        return iter(self.results)

    def __len__(self) -> int:
        return len(self.results)

    def __getitem__(self, key: int | str) -> SurvivalResult:
        if isinstance(key, int):
            return self.results[key]
        for r in self.results:
            if r.method == key:
                return r
        raise KeyError(
            f"No SurvivalResult with method='{key}' (have: {[r.method for r in self.results]})."
        )

    def to_records(self) -> list[dict[str, Any]]:
        return [r.to_dict() for r in self.results]


def estimate(
    panel: Panel,
    *,
    methods: tuple[str, ...] = ("kaplan_meier",),
    duration_col: str = "duration",
    event_col: str = "event",
    covariates: tuple[str, ...] = (),
    cluster: str | None = None,
    **engine_specific_kwargs: Any,
) -> SurvivalResults:
    """Estimate survival curves / hazard ratios under one or more methods.

    Default is ``"kaplan_meier"`` (non-parametric). For
    covariate-adjusted hazard ratios use ``"cox_ph"`` with
    ``covariates=("age", "treatment_arm", ...)``.
    """
    if not methods:
        raise ValueError("methods must be non-empty.")
    results: list[SurvivalResult] = []
    for m in methods:
        engine = registry[m]
        results.append(
            engine.fit(
                panel,
                duration_col=duration_col,
                event_col=event_col,
                covariates=covariates,
                cluster=cluster,
                **engine_specific_kwargs,
            )
        )
    return SurvivalResults(results)


__all__ = [
    "SurvivalEngine",
    "SurvivalResult",
    "SurvivalResults",
    "estimate",
    "registry",
]
