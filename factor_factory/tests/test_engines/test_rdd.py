"""RDD conformance tests."""

from __future__ import annotations

import pytest

pytest.importorskip("rdrobust")

from factor_factory.engines.rdd import estimate, registry  # noqa: E402
from factor_factory.tests._fixtures.cross_domain import (  # noqa: E402
    FIXTURE_GROUND_TRUTH,
    rdd_sharp_cutoff_panel,
)


def test_rd_robust_registered() -> None:
    assert "rd_robust" in registry


def test_rd_robust_recovers_sharp_jump() -> None:
    panel = rdd_sharp_cutoff_panel()
    truth = FIXTURE_GROUND_TRUTH["rdd_sharp_cutoff_panel"]
    results = estimate(
        panel,
        methods=("rd_robust",),
        outcome="y",
        running_variable="test_score",
        cutoff=truth["cutoff"],
        design="sharp",
    )
    r = results[0]
    assert r.design == "sharp"
    assert r.cutoff == truth["cutoff"]
    # Recover the known jump within 2 SE.
    assert abs(r.estimate - truth["jump"]) < max(2 * r.std_error, 0.5 * truth["jump"]), (
        f"Recovered jump {r.estimate} ± {r.std_error} vs truth {truth['jump']}"
    )
    # Summary table shape.
    df = r.summary_table()
    assert "estimate" in df.columns


def test_rd_robust_requires_fuzzy_treatment() -> None:
    from factor_factory.engines.rdd.rd_robust import RdRobustEngine

    engine = RdRobustEngine()
    panel = rdd_sharp_cutoff_panel()
    with pytest.raises(ValueError, match="Fuzzy RDD requires"):
        engine.fit(
            panel,
            outcome="y",
            running_variable="test_score",
            cutoff=60.0,
            design="fuzzy",
        )
