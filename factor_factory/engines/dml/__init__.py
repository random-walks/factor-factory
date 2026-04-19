"""DoubleML engines — cross-fit double/debiased machine learning."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from ...tidy.panel import Panel
from .._registry import EngineRegistry
from ._base import DmlEngine, DmlResult

_engines: dict[str, DmlEngine] = {}

try:
    from .plr import DmlPlrEngine

    _engines["plr"] = DmlPlrEngine()
except ImportError:  # pragma: no cover
    pass

registry: EngineRegistry[DmlEngine] = EngineRegistry(_engines)


class DmlResults:
    def __init__(self, results: list[DmlResult]) -> None:
        self.results = results

    def __iter__(self) -> Iterable[DmlResult]:
        return iter(self.results)

    def __getitem__(self, key: int | str) -> DmlResult:
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
    methods: tuple[str, ...] = ("plr",),
    outcome: str | None = None,
    treatment: str = "treatment",
    covariates: tuple[str, ...] = (),
    **engine_specific_kwargs: Any,
) -> DmlResults:
    outcome = outcome or panel.outcome_col
    if not methods:
        raise ValueError("methods must be non-empty.")
    return DmlResults(
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


__all__ = ["DmlEngine", "DmlResult", "DmlResults", "estimate", "registry"]
