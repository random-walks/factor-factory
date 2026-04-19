"""Mediation-analysis engine Protocol + Result dataclass.

Mediation analysis decomposes the total effect of a treatment ``A``
on an outcome ``Y`` into components that act *through* a mediator
``M`` and components that bypass it. Required for any "how does the
intervention work" question — population health (does the diet
intervention improve cardiac outcomes through cholesterol or via some
other path?), policy (does the school-funding boost graduation rates
through teacher quality or via some other path?), behavioral econ
(does the price nudge change behavior through perceived value or via
attention?).

The four-way decomposition (VanderWeele 2014) — implemented here —
splits the total effect into:

- **CDE** (Controlled Direct Effect): effect of A on Y holding M fixed
- **INTref** (Reference Interaction): interaction component when A
  changes but M is held at its A=0 value
- **INTmed** (Mediated Interaction): interaction component due to M
  shifting as A changes
- **PIE** (Pure Indirect Effect): effect via M without interaction

References
----------
VanderWeele, T. J. (2014). A unification of mediation and interaction:
A four-way decomposition. *Epidemiology*, 25(5), 749-761.
https://doi.org/10.1097/EDE.0000000000000121

VanderWeele, T. J. (2015). *Explanation in Causal Inference: Methods
for Mediation and Interaction*. Oxford University Press.

The reference R package is ``CMAverse`` (Liu, Bhavsar, VanderWeele):
https://bs1125.github.io/CMAverse/. As of late 2025 there is no
maintained Python equivalent of the four-way decomposition — closing
that ecosystem gap was one of the design motivations for
factor-factory.

For the simpler Imai-Keele-Tingley two-component decomposition
(NDE / NIE), use ``statsmodels.stats.mediation.Mediation`` directly.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

import pandas as pd

from ...tidy.panel import Panel


@dataclass(frozen=True)
class MediationResult:
    """Result of a four-way mediation decomposition (VanderWeele 2014)."""

    method: str
    n_subjects: int
    treatment: str
    mediator: str
    outcome: str

    # Four-way decomposition
    total_effect: float
    cde: float  # Controlled Direct Effect (at m=reference_level)
    int_ref: float  # Reference Interaction
    int_med: float  # Mediated Interaction
    pie: float  # Pure Indirect Effect

    # Sanity check: components should sum to total_effect
    decomposition_residual: float

    # Per-component standard errors (bootstrap)
    total_effect_se: float | None = None
    cde_se: float | None = None
    int_ref_se: float | None = None
    int_med_se: float | None = None
    pie_se: float | None = None

    # Per-component 95% CIs (bootstrap percentile)
    confidence_intervals: dict[str, tuple[float, float]] | None = None

    # Proportion of total effect attributable to each component
    proportion_eliminated: float | None = None  # 1 - CDE / TE
    proportion_mediated: float | None = None  # (PIE + INTmed) / TE

    diagnostics: dict[str, Any] | None = None
    meta: dict[str, Any] | None = field(default=None, repr=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "method": self.method,
            "n_subjects": self.n_subjects,
            "treatment": self.treatment,
            "mediator": self.mediator,
            "outcome": self.outcome,
            "total_effect": self.total_effect,
            "cde": self.cde,
            "int_ref": self.int_ref,
            "int_med": self.int_med,
            "pie": self.pie,
            "decomposition_residual": self.decomposition_residual,
            "total_effect_se": self.total_effect_se,
            "cde_se": self.cde_se,
            "int_ref_se": self.int_ref_se,
            "int_med_se": self.int_med_se,
            "pie_se": self.pie_se,
            "confidence_intervals": (
                {k: list(v) for k, v in self.confidence_intervals.items()}
                if self.confidence_intervals
                else None
            ),
            "proportion_eliminated": self.proportion_eliminated,
            "proportion_mediated": self.proportion_mediated,
            "diagnostics": self.diagnostics,
        }

    def summary_table(self) -> pd.DataFrame:
        """One-row summary table for tearsheet rendering (added v1.1.0, Batch 4)."""
        row = {
            "method": self.method,
            "n_subjects": self.n_subjects,
            "total_effect": self.total_effect,
            "cde": self.cde,
            "int_ref": self.int_ref,
            "int_med": self.int_med,
            "pie": self.pie,
            "decomposition_residual": self.decomposition_residual,
            "prop_mediated": self.proportion_mediated,
            "prop_eliminated": self.proportion_eliminated,
        }
        return pd.DataFrame([row]).set_index("method")


class MediationEngine(Protocol):
    """Protocol every mediation engine adapter must satisfy."""

    name: str

    def fit(
        self,
        panel: Panel,
        *,
        outcome: str,
        treatment: str,
        mediator: str,
        covariates: tuple[str, ...] = (),
        n_bootstrap: int = 0,
        **engine_specific_kwargs: Any,
    ) -> MediationResult:
        """Fit the mediation decomposition."""
        ...
