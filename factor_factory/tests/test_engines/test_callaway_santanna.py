"""Conformance tests for the Callaway-Sant'Anna DiD adapter.

CS is the right tool for staggered-rollout panels where TWFE suffers
from negative-weights bias (Goodman-Bacon 2021).
"""

from __future__ import annotations

import pytest

from factor_factory.engines.did import registry
from factor_factory.engines.did._base import DidResult

from .._fixtures.cross_domain import staggered_did_panel
from .._fixtures.synthetic_panels import (
    null_effect_panel,
    small_treatment_effect_panel,
)

pytestmark = pytest.mark.skipif(
    "cs" not in registry.available(),
    reason="CallawaySantannaEngine not registered (install factor-factory[did]).",
)


def test_cs_returns_did_result_on_simple_panel() -> None:
    panel = small_treatment_effect_panel()
    result = registry["cs"].fit(panel, outcome=panel.outcome_col)
    assert isinstance(result, DidResult)
    assert result.method == "cs"
    assert 0.0 <= result.p_value <= 1.0
    assert result.n > 0


def test_cs_recovers_known_effect_on_simple_panel() -> None:
    panel = small_treatment_effect_panel()  # ATT = 5.0
    result = registry["cs"].fit(panel, outcome=panel.outcome_col)
    assert abs(result.att - 5.0) < 2.0


def test_cs_null_effect_not_significant() -> None:
    panel = null_effect_panel()
    result = registry["cs"].fit(panel, outcome=panel.outcome_col)
    assert result.p_value > 0.05


def test_cs_handles_staggered_rollout() -> None:
    """The headline use-case: TWFE biased, CS unbiased."""
    panel = staggered_did_panel()
    result = registry["cs"].fit(panel, outcome=panel.outcome_col)
    # True average ATT across cohorts (3.0+1.5+5.0)/3 ≈ 3.17
    assert abs(result.att - 3.17) < 1.5
    assert result.diagnostics is not None
    assert result.diagnostics["n_cohorts"] == 3


def test_cs_requires_treatment_events() -> None:
    """CS can't run on event-free panels — clear error message."""
    from datetime import date

    from factor_factory.tidy import Panel, TreatmentEvent

    # Build a panel with treatment_events, then strip them
    panel = small_treatment_effect_panel()
    bad_metadata = panel.metadata.model_copy(update={"treatment_events": ()})
    bad_panel = Panel(panel.df.copy(), bad_metadata)
    with pytest.raises(ValueError, match="treatment_events"):
        registry["cs"].fit(bad_panel, outcome=bad_panel.outcome_col)
    # Suppress unused-import warning
    _ = TreatmentEvent, date


def test_cs_rejects_continuous_period_panel() -> None:
    """CS needs ordered discrete time; float-period panels are out of scope."""
    from factor_factory.tests._fixtures.cross_domain import chem_assay_panel

    panel = chem_assay_panel()
    # chem panel has no events; add a synthetic one to surface the period_kind check
    from datetime import date as _date

    from factor_factory.tidy import TreatmentEvent

    fake_event = TreatmentEvent(
        name="x",
        treated_units=panel.unit_ids[:2],
        period_value=1.0,
        dimension="compound",
    )
    metadata = panel.metadata.model_copy(update={"treatment_events": (fake_event,)})
    from factor_factory.tidy import Panel

    panel_with_event = Panel(panel.df.copy(), metadata)
    with pytest.raises(ValueError, match="period_kind"):
        registry["cs"].fit(panel_with_event, outcome=panel_with_event.outcome_col)
    _ = _date
