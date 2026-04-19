"""Synthetic-Control Method engines.

Adapters:
- ``pysyncon`` — classic SCM via the pysyncon package (Abadie et al. 2010).
- ``augmented`` — Augmented SCM (Ben-Michael et al. 2021), homegrown.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from ...tidy.panel import Panel
from .._registry import EngineRegistry
from ._base import ScmEngine, ScmResult
from .augmented import AugmentedScmEngine
from .matrix_completion import MatrixCompletionEngine

_engines: dict[str, ScmEngine] = {
    "augmented": AugmentedScmEngine(),
    "matrix_completion": MatrixCompletionEngine(),
}

try:
    from .pysyncon_adapter import PysynconEngine

    _engines["pysyncon"] = PysynconEngine()
except ImportError:  # pragma: no cover
    pass

registry: EngineRegistry[ScmEngine] = EngineRegistry(_engines)


class ScmResults:
    def __init__(self, results: list[ScmResult]) -> None:
        self.results = results

    def __iter__(self) -> Iterable[ScmResult]:
        return iter(self.results)

    def __getitem__(self, key: int | str) -> ScmResult:
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
    methods: tuple[str, ...] = ("augmented",),
    outcome: str | None = None,
    treatment: str = "treatment",
    **engine_specific_kwargs: Any,
) -> ScmResults:
    outcome = outcome or panel.outcome_col
    if not methods:
        raise ValueError("methods must be non-empty.")
    results = [
        registry[m].fit(panel, outcome=outcome, treatment=treatment, **engine_specific_kwargs)
        for m in methods
    ]
    return ScmResults(results)


__all__ = ["ScmEngine", "ScmResult", "ScmResults", "estimate", "registry"]
