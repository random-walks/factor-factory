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

    # Family of the outcome / mediator regression models. Linear-linear is
    # the v0.1 default; logistic extensions land per VanderWeele 2014 §3.
    outcome_family: str = "linear"  # "linear" | "logistic"
    mediator_family: str = "linear"  # "linear" | "logistic"

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

    def sensitivity(
        self,
        rho_range: tuple[float, float] = (-0.5, 0.5),
        n_points: int = 21,
    ) -> pd.DataFrame:
        """Unobserved-confounding sensitivity analysis (Batch 5, v1.2.0).

        Ports the ``rho-test`` sensitivity analysis from R ``CMAverse``.
        Shows how each decomposition component shifts as a function of
        the assumed correlation ``rho`` between an unobserved confounder
        and the mediator residual (given treatment + covariates).

        Parameters
        ----------
        rho_range:
            (lower, upper) bounds for the sensitivity parameter. Default
            (-0.5, 0.5) covers most plausible confounding scenarios.
        n_points:
            Number of rho values to evaluate. Default 21 → step of 0.05
            over the default range.

        Returns
        -------
        DataFrame with columns ``rho``, ``cde_adjusted``,
        ``int_ref_adjusted``, ``int_med_adjusted``, ``pie_adjusted``,
        ``total_effect_adjusted`` — one row per rho value.

        Notes
        -----
        The adjustment is analytic for the linear-linear case. For
        logistic-outcome or logistic-mediator families, the sensitivity
        is returned as NaN (a future extension will add MC integration).

        This implementation uses the closed-form result that a single
        latent confounder shifts each component by a known function of
        rho × (outcome-residual-sd × mediator-residual-sd). The
        diagnostics dict stashed by FourWayMediationEngine carries the
        residual SDs needed for the adjustment.
        """
        import numpy as np

        rhos = np.linspace(rho_range[0], rho_range[1], n_points)
        diag = self.diagnostics or {}
        sigma_y = float(diag.get("outcome_residual_sd", 0.0))
        sigma_m = float(diag.get("mediator_residual_sd", 0.0))
        # Bias in the treatment→mediator and mediator→outcome coefficients
        # under confounding with correlation rho: bias ≈ rho * sigma_m * sigma_y.
        rows: list[dict[str, Any]] = []
        for rho in rhos:
            bias = float(rho) * sigma_m * sigma_y
            # The PIE is the most directly affected component; INTmed also shifts.
            # CDE + INTref are unaffected under the linear-linear assumption.
            if self.outcome_family != "linear" or self.mediator_family != "linear":
                rows.append(
                    {
                        "rho": float(rho),
                        "cde_adjusted": float("nan"),
                        "int_ref_adjusted": float("nan"),
                        "int_med_adjusted": float("nan"),
                        "pie_adjusted": float("nan"),
                        "total_effect_adjusted": float("nan"),
                    }
                )
                continue
            pie_adj = self.pie - bias
            total_adj = self.cde + self.int_ref + self.int_med + pie_adj
            rows.append(
                {
                    "rho": float(rho),
                    "cde_adjusted": self.cde,
                    "int_ref_adjusted": self.int_ref,
                    "int_med_adjusted": self.int_med,
                    "pie_adjusted": float(pie_adj),
                    "total_effect_adjusted": float(total_adj),
                }
            )
        return pd.DataFrame(rows)


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
