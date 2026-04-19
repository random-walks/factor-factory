"""SDID placebo-inference option (Batch 5, v1.2.0)."""

from __future__ import annotations

import pytest

from factor_factory.engines.sdid import estimate
from factor_factory.tests._fixtures.cross_domain import sdid_block_treatment_panel


def test_sdid_placebo_inference_runs() -> None:
    panel = sdid_block_treatment_panel()
    result = estimate(panel, inference="placebo", n_placebo=50, placebo_seed=0)[0]
    assert result.diagnostics is not None
    assert result.diagnostics["inference"] == "placebo"
    # Placebo SE should be positive and finite.
    assert result.se > 0
    assert result.se < 100  # sanity


def test_sdid_jackknife_still_default() -> None:
    panel = sdid_block_treatment_panel()
    result = estimate(panel)[0]
    assert result.diagnostics is not None
    assert result.diagnostics["inference"] == "jackknife"


def test_sdid_invalid_inference_raises() -> None:
    panel = sdid_block_treatment_panel()
    with pytest.raises(ValueError, match="jackknife.*placebo"):
        estimate(panel, inference="bootstrap")


def test_sdid_placebo_vs_jackknife_recover_similar_att() -> None:
    # ATT point estimate is identical; only SE computation differs.
    panel = sdid_block_treatment_panel()
    jk = estimate(panel, inference="jackknife")[0]
    pl = estimate(panel, inference="placebo", n_placebo=100, placebo_seed=0)[0]
    assert jk.att == pytest.approx(pl.att, rel=1e-6)
