"""Fama-French factor-model event study (Batch 6, v1.3.0).

Uses a synthetic factor DataFrame to test adapter wiring without
depending on Ken French's live data endpoint.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from factor_factory.engines.event_study import estimate
from factor_factory.tests._fixtures.cross_domain import finance_event_study_panel


def _synthetic_ff3_factors(panel_df: pd.DataFrame) -> pd.DataFrame:
    """Build a synthetic FF3 factor series aligned to the panel's periods."""
    periods = sorted(panel_df.index.get_level_values("period").unique())
    rng = np.random.default_rng(42)
    n = len(periods)
    return pd.DataFrame(
        {
            "mkt_rf": rng.normal(0.0005, 0.01, n),
            "smb": rng.normal(0.0001, 0.005, n),
            "hml": rng.normal(0.0002, 0.005, n),
            "rf": np.full(n, 0.00005),
        },
        index=pd.Index(periods, name="period"),
    )


def test_fama_french_event_study_runs() -> None:
    panel = finance_event_study_panel()
    factors = _synthetic_ff3_factors(panel.df)
    results = estimate(
        panel,
        methods=("fama_french",),
        outcome="returns",
        event_window=(-1, 1),
        estimation_window=(-60, -10),
        factor_model="ff3",
        factor_source=factors,
    )
    r = results[0]
    assert r.method == "fama_french"
    assert r.diagnostics is not None
    assert r.diagnostics["factor_model"] == "ff3"
    assert r.diagnostics["factor_cols"] == ["mkt_rf", "smb", "hml"]
    # Should fit at least one treated unit.
    assert r.diagnostics["n_treated_units_fitted"] >= 1
    # AR curve should cover the event window.
    assert r.abnormal_return_curve is not None
    assert not r.abnormal_return_curve.empty


def test_fama_french_requires_treatment_event() -> None:
    from datetime import date

    from factor_factory.engines.event_study.fama_french import FamaFrenchEngine
    from factor_factory.tidy import Panel

    # Build a timestamp panel with no treatment_events.
    records = [
        {"unit": "A", "created_date": date(2024, 1, 15)},
        {"unit": "A", "created_date": date(2024, 2, 15)},
        {"unit": "B", "created_date": date(2024, 1, 15)},
        {"unit": "B", "created_date": date(2024, 2, 15)},
    ]
    panel = Panel.from_records(records, dimension="unit", outcome_col="n")

    engine = FamaFrenchEngine()
    with pytest.raises(ValueError, match="TreatmentEvent"):
        engine.fit(panel, outcome=panel.outcome_col)


def test_fama_french_requires_timestamp_periods() -> None:
    from factor_factory.engines.event_study.fama_french import FamaFrenchEngine
    from factor_factory.tests._fixtures.cross_domain import chem_assay_panel

    engine = FamaFrenchEngine()
    panel = chem_assay_panel()  # float period_kind
    with pytest.raises(ValueError, match="period_kind"):
        engine.fit(panel, outcome=panel.outcome_col)
