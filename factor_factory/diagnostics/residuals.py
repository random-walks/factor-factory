"""Residual normality + heteroskedasticity diagnostics."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

_RNG_SEED = 20260419  # fixed seed so Shapiro sub-sampling is reproducible


def residual_diagnostics(
    residuals: pd.Series,
    *,
    fitted_values: pd.Series | None = None,
    sample_size_for_shapiro: int = 5000,
) -> dict[str, Any]:
    """Run the canonical normality + heteroskedasticity test set.

    Returns a JSON-serializable dict with normality (Jarque-Bera,
    Shapiro-Wilk) and, if ``fitted_values`` is supplied, a manual
    Breusch-Pagan test for heteroskedasticity (regression of squared
    residuals on fitted values).
    """
    residuals = pd.Series(residuals).dropna().astype(float)
    if residuals.empty:
        raise ValueError("residual_diagnostics received an empty residuals series.")

    n = int(residuals.size)
    mean = float(residuals.mean())
    std = float(residuals.std(ddof=1)) if n > 1 else 0.0

    jb_stat, jb_p = stats.jarque_bera(residuals.to_numpy())

    sample = residuals
    if n > sample_size_for_shapiro:
        rng = np.random.default_rng(_RNG_SEED)
        idx = rng.choice(n, size=sample_size_for_shapiro, replace=False)
        sample = residuals.iloc[idx]
    sw_stat, sw_p = stats.shapiro(sample.to_numpy())

    bp_stat: float | None = None
    bp_p: float | None = None
    homo_passes: bool | None = None
    if fitted_values is not None:
        fitted = pd.Series(fitted_values).astype(float).reindex(residuals.index).dropna()
        # align — Shapiro can't help here; we just need both series same length
        common = residuals.index.intersection(fitted.index)
        if len(common) < 5:
            raise ValueError(
                "residual_diagnostics: fitted_values has fewer than 5 overlapping "
                "rows with residuals; can't run Breusch-Pagan."
            )
        e = residuals.loc[common].to_numpy()
        f = fitted.loc[common].to_numpy()
        bp_stat, bp_p = _breusch_pagan_simple(e, f)
        homo_passes = bp_p > 0.05

    return {
        "n": n,
        "mean": mean,
        "std": std,
        "jarque_bera_stat": float(jb_stat),
        "jarque_bera_p": float(jb_p),
        "shapiro_wilk_stat": float(sw_stat),
        "shapiro_wilk_p": float(sw_p),
        "breusch_pagan_stat": bp_stat,
        "breusch_pagan_p": bp_p,
        "normality_passes": bool(jb_p > 0.05),
        "homoskedasticity_passes": homo_passes,
    }


def _breusch_pagan_simple(residuals: np.ndarray, fitted: np.ndarray) -> tuple[float, float]:
    """Simple Breusch-Pagan against fitted values.

    LM = n * R^2 from regressing squared residuals on fitted values
    (constant + fitted), distributed asymptotically as chi-square(1).
    """
    e2 = residuals**2
    if np.allclose(e2.var(ddof=0), 0.0):
        return 0.0, 1.0
    x = np.column_stack([np.ones_like(fitted), fitted])
    coef, *_ = np.linalg.lstsq(x, e2, rcond=None)
    pred = x @ coef
    ss_res = float(((e2 - pred) ** 2).sum())
    ss_tot = float(((e2 - e2.mean()) ** 2).sum())
    if ss_tot == 0:
        return 0.0, 1.0
    r_squared = 1.0 - ss_res / ss_tot
    n = int(residuals.size)
    lm = n * r_squared
    p_value = float(stats.chi2.sf(lm, df=1))
    return float(lm), p_value
