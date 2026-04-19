"""Stratified Cox PH (Batch 6, v1.3.0)."""

from __future__ import annotations

import pytest

from factor_factory.engines.survival import estimate
from factor_factory.tests._fixtures.cross_domain import survival_oncology_panel

pytest.importorskip("lifelines")


def test_stratified_cox_runs() -> None:
    panel = survival_oncology_panel()
    # survival_oncology_panel has `age` (continuous) and `ecog` covariates.
    # Use ecog as a stratum (categorical), age as a covariate.
    results = estimate(
        panel,
        methods=("cox_ph",),
        covariates=("age",),
        strata="ecog_score",
    )
    r = results[0]
    assert r.method == "cox_ph"
    # Stratified Cox fits coefficients for non-strata covariates.
    assert r.coefficients is not None
    assert "age" in r.coefficients
    # ecog should NOT appear in coefficients (it's a stratum, not a covariate).
    assert "ecog_score" not in r.coefficients


def test_unstratified_cox_still_works() -> None:
    panel = survival_oncology_panel()
    results = estimate(panel, methods=("cox_ph",), covariates=("age", "ecog_score"))
    r = results[0]
    assert r.coefficients is not None
    assert {"age", "ecog_score"} <= set(r.coefficients)
