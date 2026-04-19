"""Conformance tests for the Synthetic DiD engine (Arkhangelsky 2021)."""

from __future__ import annotations

import pytest

from factor_factory.engines.did import estimate as did_estimate
from factor_factory.engines.sdid import estimate, registry
from factor_factory.engines.sdid._base import SdidResult

from .._fixtures.cross_domain import sdid_block_treatment_panel


def test_sdid_returns_result_dataclass() -> None:
    panel = sdid_block_treatment_panel()
    result = registry["sdid"].fit(panel, outcome=panel.outcome_col)
    assert isinstance(result, SdidResult)
    assert result.method == "sdid"
    assert result.n_treated == 5
    assert result.n_control == 45
    assert result.n_pre == 20
    assert result.n_post == 10
    assert result.unit_weights is not None
    assert len(result.unit_weights) == result.n_control


def test_sdid_unit_weights_form_a_simplex() -> None:
    panel = sdid_block_treatment_panel()
    result = registry["sdid"].fit(panel, outcome=panel.outcome_col)
    assert result.unit_weights is not None
    weights = list(result.unit_weights.values())
    assert all(w >= -1e-9 for w in weights), "unit weights must be non-negative"
    assert abs(sum(weights) - 1.0) < 1e-6, "unit weights must sum to 1"


def test_sdid_time_weights_form_a_simplex() -> None:
    panel = sdid_block_treatment_panel()
    result = registry["sdid"].fit(panel, outcome=panel.outcome_col)
    assert result.time_weights is not None
    weights = list(result.time_weights.values())
    assert all(w >= -1e-9 for w in weights)
    assert abs(sum(weights) - 1.0) < 1e-6


def test_sdid_recovers_true_att() -> None:
    """Fixture's true ATT is 4.0; SDID should recover it within ~1.5."""
    panel = sdid_block_treatment_panel()
    result = registry["sdid"].fit(panel, outcome=panel.outcome_col)
    assert abs(result.att - 4.0) < 1.5


def test_sdid_jackknife_se_is_positive() -> None:
    panel = sdid_block_treatment_panel()
    result = registry["sdid"].fit(panel, outcome=panel.outcome_col)
    assert result.se > 0.0
    assert result.diagnostics is not None
    assert result.diagnostics["inference"] == "jackknife"


def test_sdid_ci_brackets_estimate() -> None:
    panel = sdid_block_treatment_panel()
    result = registry["sdid"].fit(panel, outcome=panel.outcome_col)
    lo, hi = result.ci_95
    assert lo <= result.att <= hi


def test_sdid_requires_treatment_events() -> None:
    panel = sdid_block_treatment_panel()
    bad_metadata = panel.metadata.model_copy(update={"treatment_events": ()})
    from factor_factory.tidy import Panel

    bad_panel = Panel(panel.df.copy(), bad_metadata)
    with pytest.raises(ValueError, match="treatment_events"):
        registry["sdid"].fit(bad_panel, outcome=panel.outcome_col)


def test_sdid_estimate_dispatcher() -> None:
    panel = sdid_block_treatment_panel()
    results = estimate(panel, methods=("sdid",))
    assert len(list(results)) == 1


def test_sdid_vs_twfe_on_block_treatment() -> None:
    """Sanity check: SDID and TWFE should both recover the true ATT on this
    fixture (TWFE works fine for block treatment with parallel trends; SDID
    is the more robust choice when trends diverge). They should agree to
    within a few SEs."""
    panel = sdid_block_treatment_panel()
    twfe = did_estimate(panel, methods=("twfe",))
    sdid = registry["sdid"].fit(panel, outcome=panel.outcome_col)
    twfe_att = twfe[0].att
    sdid_att = sdid.att
    # Same order of magnitude on the true 4.0 effect
    assert abs(twfe_att - sdid_att) < 2.0
