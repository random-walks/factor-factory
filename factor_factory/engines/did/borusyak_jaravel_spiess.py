"""Borusyak-Jaravel-Spiess (BJS) imputation-based DiD adapter.

BJS (2024) fits a fixed-effects regression on **untreated cells only**,
imputes counterfactual outcomes for treated cells, and estimates the
ATT as the mean gap. Robust to heterogeneous treatment effects and
arbitrary rollout patterns; estimator is asymptotically efficient
under homoskedasticity.

Relationship to TWFE
--------------------
TWFE pools treated and untreated cells in the fixed-effects regression,
which introduces the Goodman-Bacon (2021) negative-weight problem
under staggered rollout. BJS sidesteps this by fitting the FE model
on untreated data only, then using the estimated unit- and time-fixed-
effects to impute Ŷ(0) for treated cells. The ATT is the simple mean
of Y - Ŷ(0) over treated cells.

References
----------
Borusyak, K., Jaravel, X., & Spiess, J. (2024). Revisiting event-study
designs: Robust and efficient estimation. *Review of Economic Studies*.
https://doi.org/10.1093/restud/rdae007

Reference Stata implementation: ``did_imputation`` package. No
canonical Python port — this is a homegrown adapter using scipy's
least-squares for the untreated-cells FE regression.
"""

from __future__ import annotations

from math import erf, sqrt
from typing import Any

import numpy as np
import pandas as pd

from ...tidy.panel import Panel
from ._base import DidResult


class BorusyakJaravelSpiessEngine:
    """BJS 2024 imputation-based DiD estimator."""

    name = "bjs"

    def fit(
        self,
        panel: Panel,
        *,
        outcome: str,
        treatment: str = "treatment",
        cluster: str | None = None,
        **_engine_specific_kwargs: Any,
    ) -> DidResult:
        df = panel.df
        if treatment not in df.columns:
            raise ValueError(
                f"BJS requires a {treatment!r} column on the panel; "
                f"build the Panel with treatment_events so the column is attached."
            )
        if outcome not in df.columns:
            raise ValueError(f"Outcome column {outcome!r} not found on panel.")

        reset = df.reset_index()
        y = reset[outcome].to_numpy(dtype=float)
        w = reset[treatment].to_numpy(dtype=float) > 0  # binary treated-cell mask
        units = reset["unit_id"].to_numpy()
        periods = reset["period"].to_numpy()

        if not w.any():
            raise ValueError("BJS requires at least one treated cell.")
        if w.all():
            raise ValueError("BJS requires at least one untreated cell to fit the FE model.")

        # Fit unit + time fixed-effects on untreated cells only.
        #   Y_it = α_i + δ_t + ε_it   for (i,t) with W_it = 0
        # Build design matrix with dummy columns per unit and per period.
        y_u = y[~w]
        units_u = units[~w]
        periods_u = periods[~w]

        unit_codes, unit_index = pd.factorize(units_u)
        period_codes, period_index = pd.factorize(periods_u)
        n = len(y_u)
        n_units = len(unit_index)
        n_periods = len(period_index)

        # Design: intercept + (n_units - 1) unit dummies + (n_periods - 1) period dummies
        # (drop first unit and first period for identification).
        X = np.zeros((n, 1 + (n_units - 1) + (n_periods - 1)), dtype=float)
        X[:, 0] = 1.0
        for k in range(1, n_units):
            X[:, k] = (unit_codes == k).astype(float)
        for k in range(1, n_periods):
            X[:, n_units + (k - 1)] = (period_codes == k).astype(float)

        # Least-squares: β = (X'X)^-1 X'y
        # Use lstsq for numerical stability; we don't need SEs of the FEs.
        beta, *_ = np.linalg.lstsq(X, y_u, rcond=None)
        const = beta[0]
        unit_fe = np.concatenate(([0.0], beta[1:n_units]))  # first unit = 0 reference
        period_fe = np.concatenate(([0.0], beta[n_units:]))  # first period = 0 reference

        # Impute Ŷ(0) for treated cells by looking up their unit_fe + period_fe.
        # Some treated units may never have appeared in the untreated data (entirely
        # treated-over-all-periods). Flag them and exclude from the ATT average.
        unit_to_fe = dict(zip(unit_index, unit_fe, strict=True))
        period_to_fe = dict(zip(period_index, period_fe, strict=True))

        treated_mask = w
        y_t = y[treated_mask]
        units_t = units[treated_mask]
        periods_t = periods[treated_mask]
        y_hat = np.full(len(y_t), np.nan)
        for idx in range(len(y_t)):
            u_fe = unit_to_fe.get(units_t[idx])
            p_fe = period_to_fe.get(periods_t[idx])
            if u_fe is None or p_fe is None:
                continue  # can't impute; leaves NaN
            y_hat[idx] = const + u_fe + p_fe

        gaps = y_t - y_hat
        finite = np.isfinite(gaps)
        n_dropped = int((~finite).sum())
        if not finite.any():
            raise ValueError(
                "BJS could not impute counterfactuals for any treated cell "
                "(no overlapping unit/period FEs in the untreated panel). "
                "Check treatment rollout — are there any never-treated cells "
                "for the treated units' periods?"
            )

        att = float(np.mean(gaps[finite]))

        # Heteroskedasticity-robust SE over treated cells (simple sample std / sqrt(n_t)).
        # For a full BJS SE, bootstrap or analytical sandwich is needed — deferred.
        n_t = int(finite.sum())
        se = float(np.std(gaps[finite], ddof=1) / np.sqrt(n_t)) if n_t > 1 else float("nan")

        ci_lo = att - 1.96 * se if np.isfinite(se) else float("nan")
        ci_hi = att + 1.96 * se if np.isfinite(se) else float("nan")
        p_value = float(2.0 * (1.0 - _phi(abs(att / se)))) if (se > 0) else float("nan")

        return DidResult(
            method=self.name,
            att=att,
            se=se,
            ci_95=(ci_lo, ci_hi),
            p_value=p_value,
            n=int(len(df)),
            diagnostics={
                "n_treated_cells": n_t,
                "n_untreated_cells": int(len(y_u)),
                "n_treated_cells_dropped": n_dropped,
                "n_units": n_units,
                "n_periods": n_periods,
                "method": "imputation (BJS 2024)",
                "se_method": "treated-cell sample std / sqrt(n_t) — "
                "full analytical sandwich SE deferred",
            },
        )


def _phi(z: float) -> float:
    """Standard-normal CDF via erf."""
    return 0.5 * (1.0 + erf(z / sqrt(2.0)))
