"""Tests for the four required-for-v0.1 diagnostics."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")  # headless

import numpy as np
import pandas as pd
import pytest

from factor_factory.diagnostics import (
    multi_index_assertions,
    parallel_trends_plot,
    residual_diagnostics,
    standardized_mean_differences,
)

from ._fixtures.synthetic_panels import (
    small_treatment_effect_panel,
    unbalanced_panel,
)

# ─── multi_index_assertions ────────────────────────────────────────────────


def test_multi_index_assertions_passes_on_valid_panel() -> None:
    panel = small_treatment_effect_panel()
    multi_index_assertions(panel)  # should not raise


def test_multi_index_assertions_raises_on_unbalanced() -> None:
    bad_df = unbalanced_panel()
    panel = small_treatment_effect_panel()
    panel.df = bad_df  # bypass __init__ validation, simulate post-mutation drift
    with pytest.raises(AssertionError, match="unbalanced"):
        multi_index_assertions(panel)


# ─── standardized_mean_differences ─────────────────────────────────────────


def test_smd_on_balanced_panel() -> None:
    panel = small_treatment_effect_panel()
    # Add a covariate that is well-balanced by construction
    df = panel.df.copy()
    rng = np.random.default_rng(7)
    df["covariate_balanced"] = rng.normal(0, 1, len(df))
    panel.df = df

    result = standardized_mean_differences(
        panel, covariates=("covariate_balanced",), pre_treatment_only=True
    )
    assert list(result.columns) == [
        "covariate",
        "treated_mean",
        "control_mean",
        "diff",
        "pooled_sd",
        "smd",
        "imbalance_flag",
    ]
    assert len(result) == 1
    assert abs(result.loc[0, "smd"]) < 0.5


def test_smd_flags_imbalance() -> None:
    panel = small_treatment_effect_panel()
    df = panel.df.copy()
    treated_mask = df["treated_unit"].astype(bool)
    df["covariate_imbalanced"] = np.where(treated_mask, 5.0, 0.0)
    panel.df = df

    result = standardized_mean_differences(panel, covariates=("covariate_imbalanced",))
    assert result.loc[0, "imbalance_flag"] == "***"


def test_smd_raises_on_missing_covariate() -> None:
    panel = small_treatment_effect_panel()
    with pytest.raises(ValueError, match="covariate"):
        standardized_mean_differences(panel, covariates=("does_not_exist",))


# ─── parallel_trends_plot ──────────────────────────────────────────────────


def test_parallel_trends_returns_figure() -> None:
    panel = small_treatment_effect_panel()
    fig = parallel_trends_plot(panel)
    assert fig is not None
    assert len(fig.axes) == 1


def test_parallel_trends_uses_treatment_event_date() -> None:
    panel = small_treatment_effect_panel()
    fig = parallel_trends_plot(panel)
    ax = fig.axes[0]
    # Must contain a vertical line for treatment date
    vlines = [c for c in ax.lines if c.get_linestyle() == "--"]
    assert len(vlines) >= 1


# ─── residual_diagnostics ──────────────────────────────────────────────────


def test_residual_diagnostics_normal_residuals() -> None:
    rng = np.random.default_rng(42)
    residuals = pd.Series(rng.normal(0, 1, 1000))
    out = residual_diagnostics(residuals)
    assert out["n"] == 1000
    assert out["normality_passes"] is True
    assert out["breusch_pagan_p"] is None  # no fitted_values supplied


def test_residual_diagnostics_with_fitted() -> None:
    rng = np.random.default_rng(42)
    n = 500
    fitted = pd.Series(rng.uniform(0, 10, n))
    residuals = pd.Series(rng.normal(0, 1, n))
    out = residual_diagnostics(residuals, fitted_values=fitted)
    assert out["breusch_pagan_p"] is not None
    assert 0.0 <= out["breusch_pagan_p"] <= 1.0


def test_residual_diagnostics_flags_non_normal() -> None:
    rng = np.random.default_rng(42)
    # heavy-tailed distribution
    residuals = pd.Series(rng.standard_cauchy(2000))
    out = residual_diagnostics(residuals)
    assert out["normality_passes"] is False


def test_residual_diagnostics_raises_on_empty() -> None:
    with pytest.raises(ValueError, match="empty"):
        residual_diagnostics(pd.Series([], dtype=float))
