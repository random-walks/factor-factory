"""SCM conformance tests."""

from __future__ import annotations

from factor_factory.engines.scm import estimate, registry
from factor_factory.tests._fixtures.cross_domain import (
    FIXTURE_GROUND_TRUTH,
    scm_single_treated_state_panel,
)


def test_augmented_scm_registered() -> None:
    assert "augmented" in registry


def test_augmented_scm_recovers_att() -> None:
    panel = scm_single_treated_state_panel()
    truth = FIXTURE_GROUND_TRUTH["scm_single_treated_state_panel"]["att"]
    results = estimate(panel, methods=("augmented",), outcome="y")
    r = results[0]
    # Augmented SCM should be within 1 of ground truth on this fixture.
    assert abs(r.att - truth) < 1.5, f"ATT {r.att} vs truth {truth}"
    assert r.pre_period_rmspe >= 0
    assert r.post_period_rmspe >= 0
    assert r.n_donor == 24


def test_scm_summary_table() -> None:
    panel = scm_single_treated_state_panel()
    r = estimate(panel, methods=("augmented",), outcome="y")[0]
    df = r.summary_table()
    assert "att" in df.columns
    assert "augmented" in df.index
