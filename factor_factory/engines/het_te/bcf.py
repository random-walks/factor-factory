"""Bayesian Causal Forests (BCF) — homegrown simplified port.

BCF (Hahn, Murray, Carvalho 2020, Bayesian Analysis) addresses two
TARNet/Causal-Forest weaknesses:

1. Regularization-induced confounding: classical BART/CF regularizes
   the propensity + outcome models separately, which can leak
   confounding into the treatment-effect posterior.
2. Separate prior specifications: BCF uses distinct priors for the
   prognostic function μ(x) and the treatment-effect function τ(x).

This adapter ships a **simplified linear-Gaussian port** suitable for
quick sensitivity checks. For production use, the R ``bcf`` package
remains the reference implementation — we'll swap in a proper Python
port when a mature upstream (``bcf-py`` or similar) exists.

References
----------
Hahn, P. R., Murray, J. S., & Carvalho, C. M. (2020). Bayesian
regression tree models for causal inference: Regularization,
confounding, and heterogeneous effects. *Bayesian Analysis*, 15(3),
965-1056. https://doi.org/10.1214/19-BA1195

Reference R implementation: https://cran.r-project.org/package=bcf
"""

from __future__ import annotations

from typing import Any

import numpy as np

from ...tidy.panel import Panel
from ._base import HetTeResult


class BcfEngine:
    """Bayesian Causal Forest (simplified linear-Gaussian port)."""

    name = "bcf"

    def fit(
        self,
        panel: Panel,
        *,
        outcome: str,
        treatment: str = "treatment",
        covariates: tuple[str, ...] = (),
        n_draws: int = 1000,
        random_state: int = 42,
        **_engine_specific_kwargs: Any,
    ) -> HetTeResult:
        if not covariates:
            raise ValueError("BcfEngine requires at least one covariate.")

        df = panel.df.reset_index()
        y = df[outcome].to_numpy(dtype=float)
        t = df[treatment].to_numpy(dtype=float)
        x = df[list(covariates)].to_numpy(dtype=float)

        # Simplified linear-Gaussian BCF: separate priors on μ and τ.
        # Propensity via logistic regression on x.
        # Prognostic model: μ(x) = β_μ' x
        # Treatment effect: τ(x) = β_τ' x
        # Full: y = μ(x) + t * τ(x) + ε, ε ~ N(0, σ²)
        # Prior: β_μ ~ N(0, c_μ² I), β_τ ~ N(0, c_τ² I) with c_τ << c_μ
        # (the regularization discount on τ is what differentiates BCF from
        # a plain interaction model — it shrinks heterogeneity toward zero
        # unless the data strongly supports it).

        # Fit propensity (logistic).
        from sklearn.linear_model import LogisticRegression, Ridge

        rng = np.random.default_rng(random_state)
        t_binary = (t > 0).astype(int)
        if t_binary.sum() == 0 or t_binary.sum() == len(t):
            raise ValueError("BCF needs both treated and untreated observations.")

        prop_model = LogisticRegression(max_iter=1000)
        prop_model.fit(x, t_binary)
        # propensity scores available via prop_model.predict_proba — unused
        # in this simplified port but preserved for future regularization hooks.

        # Fit μ(x) via ridge on controls; different ridge on τ(x) via
        # interaction regression on treated residuals.
        mu_model = Ridge(alpha=1.0)
        control_mask = t_binary == 0
        if control_mask.sum() < 5:
            raise ValueError("BCF needs at least 5 control observations.")
        mu_model.fit(x[control_mask], y[control_mask])
        mu_hat = mu_model.predict(x)

        # τ ridge: regress y - μ̂(x) on x with treatment as a multiplier.
        # Use heavier shrinkage (larger alpha) to reflect BCF's τ-prior.
        tau_model = Ridge(alpha=10.0)
        residual = y - mu_hat
        # Keep only treated observations for τ fit; include intercept.
        treated_mask = t_binary == 1
        tau_model.fit(x[treated_mask], residual[treated_mask])
        tau_hat = tau_model.predict(x)

        # Simulate posterior draws of τ(x) via bootstrap over the fitted residuals.
        tau_draws = np.zeros((n_draws, len(y)))
        for d in range(n_draws):
            idx = rng.choice(len(y), size=len(y), replace=True)
            m = Ridge(alpha=10.0).fit(x[idx], residual[idx])
            tau_draws[d] = m.predict(x)

        ate = float(np.mean(tau_hat))
        ate_se = float(np.std(tau_draws.mean(axis=1), ddof=1))

        return HetTeResult(
            method=self.name,
            ate=ate,
            ate_std_error=ate_se,
            cate_predictions=tau_hat,
            cate_std_errors=np.std(tau_draws, axis=0, ddof=1),
            treatment_effect_heterogeneity_pvalue=None,
            feature_importances={
                c: float(v) for c, v in zip(covariates, np.abs(tau_model.coef_), strict=True)
            },
            n_units=int(len(y)),
            diagnostics={
                "n_draws": n_draws,
                "mu_ridge_alpha": 1.0,
                "tau_ridge_alpha": 10.0,
                "method": "simplified linear-Gaussian BCF port",
                "upstream_ref": "R bcf package",
            },
        )
