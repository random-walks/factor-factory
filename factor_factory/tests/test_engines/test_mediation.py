"""Conformance tests for the four-way mediation engine (VanderWeele 2014)."""

from __future__ import annotations

import pytest

from factor_factory.engines.mediation import estimate, registry
from factor_factory.engines.mediation._base import MediationResult

from .._fixtures.cross_domain import mediation_panel


def test_returns_mediation_result_dataclass() -> None:
    panel = mediation_panel()
    result = registry["four_way"].fit(
        panel,
        outcome="outcome",
        treatment="treatment",
        mediator="mediator",
        covariates=("covariate",),
        n_bootstrap=0,
    )
    assert isinstance(result, MediationResult)
    assert result.method == "four_way"
    assert result.n_subjects == 1000
    assert result.outcome == "outcome"
    assert result.treatment == "treatment"
    assert result.mediator == "mediator"


def test_decomposition_components_sum_to_total() -> None:
    """CDE + INTref + INTmed + PIE must equal Total Effect by construction."""
    panel = mediation_panel()
    result = registry["four_way"].fit(
        panel,
        outcome="outcome",
        treatment="treatment",
        mediator="mediator",
        covariates=("covariate",),
        n_bootstrap=0,
    )
    assert abs(result.decomposition_residual) < 1e-9


def test_recovers_known_components() -> None:
    """Fixture has true CDE=2.0, PIE=1.5, INTmed=0.45, INTref≈0.15."""
    panel = mediation_panel()
    result = registry["four_way"].fit(
        panel,
        outcome="outcome",
        treatment="treatment",
        mediator="mediator",
        covariates=("covariate",),
        n_bootstrap=0,
    )
    assert abs(result.cde - 2.0) < 0.2, f"CDE: expected ≈2.0, got {result.cde}"
    assert abs(result.pie - 1.5) < 0.2, f"PIE: expected ≈1.5, got {result.pie}"
    assert abs(result.int_med - 0.45) < 0.2, f"INTmed: expected ≈0.45, got {result.int_med}"
    assert abs(result.int_ref - 0.15) < 0.2, f"INTref: expected ≈0.15, got {result.int_ref}"


def test_proportion_mediated_in_sensible_range() -> None:
    panel = mediation_panel()
    result = registry["four_way"].fit(
        panel,
        outcome="outcome",
        treatment="treatment",
        mediator="mediator",
        covariates=("covariate",),
        n_bootstrap=0,
    )
    assert result.proportion_mediated is not None
    assert 0.3 < result.proportion_mediated < 0.7  # PIE+INTmed ≈ 1.95 / TE ≈ 4.10


def test_bootstrap_provides_ses_and_cis() -> None:
    panel = mediation_panel()
    result = registry["four_way"].fit(
        panel,
        outcome="outcome",
        treatment="treatment",
        mediator="mediator",
        covariates=("covariate",),
        n_bootstrap=200,
    )
    assert result.cde_se is not None and result.cde_se > 0
    assert result.pie_se is not None and result.pie_se > 0
    assert result.confidence_intervals is not None
    assert "cde" in result.confidence_intervals
    lo, hi = result.confidence_intervals["cde"]
    assert lo <= result.cde <= hi


def test_rejects_missing_columns() -> None:
    panel = mediation_panel()
    with pytest.raises(ValueError, match="missing column"):
        registry["four_way"].fit(
            panel,
            outcome="does_not_exist",
            treatment="treatment",
            mediator="mediator",
            n_bootstrap=0,
        )


def test_estimate_dispatcher() -> None:
    panel = mediation_panel()
    results = estimate(
        panel,
        outcome="outcome",
        treatment="treatment",
        mediator="mediator",
        covariates=("covariate",),
        n_bootstrap=0,
    )
    assert len(list(results)) == 1


def test_no_covariates_works() -> None:
    """Mediation should still run when no covariates are supplied."""
    panel = mediation_panel()
    result = registry["four_way"].fit(
        panel,
        outcome="outcome",
        treatment="treatment",
        mediator="mediator",
        covariates=(),
        n_bootstrap=0,
    )
    # Without covariates, the decomposition still works (covariate's
    # contribution is small in our fixture).
    assert abs(result.decomposition_residual) < 1e-9
