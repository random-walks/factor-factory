"""Synthetic Difference-in-Differences engine Protocol + Result dataclass.

References
----------
Arkhangelsky, D., Athey, S., Hirshberg, D. A., Imbens, G. W., & Wager,
S. (2021). Synthetic Difference-in-Differences. *American Economic
Review*, 111(12), 4088-4118.
https://doi.org/10.1257/aer.20190159

Reference R implementation: ``synthdid`` package, Stanford team.
https://synth-inference.github.io/synthdid/

Why this engine exists in factor-factory
----------------------------------------
SDID is a high-impact econometric advance from 2021 that has no
mature first-class Python implementation as of late 2025 (the R
``synthdid`` package is canonical; partial Python ports like
``pysdid`` are lightly maintained). Closing this Python-ecosystem gap
was one of the design motivations for factor-factory.

The estimator combines:

1. **Unit weights** ``ω̂`` (synthetic-control style): control units
   re-weighted to match treated units' pre-treatment outcome trend.
2. **Time weights** ``λ̂``: pre-treatment periods re-weighted to
   match each control unit's post-treatment outcome.
3. **Weighted DiD**: standard two-way FE regression weighted by
   ``ω̃_i × λ̃_t``.

Compared to standard DiD: more robust to violations of parallel
trends. Compared to vanilla SCM: provides valid inference (jackknife
or placebo) and handles multiple treated units more cleanly.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

import numpy as np
import pandas as pd

from ...tidy.panel import Panel


@dataclass(frozen=True)
class SdidResult:
    """Result of a Synthetic DiD fit (Arkhangelsky et al. 2021)."""

    method: str
    att: float
    se: float
    ci_95: tuple[float, float]
    p_value: float
    n: int

    # Unit weights (control units only)
    unit_weights: dict[Any, float] | None = None
    # Time weights (pre-treatment periods only)
    time_weights: dict[Any, float] | None = None
    # Number of treated units / pre periods / post periods
    n_treated: int | None = None
    n_control: int | None = None
    n_pre: int | None = None
    n_post: int | None = None

    diagnostics: dict[str, Any] | None = None
    meta: dict[str, Any] | None = field(default=None, repr=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "method": self.method,
            "att": self.att,
            "se": self.se,
            "ci_95_lower": self.ci_95[0],
            "ci_95_upper": self.ci_95[1],
            "p_value": self.p_value,
            "n": self.n,
            "n_treated": self.n_treated,
            "n_control": self.n_control,
            "n_pre": self.n_pre,
            "n_post": self.n_post,
            "diagnostics": self.diagnostics,
        }

    def summary_table(self) -> pd.DataFrame:
        """One-row summary table for tearsheet rendering (added v1.1.0, Batch 4)."""
        row = {
            "method": self.method,
            "att": self.att,
            "se": self.se,
            "ci_lo": self.ci_95[0],
            "ci_hi": self.ci_95[1],
            "p_value": self.p_value,
            "n": self.n,
            "n_treated": self.n_treated,
            "n_control": self.n_control,
        }
        return pd.DataFrame([row]).set_index("method")


class SdidEngine(Protocol):
    """Protocol every SDID engine adapter must satisfy.

    Domain: panel data with a single treatment block (one or more
    treated units, one treatment date). For staggered rollout, see
    ``engines.did.callaway_santanna`` instead.
    """

    name: str

    def fit(
        self,
        panel: Panel,
        *,
        outcome: str,
        treatment: str = "treatment",
        cluster: str | None = None,
        **engine_specific_kwargs: Any,
    ) -> SdidResult:
        """Fit SDID on ``panel``."""
        ...


def _pivot_panel_to_matrix(
    panel: Panel, outcome: str, treatment: str
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Reshape a Panel into wide (units × periods) Y and W matrices."""
    df = panel.df
    if outcome not in df.columns:
        raise ValueError(f"Panel missing outcome column {outcome!r}.")
    if treatment not in df.columns:
        raise ValueError(
            f"Panel missing treatment column {treatment!r}. "
            "Build the panel with treatment_events to populate it."
        )
    y = df[outcome].unstack("period")
    w = df[treatment].unstack("period").astype(np.int8)
    if y.shape != w.shape:
        raise AssertionError("Internal: Y and W shapes diverged after unstack.")
    return y, w
