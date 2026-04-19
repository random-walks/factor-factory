"""Four-way mediation decomposition (VanderWeele 2014).

Implementation notes
--------------------

For a binary treatment ``A``, mediator ``M`` (binary or continuous),
outcome ``Y`` (continuous), and optional covariates ``C``, the
four-way decomposition uses two regressions:

- **Mediator model**: ``M = β₀ + β₁ A + β_C C + u``
- **Outcome model**: ``Y = θ₀ + θ₁ A + θ₂ M + θ₃ A·M + θ_C C + e``

Under sequential ignorability (Imai, Keele, Tingley 2010), the
expected potential outcomes have closed-form expressions in the
linear case:

- ``CDE(m=0)`` = θ₁
- ``INTref``    = θ₃ · E[M | A=0, C̄] = θ₃ · (β₀ + β_C C̄)
- ``INTmed``    = θ₃ · β₁
- ``PIE``       = θ₂ · β₁
- ``Total``     = θ₁ + θ₃ · (β₀ + β_C C̄ + β₁) + θ₂ · β₁ = CDE + INTref + INTmed + PIE

Citation
--------
VanderWeele, T. J. (2014). A unification of mediation and interaction:
A four-way decomposition. *Epidemiology*, 25(5), 749-761.
https://doi.org/10.1097/EDE.0000000000000121

VanderWeele, T. J., & Vansteelandt, S. (2014). Mediation analysis with
multiple mediators. *Epidemiologic Methods*, 2(1), 95-115.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

from ...tidy.panel import Panel
from ._base import MediationResult


class FourWayMediationEngine:
    """Four-way mediation decomposition for linear-linear models.

    Currently supports continuous outcome with binary treatment +
    binary or continuous mediator. Logistic-outcome / logistic-mediator
    extensions ship in v0.2 (the math is the same but requires
    Monte-Carlo integration; see VanderWeele 2014 §3 for details).
    """

    name = "four_way"

    def fit(
        self,
        panel: Panel,
        *,
        outcome: str,
        treatment: str,
        mediator: str,
        covariates: tuple[str, ...] = (),
        n_bootstrap: int = 1000,
        random_state: int = 20260420,
        **_engine_specific_kwargs: Any,
    ) -> MediationResult:
        df = _flatten_to_subject_table(panel, outcome, treatment, mediator, covariates)

        # Point estimate
        components = _fit_decomposition(df, outcome, treatment, mediator, covariates)
        residual = (
            components["total_effect"]
            - components["cde"]
            - components["int_ref"]
            - components["int_med"]
            - components["pie"]
        )

        # Bootstrap inference
        boot_results: dict[str, list[float]] | None = None
        ses: dict[str, float] = {}
        cis: dict[str, tuple[float, float]] = {}
        if n_bootstrap > 0:
            boot_results = _bootstrap_decomposition(
                df, outcome, treatment, mediator, covariates, n_bootstrap, random_state
            )
            for key, samples in boot_results.items():
                arr = np.asarray(samples)
                ses[key] = float(arr.std(ddof=1))
                cis[key] = (float(np.percentile(arr, 2.5)), float(np.percentile(arr, 97.5)))

        te = components["total_effect"]
        proportion_mediated = (
            (components["pie"] + components["int_med"]) / te if abs(te) > 1e-9 else None
        )
        proportion_eliminated = 1.0 - components["cde"] / te if abs(te) > 1e-9 else None

        return MediationResult(
            method=self.name,
            n_subjects=int(len(df)),
            treatment=treatment,
            mediator=mediator,
            outcome=outcome,
            total_effect=float(te),
            cde=float(components["cde"]),
            int_ref=float(components["int_ref"]),
            int_med=float(components["int_med"]),
            pie=float(components["pie"]),
            decomposition_residual=float(residual),
            total_effect_se=ses.get("total_effect"),
            cde_se=ses.get("cde"),
            int_ref_se=ses.get("int_ref"),
            int_med_se=ses.get("int_med"),
            pie_se=ses.get("pie"),
            confidence_intervals=cis or None,
            proportion_eliminated=(
                float(proportion_eliminated) if proportion_eliminated is not None else None
            ),
            proportion_mediated=(
                float(proportion_mediated) if proportion_mediated is not None else None
            ),
            diagnostics={
                "n_bootstrap": n_bootstrap,
                "n_covariates": len(covariates),
                "model_class": "linear_linear",
            },
            meta={
                "outcome_coefs": components["outcome_coefs"],
                "mediator_coefs": components["mediator_coefs"],
            },
        )


# ─── core decomposition ────────────────────────────────────────────────────


def _fit_decomposition(
    df: pd.DataFrame,
    outcome: str,
    treatment: str,
    mediator: str,
    covariates: tuple[str, ...],
) -> dict[str, Any]:
    """Compute the four components for a single sample (linear-linear)."""
    # Mediator model: M = β_0 + β_1 A + β_C C
    m_x_cols = [treatment, *covariates]
    M_endog = df[mediator].to_numpy(dtype=float)
    M_exog = _design_matrix(df[m_x_cols])
    beta = np.asarray(np.linalg.lstsq(M_exog, M_endog, rcond=None)[0], dtype=np.float64)
    beta_0 = float(beta[0])
    beta_1 = float(beta[1])  # coefficient on A
    beta_C = beta[2:] if len(covariates) > 0 else np.array([], dtype=np.float64)

    # Outcome model: Y = θ_0 + θ_1 A + θ_2 M + θ_3 A*M + θ_C C
    df = df.copy()
    df["__interaction"] = df[treatment].astype(float) * df[mediator].astype(float)
    y_x_cols = [treatment, mediator, "__interaction", *covariates]
    Y_endog = df[outcome].to_numpy(dtype=float)
    Y_exog = _design_matrix(df[y_x_cols])
    theta = np.asarray(np.linalg.lstsq(Y_exog, Y_endog, rcond=None)[0], dtype=np.float64)
    theta_1 = float(theta[1])  # A
    theta_2 = float(theta[2])  # M
    theta_3 = float(theta[3])  # A*M

    # E[M | A=0, C̄] using mean covariates
    if len(covariates) > 0:
        c_mean = df[list(covariates)].mean().to_numpy(dtype=float)
        m_at_a_zero = beta_0 + float(beta_C @ c_mean)
    else:
        m_at_a_zero = beta_0

    cde = theta_1  # CDE at m=0 (per VanderWeele 2014 §2)
    int_ref = theta_3 * m_at_a_zero  # reference interaction
    int_med = theta_3 * beta_1  # mediated interaction
    pie = theta_2 * beta_1  # pure indirect effect
    total = cde + int_ref + int_med + pie

    return {
        "cde": cde,
        "int_ref": int_ref,
        "int_med": int_med,
        "pie": pie,
        "total_effect": total,
        "outcome_coefs": {
            "intercept": float(theta[0]),
            treatment: theta_1,
            mediator: theta_2,
            "interaction": theta_3,
            **{c: float(theta[4 + i]) for i, c in enumerate(covariates)},
        },
        "mediator_coefs": {
            "intercept": beta_0,
            treatment: beta_1,
            **{c: float(beta_C[i]) for i, c in enumerate(covariates)},
        },
    }


def _bootstrap_decomposition(
    df: pd.DataFrame,
    outcome: str,
    treatment: str,
    mediator: str,
    covariates: tuple[str, ...],
    n_bootstrap: int,
    random_state: int,
) -> dict[str, list[float]]:
    """Nonparametric bootstrap by resampling subjects with replacement."""
    rng = np.random.default_rng(random_state)
    n = len(df)
    out: dict[str, list[float]] = {
        "cde": [],
        "int_ref": [],
        "int_med": [],
        "pie": [],
        "total_effect": [],
    }
    for _ in range(n_bootstrap):
        idx = rng.integers(0, n, size=n)
        boot_df = df.iloc[idx].reset_index(drop=True)
        try:
            comps = _fit_decomposition(boot_df, outcome, treatment, mediator, covariates)
        except np.linalg.LinAlgError:  # pragma: no cover - rare degenerate sample
            continue
        for k in out:
            out[k].append(comps[k])
    return out


def _design_matrix(df: pd.DataFrame) -> np.ndarray:
    """Build a design matrix with leading intercept column."""
    n = len(df)
    cols: list[np.ndarray] = [np.ones(n, dtype=np.float64)]
    for col in df.columns:
        cols.append(df[col].astype(float).to_numpy(dtype=np.float64))
    return np.column_stack(cols)


def _flatten_to_subject_table(
    panel: Panel,
    outcome: str,
    treatment: str,
    mediator: str,
    covariates: tuple[str, ...],
) -> pd.DataFrame:
    """Collapse a Panel to one row per subject for cross-sectional mediation.

    If the panel has multiple periods per unit, take the row at the
    largest period (the latest observation) — this matches the classic
    mediation-analysis setup.
    """
    df = panel.df
    needed = [outcome, treatment, mediator, *covariates]
    missing = [c for c in needed if c not in df.columns]
    if missing:
        raise ValueError(f"Panel missing column(s) {missing}. Got: {list(df.columns)}.")
    if df.index.get_level_values("unit_id").nunique() == len(df):
        return df.reset_index(level="period", drop=True)[needed]
    return (
        df.groupby(level="unit_id", group_keys=False)
        .tail(1)
        .reset_index(level="period", drop=True)[needed]
    )


# Keep scipy.stats import for potential v0.2 extensions (analytic SEs via
# delta method, normal-approximation z-tests on the four components).
_ = stats
