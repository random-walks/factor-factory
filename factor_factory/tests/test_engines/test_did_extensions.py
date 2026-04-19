"""Sun-Abraham + BJS DiD adapters (Batch 6, v1.3.0)."""

from __future__ import annotations

import pytest

from factor_factory.engines.did import estimate
from factor_factory.tests._fixtures.cross_domain import staggered_did_panel


def test_bjs_registered() -> None:
    from factor_factory.engines.did import registry

    assert "bjs" in registry


def test_bjs_fits_staggered_panel() -> None:
    panel = staggered_did_panel()
    # Attach aggregate treatment columns for BJS (it expects `treatment`).
    panel_with_agg = panel.attach_treatment_columns(replace=True)
    results = estimate(panel_with_agg, methods=("bjs",))
    r = results[0]
    assert r.method == "bjs"
    # BJS ATT is a float; SE is positive.
    assert isinstance(r.att, float)
    import math

    assert r.se > 0 or math.isnan(r.se)  # NaN acceptable if degenerate
    # Diagnostics must name the method.
    assert r.diagnostics is not None
    assert "imputation" in r.diagnostics["method"]


def test_sun_abraham_requires_differences() -> None:
    pytest.importorskip("differences")
    from factor_factory.engines.did import registry

    assert "sa" in registry


def test_sun_abraham_fits_staggered_panel() -> None:
    pytest.importorskip("differences")
    panel = staggered_did_panel()
    results = estimate(panel, methods=("sa",))
    r = results[0]
    assert r.method == "sa"
    assert isinstance(r.att, float)
    assert r.diagnostics is not None
    assert r.diagnostics["aggregation"] == "sun_abraham_iw"


def test_multi_method_fit_composable() -> None:
    pytest.importorskip("differences")
    panel = staggered_did_panel()
    results = estimate(panel.attach_treatment_columns(replace=True), methods=("twfe", "bjs"))
    assert len(results) == 2
    methods = {r.method for r in results.results}
    assert methods == {"twfe", "bjs"}
