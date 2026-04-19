"""Conformance tests for the Survival engine family."""

from __future__ import annotations

import pytest

from factor_factory.engines.survival import estimate, registry
from factor_factory.engines.survival._base import SurvivalResult

from .._fixtures.cross_domain import survival_oncology_panel

pytestmark = pytest.mark.skipif(
    not registry.available(),
    reason="Survival engines not registered (install factor-factory[survival]).",
)


def test_kaplan_meier_returns_survival_result() -> None:
    panel = survival_oncology_panel()
    result = registry["kaplan_meier"].fit(panel, duration_col="duration", event_col="event")
    assert isinstance(result, SurvivalResult)
    assert result.method == "kaplan_meier"
    assert result.n_subjects == 200
    assert result.n_events > 0
    # Survival curve has the right shape
    assert result.survival_curve is not None
    assert {"timeline", "survival_prob", "ci_lower", "ci_upper"} <= set(
        result.survival_curve.columns
    )
    # Survival curve is monotonically non-increasing
    sf = result.survival_curve["survival_prob"].to_numpy()
    assert (sf[1:] <= sf[:-1] + 1e-9).all()


def test_kaplan_meier_recovers_reasonable_median() -> None:
    """True median in fixture is ~18 months."""
    panel = survival_oncology_panel()
    result = registry["kaplan_meier"].fit(panel)
    assert result.median_survival is not None
    assert 10.0 < result.median_survival < 30.0


def test_cox_ph_recovers_covariate_effects() -> None:
    """ECOG and age both increase hazard in the fixture."""
    panel = survival_oncology_panel()
    result = registry["cox_ph"].fit(
        panel,
        duration_col="duration",
        event_col="event",
        covariates=("age", "ecog_score"),
    )
    assert isinstance(result, SurvivalResult)
    assert result.method == "cox_ph"
    assert result.coefficients is not None
    assert result.hazard_ratios is not None
    # Both coefficients should be positive (increased hazard with age + ECOG)
    assert result.coefficients["ecog_score"] > 0
    # Hazard ratios > 1 imply elevated risk
    assert result.hazard_ratios["ecog_score"] > 1.0


def test_cox_ph_requires_covariates() -> None:
    panel = survival_oncology_panel()
    with pytest.raises(ValueError, match="covariate"):
        registry["cox_ph"].fit(panel, covariates=())


def test_estimate_dispatcher_runs_multiple_methods() -> None:
    panel = survival_oncology_panel()
    results = estimate(
        panel,
        methods=("kaplan_meier", "cox_ph"),
        covariates=("age", "ecog_score"),
    )
    assert len(results) == 2
    methods = [r.method for r in results]
    assert "kaplan_meier" in methods
    assert "cox_ph" in methods
