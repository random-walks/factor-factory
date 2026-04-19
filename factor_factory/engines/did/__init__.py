"""Difference-in-differences engines + ``estimate()`` dispatcher."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import pandas as pd

from ...tidy.panel import Panel
from .._registry import EngineRegistry
from ._base import DidEngine, DidResult

_engines: dict[str, DidEngine] = {}

# TwfeEngine pulls in linearmodels — register lazily so the default
# install (no `[did]` extra) stays importable.
try:
    from .twfe import TwfeEngine

    _engines["twfe"] = TwfeEngine()
except ImportError:  # pragma: no cover - exercised in environments lacking `linearmodels`
    pass

registry: EngineRegistry[DidEngine] = EngineRegistry(_engines)


class DidResults:
    """A small wrapper around a list of ``DidResult`` for side-by-side comparison."""

    def __init__(self, results: list[DidResult]) -> None:
        self.results = results

    def __iter__(self) -> Iterable[DidResult]:
        return iter(self.results)

    def __len__(self) -> int:
        return len(self.results)

    def __getitem__(self, key: int | str) -> DidResult:
        if isinstance(key, int):
            return self.results[key]
        for r in self.results:
            if r.method == key:
                return r
        raise KeyError(
            f"No DidResult with method='{key}' (have: {[r.method for r in self.results]})."
        )

    def summary_table(self) -> pd.DataFrame:
        """Side-by-side comparison: rows = method, columns = stats."""
        rows = []
        for r in self.results:
            rows.append(
                {
                    "method": r.method,
                    "att": r.att,
                    "se": r.se,
                    "ci_lo": r.ci_95[0],
                    "ci_hi": r.ci_95[1],
                    "p_value": r.p_value,
                    "n": r.n,
                }
            )
        return pd.DataFrame(rows).set_index("method")

    def to_records(self) -> list[dict[str, Any]]:
        return [r.to_dict() for r in self.results]


def estimate(
    panel: Panel,
    *,
    methods: tuple[str, ...] = ("twfe",),
    outcome: str | None = None,
    treatment: str = "treatment",
    cluster: str | None = None,
    **engine_specific_kwargs: Any,
) -> DidResults:
    """Estimate the DiD effect under one or more methods.

    The default method is ``"twfe"`` (TWFE via ``linearmodels``). Add
    more by installing optional extras: ``factor-factory[did]`` adds
    Callaway-Sant'Anna, Sun-Abraham, Borusyak-Jaravel-Spiess in v0.2+.
    """
    outcome = outcome or panel.outcome_col
    if not methods:
        raise ValueError("methods must be a non-empty tuple, e.g. ('twfe',).")
    results: list[DidResult] = []
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
    return DidResults(results)


__all__ = ["DidEngine", "DidResult", "DidResults", "estimate", "registry"]
