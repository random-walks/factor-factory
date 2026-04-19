"""Regression-Discontinuity engine Protocol + Result dataclass."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

import pandas as pd

from ...tidy.panel import Panel


@dataclass(frozen=True)
class RddResult:
    """Result of a single regression-discontinuity fit.

    Sharp RDD: ``estimate`` is the jump at the cutoff.
    Fuzzy RDD: ``estimate`` is the IV-style Wald LATE; ``first_stage_f``
    captures first-stage strength.
    """

    method: str
    design: str  # "sharp" | "fuzzy"
    cutoff: float
    estimate: float
    std_error: float
    ci_95: tuple[float, float]
    p_value: float
    bandwidth: float
    kernel: str
    polynomial_order: int
    n_effective: int
    n_total: int

    first_stage_f: float | None = None  # fuzzy RDD only
    covariate_balance_pvalues: dict[str, float] | None = None
    diagnostics: dict[str, Any] | None = None
    meta: dict[str, Any] | None = field(default=None, repr=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "method": self.method,
            "design": self.design,
            "cutoff": self.cutoff,
            "estimate": self.estimate,
            "std_error": self.std_error,
            "ci_95_lower": self.ci_95[0],
            "ci_95_upper": self.ci_95[1],
            "p_value": self.p_value,
            "bandwidth": self.bandwidth,
            "kernel": self.kernel,
            "polynomial_order": self.polynomial_order,
            "n_effective": self.n_effective,
            "n_total": self.n_total,
            "first_stage_f": self.first_stage_f,
            "covariate_balance_pvalues": self.covariate_balance_pvalues,
            "diagnostics": self.diagnostics,
        }

    def summary_table(self) -> pd.DataFrame:
        row = {
            "method": self.method,
            "design": self.design,
            "cutoff": self.cutoff,
            "estimate": self.estimate,
            "se": self.std_error,
            "ci_lo": self.ci_95[0],
            "ci_hi": self.ci_95[1],
            "p_value": self.p_value,
            "bandwidth": self.bandwidth,
            "n_eff": self.n_effective,
        }
        return pd.DataFrame([row]).set_index("method")


class RddEngine(Protocol):
    """Protocol every RDD engine adapter must satisfy."""

    name: str

    def fit(
        self,
        panel: Panel,
        *,
        outcome: str,
        running_variable: str,
        cutoff: float = 0.0,
        design: str = "sharp",
        treatment: str | None = None,
        **engine_specific_kwargs: Any,
    ) -> RddResult:
        """Fit the RDD estimator and return a ``RddResult``."""
        ...
