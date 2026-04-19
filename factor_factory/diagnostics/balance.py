"""Standardized mean differences (SMD) for treated/control balance checks."""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..tidy.panel import Panel


def standardized_mean_differences(
    panel: Panel,
    *,
    treated_col: str = "treated_unit",
    covariates: tuple[str, ...],
    pre_treatment_only: bool = True,
) -> pd.DataFrame:
    """Compute SMDs between treated and control units on each covariate.

    Returns a DataFrame with one row per covariate. The ``imbalance_flag``
    column flags ``"*"`` for ``|SMD| > 0.1`` and ``"***"`` for
    ``|SMD| > 0.5`` — the conventional Stuart 2010 cutoffs.
    """
    if not covariates:
        raise ValueError("At least one covariate must be supplied.")
    df = panel.df
    if treated_col not in df.columns:
        raise ValueError(
            f"Panel missing treated_col '{treated_col}'. Got columns: {list(df.columns)}."
        )
    missing = [c for c in covariates if c not in df.columns]
    if missing:
        raise ValueError(f"Panel missing covariate(s) {missing}. Got columns: {list(df.columns)}.")

    if pre_treatment_only and "post" in df.columns:
        df = df[df["post"] == 0]
        if df.empty:
            raise ValueError(
                "pre_treatment_only=True but no pre-treatment rows on the panel "
                "(all rows have post=1)."
            )

    treated_mask = df[treated_col].astype(bool)
    control_mask = ~treated_mask
    if not treated_mask.any():
        raise ValueError(f"No treated rows: '{treated_col}' is all 0.")
    if not control_mask.any():
        raise ValueError(f"No control rows: '{treated_col}' is all 1.")

    rows: list[dict[str, object]] = []
    for cov in covariates:
        treated_vals = df.loc[treated_mask, cov].astype(float)
        control_vals = df.loc[control_mask, cov].astype(float)

        treated_mean = float(treated_vals.mean())
        control_mean = float(control_vals.mean())
        diff = treated_mean - control_mean

        # Pooled SD per Rubin 2001 / Stuart 2010
        treated_var = float(treated_vals.var(ddof=1)) if len(treated_vals) > 1 else 0.0
        control_var = float(control_vals.var(ddof=1)) if len(control_vals) > 1 else 0.0
        pooled_sd = float(np.sqrt((treated_var + control_var) / 2.0))

        if pooled_sd == 0:  # noqa: SIM108 — explicit branches are clearer here
            smd = 0.0 if diff == 0 else float("inf")
        else:
            smd = diff / pooled_sd

        if not np.isfinite(smd) or abs(smd) > 0.5:
            flag = "***"
        elif abs(smd) > 0.1:
            flag = "*"
        else:
            flag = ""

        rows.append(
            {
                "covariate": cov,
                "treated_mean": treated_mean,
                "control_mean": control_mean,
                "diff": diff,
                "pooled_sd": pooled_sd,
                "smd": smd,
                "imbalance_flag": flag,
            }
        )

    return pd.DataFrame(
        rows,
        columns=[
            "covariate",
            "treated_mean",
            "control_mean",
            "diff",
            "pooled_sd",
            "smd",
            "imbalance_flag",
        ],
    )
