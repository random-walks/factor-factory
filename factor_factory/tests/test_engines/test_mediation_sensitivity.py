"""Mediation sensitivity analysis + outcome/mediator family fields (Batch 5, v1.2.0)."""

from __future__ import annotations

import numpy as np

from factor_factory.engines.mediation import MediationResult


def _mk_result(**overrides) -> MediationResult:
    base = {
        "method": "four_way",
        "n_subjects": 1000,
        "treatment": "A",
        "mediator": "M",
        "outcome": "Y",
        "total_effect": 4.1,
        "cde": 2.0,
        "int_ref": 0.15,
        "int_med": 0.45,
        "pie": 1.5,
        "decomposition_residual": 0.0,
        "diagnostics": {
            "outcome_residual_sd": 1.0,
            "mediator_residual_sd": 1.0,
        },
    }
    base.update(overrides)
    return MediationResult(**base)


def test_sensitivity_linear_linear_shape() -> None:
    result = _mk_result()
    df = result.sensitivity(rho_range=(-0.3, 0.3), n_points=7)
    assert len(df) == 7
    assert {
        "rho",
        "cde_adjusted",
        "int_ref_adjusted",
        "int_med_adjusted",
        "pie_adjusted",
        "total_effect_adjusted",
    } <= set(df.columns)


def test_sensitivity_at_rho_zero_returns_unchanged() -> None:
    result = _mk_result()
    df = result.sensitivity(rho_range=(0.0, 0.0), n_points=1)
    row = df.iloc[0]
    assert row["pie_adjusted"] == result.pie
    assert row["cde_adjusted"] == result.cde


def test_sensitivity_pie_shifts_with_rho() -> None:
    result = _mk_result()
    df = result.sensitivity(rho_range=(-0.5, 0.5), n_points=11)
    # PIE adjusted must be monotonically decreasing in rho (under the
    # linear-linear bias formula bias = rho * sigma_m * sigma_y).
    pies = df["pie_adjusted"].to_numpy()
    diffs = np.diff(pies)
    assert np.all(diffs <= 0), "PIE adjustment should decrease as rho increases"


def test_sensitivity_logistic_returns_nan() -> None:
    result = _mk_result(outcome_family="logistic")
    df = result.sensitivity(rho_range=(-0.2, 0.2), n_points=5)
    # Logistic case not yet implemented → NaN.
    assert df["pie_adjusted"].isna().all()


def test_outcome_mediator_family_default_linear() -> None:
    result = _mk_result()
    assert result.outcome_family == "linear"
    assert result.mediator_family == "linear"
