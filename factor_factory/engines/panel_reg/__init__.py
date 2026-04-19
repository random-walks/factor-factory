"""Panel-regression (HDFE) engines."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from ...tidy.panel import Panel
from .._registry import EngineRegistry
from ._base import PanelRegEngine, PanelRegResult

_engines: dict[str, PanelRegEngine] = {}

try:
    from .pyfixest_adapter import PyfixestEngine

    _engines["pyfixest"] = PyfixestEngine()
except ImportError:  # pragma: no cover
    pass

registry: EngineRegistry[PanelRegEngine] = EngineRegistry(_engines)


class PanelRegResults:
    def __init__(self, results: list[PanelRegResult]) -> None:
        self.results = results

    def __iter__(self) -> Iterable[PanelRegResult]:
        return iter(self.results)

    def __getitem__(self, key: int | str) -> PanelRegResult:
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
    methods: tuple[str, ...] = ("pyfixest",),
    outcome: str | None = None,
    regressors: tuple[str, ...] = (),
    fixed_effects: tuple[str, ...] = (),
    cluster: str | None = None,
    **engine_specific_kwargs: Any,
) -> PanelRegResults:
    outcome = outcome or panel.outcome_col
    if not methods:
        raise ValueError("methods must be non-empty.")
    if not regressors:
        raise ValueError("At least one regressor is required.")
    return PanelRegResults(
        [
            registry[m].fit(
                panel,
                outcome=outcome,
                regressors=regressors,
                fixed_effects=fixed_effects,
                cluster=cluster,
                **engine_specific_kwargs,
            )
            for m in methods
        ]
    )


__all__ = ["PanelRegEngine", "PanelRegResult", "PanelRegResults", "estimate", "registry"]
