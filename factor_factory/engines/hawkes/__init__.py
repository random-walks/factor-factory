"""Hawkes self-exciting point-process engines.

References
----------
Hawkes, A. G. (1971). Spectra of some self-exciting and mutually
exciting point processes. *Biometrika*, 58(1), 83-90.

Bacry, E., Delattre, S., Hoffmann, M., & Muzy, J.-F. (2013). Some
limit theorems for Hawkes processes and application to financial
statistics. *Stochastic Processes and their Applications*, 123(7),
2475-2499.

Reference implementation: ``tick`` package
(https://x-datainitiative.github.io/tick/).
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any, Protocol

import numpy as np
import pandas as pd

from ...tidy.panel import Panel
from .._registry import EngineRegistry


@dataclass(frozen=True)
class HawkesResult:
    method: str
    baseline_intensities: np.ndarray
    excitation_matrix: np.ndarray
    branching_ratio: float
    log_likelihood: float | None = None
    n_events: int = 0
    n_dimensions: int = 0
    kernel: str = "exp"
    diagnostics: dict[str, Any] | None = None
    meta: dict[str, Any] | None = field(default=None, repr=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "method": self.method,
            "baseline_intensities": self.baseline_intensities.tolist(),
            "excitation_matrix": self.excitation_matrix.tolist(),
            "branching_ratio": self.branching_ratio,
            "log_likelihood": self.log_likelihood,
            "n_events": self.n_events,
            "n_dimensions": self.n_dimensions,
            "kernel": self.kernel,
            "diagnostics": self.diagnostics,
        }

    def summary_table(self) -> pd.DataFrame:
        row = {
            "method": self.method,
            "branching_ratio": self.branching_ratio,
            "n_events": self.n_events,
            "n_dimensions": self.n_dimensions,
            "kernel": self.kernel,
        }
        return pd.DataFrame([row]).set_index("method")


class HawkesEngine(Protocol):
    name: str

    def fit(
        self,
        panel: Panel,
        *,
        timestamp_col: str = "timestamp",
        **engine_specific_kwargs: Any,
    ) -> HawkesResult: ...


class TickHawkesEngine:
    """Univariate or multivariate Hawkes fit via tick."""

    name = "tick"

    def fit(
        self,
        panel: Panel,
        *,
        timestamp_col: str = "timestamp",
        decay: float = 1.0,
        **_engine_specific_kwargs: Any,
    ) -> HawkesResult:
        try:
            from tick.hawkes import HawkesExpKern
        except ImportError as exc:  # pragma: no cover
            raise ImportError(
                "TickHawkesEngine requires `tick`. Install via "
                "`pip install factor-factory[hawkes]`."
            ) from exc

        df = panel.df.reset_index()
        if timestamp_col not in df.columns:
            raise ValueError(
                f"Hawkes requires a {timestamp_col!r} column listing event times."
            )

        # Group by unit — each unit = one dimension of the multivariate process.
        units = sorted(df["unit_id"].unique())
        event_times_by_unit = [
            np.sort(df[df["unit_id"] == u][timestamp_col].to_numpy(dtype=float))
            for u in units
        ]
        end_time = float(max(t[-1] for t in event_times_by_unit if len(t) > 0))

        learner = HawkesExpKern(decays=decay)
        learner.fit([event_times_by_unit])
        baseline = np.asarray(learner.baseline, dtype=float)
        adjacency = np.asarray(learner.adjacency, dtype=float)

        # Branching ratio = spectral radius of the excitation matrix integrated.
        # For exp kernel with decay α: integral is ||A||_∞ / α; branching ratio
        # is the spectral radius of A / α.
        if adjacency.ndim >= 2:
            excitation_normalized = adjacency.reshape(len(units), len(units)) / decay
            branching = float(np.max(np.abs(np.linalg.eigvals(excitation_normalized))))
        else:
            branching = float("nan")

        return HawkesResult(
            method=self.name,
            baseline_intensities=baseline,
            excitation_matrix=adjacency.reshape(len(units), len(units))
            if adjacency.ndim >= 2 else adjacency,
            branching_ratio=branching,
            log_likelihood=float(learner.score()) if hasattr(learner, "score") else None,
            n_events=int(sum(len(t) for t in event_times_by_unit)),
            n_dimensions=len(units),
            kernel="exp",
            diagnostics={"decay": decay, "end_time": end_time},
        )


import contextlib as _contextlib  # noqa: E402

_engines: dict[str, HawkesEngine] = {}
with _contextlib.suppress(Exception):  # pragma: no cover
    _engines["tick"] = TickHawkesEngine()
registry: EngineRegistry[HawkesEngine] = EngineRegistry(_engines)


class HawkesResults:
    def __init__(self, results: list[HawkesResult]) -> None:
        self.results = results

    def __iter__(self) -> Iterable[HawkesResult]:
        return iter(self.results)

    def __getitem__(self, key: int | str) -> HawkesResult:
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
    methods: tuple[str, ...] = ("tick",),
    timestamp_col: str = "timestamp",
    **engine_specific_kwargs: Any,
) -> HawkesResults:
    if not methods:
        raise ValueError("methods must be non-empty.")
    return HawkesResults(
        [
            registry[m].fit(panel, timestamp_col=timestamp_col, **engine_specific_kwargs)
            for m in methods
        ]
    )


__all__ = [
    "HawkesEngine",
    "HawkesResult",
    "HawkesResults",
    "TickHawkesEngine",
    "estimate",
    "registry",
]
