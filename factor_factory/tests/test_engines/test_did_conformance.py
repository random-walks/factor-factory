"""Conformance tests every DiD engine adapter must pass."""

from __future__ import annotations

import pytest

from factor_factory.engines.did import estimate, registry
from factor_factory.engines.did._base import DidResult

from .._fixtures.synthetic_panels import (
    null_effect_panel,
    small_treatment_effect_panel,
)

pytestmark = pytest.mark.skipif(
    not registry.available(),
    reason="No DiD engines registered (install factor-factory[did]).",
)


@pytest.fixture(params=registry.available())
def engine(request):  # type: ignore[no-untyped-def]
    return registry[request.param]


def test_returns_did_result(engine) -> None:  # type: ignore[no-untyped-def]
    panel = small_treatment_effect_panel()
    result = engine.fit(panel, outcome=panel.outcome_col)
    assert isinstance(result, DidResult)
    assert result.method == engine.name
    assert isinstance(result.att, float)
    assert isinstance(result.ci_95, tuple) and len(result.ci_95) == 2
    assert 0.0 <= result.p_value <= 1.0
    assert result.n > 0


def test_recovers_known_treatment_effect(engine) -> None:  # type: ignore[no-untyped-def]
    panel = small_treatment_effect_panel()  # ATT = 5.0
    result = engine.fit(panel, outcome=panel.outcome_col)
    assert abs(result.att - 5.0) < 2.0, (
        f"{engine.name}: ATT {result.att} differs from true 5.0 by >2"
    )


def test_null_effect_not_significant_at_05(engine) -> None:  # type: ignore[no-untyped-def]
    panel = null_effect_panel()
    result = engine.fit(panel, outcome=panel.outcome_col)
    assert result.p_value > 0.05, (
        f"{engine.name} found significant effect on null panel "
        f"(att={result.att}, p={result.p_value})"
    )


def test_ci_brackets_estimate(engine) -> None:  # type: ignore[no-untyped-def]
    panel = small_treatment_effect_panel()
    result = engine.fit(panel, outcome=panel.outcome_col)
    lo, hi = result.ci_95
    assert lo <= result.att <= hi


def test_estimate_dispatcher_returns_summary_table() -> None:
    panel = small_treatment_effect_panel()
    results = estimate(panel, methods=("twfe",))
    table = results.summary_table()
    assert "att" in table.columns
    assert "twfe" in table.index
