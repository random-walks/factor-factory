"""Augmented SCM (Ben-Michael, Feller, Rothstein 2021) — homegrown adapter.

Classic SCM restricts donor weights to the simplex (non-negative,
sum to 1). Under poor pre-period fit this can lead to large bias.
Augmented SCM (ASCM) adds a ridge-regression outcome model on top of
the SCM fit: the post-period counterfactual is the SCM prediction plus
an outcome-model correction for the pre-period fit residuals.

References
----------
Ben-Michael, E., Feller, A., & Rothstein, J. (2021). The augmented
synthetic control method. *JASA*, 116(536), 1789-1803.
https://doi.org/10.1080/01621459.2021.1929245

Reference R implementation: ``augsynth`` (Berkeley team,
https://github.com/ebenmichael/augsynth). This is a homegrown Python
adapter using ridge regression on pre-period residuals.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from ...tidy.panel import Panel
from ._base import ScmResult


class AugmentedScmEngine:
    """Augmented SCM (Ben-Michael et al. 2021)."""

    name = "augmented"

    def fit(
        self,
        panel: Panel,
        *,
        outcome: str,
        treatment: str = "treatment",
        ridge_lambda: float = 1.0,
        **_engine_specific_kwargs: Any,
    ) -> ScmResult:
        if not panel.treatment_events:
            raise ValueError("AugmentedScmEngine requires a treatment event.")

        import pandas as pd

        event = panel.treatment_events[0]
        treated_unit = list(event.treated_units)[0]
        treatment_period = event.treatment_date or event.period_value
        if panel.period_kind == "timestamp" and treatment_period is not None:
            treatment_period = pd.Timestamp(treatment_period)

        df = panel.df.reset_index()
        periods = sorted(df["period"].unique())
        pre_periods = [p for p in periods if p < treatment_period]
        post_periods = [p for p in periods if p >= treatment_period]
        wide = df.pivot_table(index="period", columns="unit_id", values=outcome)
        wide = wide.sort_index()
        # Align to period order: rows periods × cols units.

        all_units = list(wide.columns)
        controls = [u for u in all_units if u != treated_unit]

        Y_pre_t = wide.loc[pre_periods, treated_unit].to_numpy(dtype=float)
        Y_pre_c = wide.loc[pre_periods, controls].to_numpy(dtype=float)  # (n_pre, n_co)
        Y_post_t = wide.loc[post_periods, treated_unit].to_numpy(dtype=float)
        Y_post_c = wide.loc[post_periods, controls].to_numpy(dtype=float)

        # Step 1: classic SCM weights (simplex-constrained least squares).
        # Simplified via scipy SLSQP — same approach as engines.sdid.
        from scipy.optimize import minimize

        def loss(w: np.ndarray) -> float:
            return float(np.mean((Y_pre_t - Y_pre_c @ w) ** 2))

        n_co = len(controls)
        w0 = np.full(n_co, 1.0 / n_co)
        cons = [{"type": "eq", "fun": lambda w: np.sum(w) - 1.0}]
        bounds = [(0.0, 1.0)] * n_co
        res = minimize(loss, w0, method="SLSQP", bounds=bounds, constraints=cons)
        w_scm = res.x

        # Step 2: Ridge outcome-model correction.
        # Fit Y_pre,i = α + x_i · β + ε on control units with x_i a vector of
        # predictor values (here simply the mean pre-period outcome per unit).
        # Compute SCM residuals in the pre-period, then extrapolate via ridge.
        scm_pre = Y_pre_c @ w_scm
        residual_pre = Y_pre_t - scm_pre
        # Simple ridge on a constant + unit mean-pre feature.
        x_ctrl = np.column_stack([np.ones(len(pre_periods)), np.mean(Y_pre_c, axis=1)])
        # Ridge closed-form: β = (X'X + λI)^-1 X'y
        XtX = x_ctrl.T @ x_ctrl + ridge_lambda * np.eye(x_ctrl.shape[1])
        beta_ridge = np.linalg.solve(XtX, x_ctrl.T @ residual_pre)

        x_post = np.column_stack([np.ones(len(post_periods)), np.mean(Y_post_c, axis=1)])
        ridge_correction = x_post @ beta_ridge

        # Augmented counterfactual: SCM prediction + ridge correction.
        Y_post_counterfactual = Y_post_c @ w_scm + ridge_correction
        gap_post = Y_post_t - Y_post_counterfactual

        scm_post = Y_post_c @ w_scm  # for RMSPE diagnostic on plain SCM
        pre_rmspe = float(np.sqrt(np.mean((Y_pre_t - scm_pre) ** 2)))
        post_rmspe = float(np.sqrt(np.mean((Y_post_t - scm_post) ** 2)))
        att = float(np.mean(gap_post))

        return ScmResult(
            method=self.name,
            att=att,
            std_error=None,
            pre_period_rmspe=pre_rmspe,
            post_period_rmspe=post_rmspe,
            donor_weights={c: float(w) for c, w in zip(controls, w_scm, strict=True)},
            predictor_weights={
                "ridge_intercept": float(beta_ridge[0]),
                "ridge_pre_mean": float(beta_ridge[1]),
            },
            placebo_pvalue=None,
            n_donor=n_co,
            n_pre=len(pre_periods),
            n_post=len(post_periods),
            diagnostics={
                "treated_unit": str(treated_unit),
                "ridge_lambda": ridge_lambda,
                "method": "ASCM (Ben-Michael et al. 2021)",
            },
        )
