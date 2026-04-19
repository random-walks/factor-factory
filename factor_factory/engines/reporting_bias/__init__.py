"""Reporting-bias engine — two-class latent-EM under-reporting estimator.

Homegrown (no mature Python upstream). Estimates the fraction of true
events under-reported by modeling observed counts as a mixture of
"reporters" (observe with probability p) and "non-reporters"
(observe with probability q << p).

References
----------
No single canonical paper; the pattern appears throughout civic-data
research (311-complaint under-reporting, police-incident under-
reporting, medical-claim false-negatives). Inspired by:

- Dempster, Laird, & Rubin (1977). Maximum likelihood from incomplete
  data via the EM algorithm. *JRSS:B*, 39(1), 1-38.
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
class ReportingBiasResult:
    method: str
    p_reporter: float  # reporting rate among reporters
    p_non_reporter: float  # reporting rate among non-reporters
    pi_reporter: float  # mixture share of reporters
    inferred_true_rate: float  # estimated true event rate
    observed_rate: float
    n_units: int = 0
    n_em_iterations: int = 0
    log_likelihood: float | None = None
    diagnostics: dict[str, Any] | None = None
    meta: dict[str, Any] | None = field(default=None, repr=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "method": self.method,
            "p_reporter": self.p_reporter,
            "p_non_reporter": self.p_non_reporter,
            "pi_reporter": self.pi_reporter,
            "inferred_true_rate": self.inferred_true_rate,
            "observed_rate": self.observed_rate,
            "n_units": self.n_units,
            "n_em_iterations": self.n_em_iterations,
            "log_likelihood": self.log_likelihood,
            "diagnostics": self.diagnostics,
        }

    def summary_table(self) -> pd.DataFrame:
        row = {
            "method": self.method,
            "observed_rate": self.observed_rate,
            "inferred_true_rate": self.inferred_true_rate,
            "p_reporter": self.p_reporter,
            "p_non_reporter": self.p_non_reporter,
            "pi_reporter": self.pi_reporter,
        }
        return pd.DataFrame([row]).set_index("method")


class ReportingBiasEngine(Protocol):
    name: str

    def fit(
        self,
        panel: Panel,
        *,
        outcome: str,
        exposure: str | None = None,
        **engine_specific_kwargs: Any,
    ) -> ReportingBiasResult: ...


class LatentEmEngine:
    """Two-class latent-EM under-reporting estimator.

    Each unit is either a 'reporter' (reporting probability p) or a
    'non-reporter' (reporting probability q), with mixture share π.
    EM iterates between estimating class membership from observed
    counts and re-estimating (p, q, π).
    """

    name = "latent_em"

    def fit(
        self,
        panel: Panel,
        *,
        outcome: str,
        exposure: str | None = None,
        max_iter: int = 100,
        tol: float = 1e-6,
        random_state: int = 42,
        **_engine_specific_kwargs: Any,
    ) -> ReportingBiasResult:
        df = panel.df.reset_index()
        # Aggregate to unit-level event counts + exposure.
        if exposure and exposure in df.columns:
            agg = df.groupby("unit_id").agg({outcome: "sum", exposure: "sum"}).reset_index()
            n = agg[exposure].to_numpy(dtype=float)
        else:
            agg = df.groupby("unit_id")[outcome].sum().reset_index()
            n = np.full(len(agg), df.groupby("unit_id").size().mean())
        k = agg[outcome].to_numpy(dtype=float)
        n_units = int(len(k))

        rng = np.random.default_rng(random_state)
        p = 0.8 + rng.uniform(-0.1, 0.1)  # reporters
        q = 0.2 + rng.uniform(-0.1, 0.1)  # non-reporters
        pi = 0.5

        log_lik_prev = -np.inf
        log_lik = -np.inf
        iteration = 0
        for iteration in range(max_iter):  # noqa: B007
            # E-step: posterior for reporter class.
            # Binomial p.m.f. ratio (log-space for stability).
            log_pi_r = np.log(pi) + k * np.log(p + 1e-12) + (n - k) * np.log(1 - p + 1e-12)
            log_pi_nr = np.log(1 - pi) + k * np.log(q + 1e-12) + (n - k) * np.log(1 - q + 1e-12)
            max_log = np.maximum(log_pi_r, log_pi_nr)
            log_lik = float(np.sum(max_log + np.log(np.exp(log_pi_r - max_log) + np.exp(log_pi_nr - max_log))))
            gamma = np.exp(log_pi_r - max_log) / (
                np.exp(log_pi_r - max_log) + np.exp(log_pi_nr - max_log)
            )

            # M-step.
            pi = float(np.mean(gamma))
            p = float(np.sum(gamma * k) / np.sum(gamma * n))
            q = float(np.sum((1 - gamma) * k) / np.sum((1 - gamma) * n))

            if abs(log_lik - log_lik_prev) < tol:
                break
            log_lik_prev = log_lik

        observed_rate = float(np.sum(k) / np.sum(n))
        # Best-case true rate = the higher of p (reporter) / q (non-reporter).
        inferred_true = float(max(p, q))

        return ReportingBiasResult(
            method=self.name,
            p_reporter=p,
            p_non_reporter=q,
            pi_reporter=pi,
            inferred_true_rate=inferred_true,
            observed_rate=observed_rate,
            n_units=n_units,
            n_em_iterations=iteration + 1,
            log_likelihood=log_lik,
            diagnostics={"converged": iteration + 1 < max_iter},
        )


_engines: dict[str, ReportingBiasEngine] = {"latent_em": LatentEmEngine()}
registry: EngineRegistry[ReportingBiasEngine] = EngineRegistry(_engines)


class ReportingBiasResults:
    def __init__(self, results: list[ReportingBiasResult]) -> None:
        self.results = results

    def __iter__(self) -> Iterable[ReportingBiasResult]:
        return iter(self.results)

    def __getitem__(self, key: int | str) -> ReportingBiasResult:
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
    methods: tuple[str, ...] = ("latent_em",),
    outcome: str | None = None,
    exposure: str | None = None,
    **engine_specific_kwargs: Any,
) -> ReportingBiasResults:
    outcome = outcome or panel.outcome_col
    if not methods:
        raise ValueError("methods must be non-empty.")
    return ReportingBiasResults(
        [
            registry[m].fit(panel, outcome=outcome, exposure=exposure, **engine_specific_kwargs)
            for m in methods
        ]
    )


__all__ = [
    "LatentEmEngine",
    "ReportingBiasEngine",
    "ReportingBiasResult",
    "ReportingBiasResults",
    "estimate",
    "registry",
]
