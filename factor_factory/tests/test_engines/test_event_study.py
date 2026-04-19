"""Conformance tests for the EventStudy engine family."""

from __future__ import annotations

import pytest

from factor_factory.engines.event_study import estimate, registry
from factor_factory.engines.event_study._base import EventStudyResult

from .._fixtures.cross_domain import finance_event_study_panel


def test_market_adjusted_returns_event_study_result() -> None:
    panel = finance_event_study_panel()
    result = registry["market_adjusted"].fit(panel, outcome="returns", event_window=(-2, 5))
    assert isinstance(result, EventStudyResult)
    assert result.method == "market_adjusted"
    assert result.n_events > 0
    assert result.event_window == (-2, 5)
    assert result.abnormal_return_curve is not None


def test_market_adjusted_detects_abnormal_returns() -> None:
    """The fixture seeds +2bp abnormal returns post-event for treated tickers."""
    panel = finance_event_study_panel()
    result = registry["market_adjusted"].fit(panel, outcome="returns", event_window=(0, 30))
    # Average CAR over a 30-day post-event window should be positive
    assert result.car_event_window > 0
    # 2bp/day × 30 days × 10 treated = sizeable t-stat
    assert result.car_t_stat > 1.0


def test_event_study_requires_treatment_events() -> None:
    panel = finance_event_study_panel()
    bad_metadata = panel.metadata.model_copy(update={"treatment_events": ()})
    from factor_factory.tidy import Panel

    bad_panel = Panel(panel.df.copy(), bad_metadata)
    with pytest.raises(ValueError, match="treatment_events"):
        registry["market_adjusted"].fit(bad_panel, outcome="returns")


def test_estimate_dispatcher() -> None:
    panel = finance_event_study_panel()
    results = estimate(panel, methods=("market_adjusted",), event_window=(-1, 1))
    assert len(list(results)) == 1
