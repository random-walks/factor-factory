"""Heterogeneous-treatment-effects engines (causal forests, meta-learners, BCF)."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from ...tidy.panel import Panel
from .._registry import EngineRegistry
from ._base import HetTeEngine, HetTeResult

_engines: dict[str, HetTeEngine] = {}

try:
    from .causal_forest import CausalForestEngine

    _engines["causal_forest"] = CausalForestEngine()
except ImportError:  # pragma: no cover
    pass

registry: EngineRegistry[HetTeEngine] = EngineRegistry(_engines)


class HetTeResults:
    def __init__(self, results: list[HetTeResult]) -> None:
        self.results = results

    def __iter__(self) -> Iterable[HetTeResult]:
        return iter(self.results)

    def __getitem__(self, key: int | str) -> HetTeResult:
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
    methods: tuple[str, ...] = ("causal_forest",),
    outcome: str | None = None,
    treatment: str = "treatment",
    covariates: tuple[str, ...] = (),
    **engine_specific_kwargs: Any,
) -> HetTeResults:
    outcome = outcome or panel.outcome_col
    if not methods:
        raise ValueError("methods must be non-empty.")
    return HetTeResults(
        [
            registry[m].fit(
                panel,
                outcome=outcome,
                treatment=treatment,
                covariates=covariates,
                **engine_specific_kwargs,
            )
            for m in methods
        ]
    )


__all__ = ["HetTeEngine", "HetTeResult", "HetTeResults", "estimate", "registry"]
