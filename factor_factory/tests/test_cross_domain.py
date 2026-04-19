"""Cross-domain conformance — Panel contract works across data shapes.

Each fixture exercises a different generalization axis:

- finance: business-day periods (no monthly bin), multiple outcomes,
  weights column.
- RCT: multi-arm (categorical) treatments, integer outcome
  (adverse_events count).
- agronomic: continuous treatment intensity, semi-annual freq.
- chemistry: float period_kind (no time at all).
- staggered DiD: multiple binary events, per-event columns.
"""

from __future__ import annotations

import numpy as np
import pytest

from factor_factory.tidy import Panel

from ._fixtures.cross_domain import (
    agronomic_dose_response_panel,
    chem_assay_panel,
    finance_event_study_panel,
    rct_longitudinal_panel,
    staggered_did_panel,
)


@pytest.mark.parametrize(
    "factory",
    [
        finance_event_study_panel,
        rct_longitudinal_panel,
        agronomic_dose_response_panel,
        chem_assay_panel,
        staggered_did_panel,
    ],
)
def test_cross_domain_panel_validates(factory) -> None:  # type: ignore[no-untyped-def]
    panel = factory()
    assert isinstance(panel, Panel)
    panel.validate()


def test_finance_panel_has_multiple_outcomes_and_weights() -> None:
    panel = finance_event_study_panel()
    assert panel.outcome_cols == ("returns", "abnormal_returns")
    assert panel.outcome_col == "returns"  # primary
    assert panel.weights_col == "market_cap_mm"
    assert panel.weights is not None
    assert panel.weights.notna().all()
    assert panel.dimension == "ticker"
    assert panel.freq is None  # business days don't fit ME/QE/YE


def test_rct_categorical_arms_produce_per_event_arm_columns() -> None:
    panel = rct_longitudinal_panel()
    df = panel.df
    # Categorical events produce arm__<name> columns, not treatment__<name>
    assert "arm__low_dose" in df.columns
    assert "arm__high_dose" in df.columns
    # Aggregate columns should NOT exist (only categorical events present)
    assert "treatment" not in df.columns
    # Per-event treated_unit / post columns DO exist for categorical events
    assert "treated_unit__low_dose" in df.columns
    assert "post__low_dose" in df.columns


def test_agronomic_continuous_treatment_produces_float_treatment_column() -> None:
    panel = agronomic_dose_response_panel()
    df = panel.df
    # Continuous treatment column is float64 (intensity-scaled mask)
    assert df["treatment__fertilizer_program"].dtype == np.float64
    # Aggregate `treatment` column is float (continuous events present)
    assert df["treatment"].dtype == np.float64
    # Treated-post intensity equals 80.0 kg/ha
    treated_post = df[df["treatment__fertilizer_program"] > 0]["treatment__fertilizer_program"]
    assert np.allclose(treated_post.unique(), [80.0])


def test_chem_panel_float_period_kind() -> None:
    panel = chem_assay_panel()
    assert panel.period_kind == "float"
    assert panel.freq is None
    # Periods are concentrations (μM) — float dtype
    assert np.issubdtype(panel.periods.dtype, np.floating)
    # No treatment columns at all (no events)
    assert "treatment" not in panel.df.columns
    assert "treated_unit" not in panel.df.columns


def test_staggered_did_per_event_columns() -> None:
    panel = staggered_did_panel()
    df = panel.df
    for ev_name in ("alpha", "beta", "gamma"):
        assert f"treatment__{ev_name}" in df.columns
        assert f"treated_unit__{ev_name}" in df.columns
        assert f"post__{ev_name}" in df.columns

    # Aggregate columns: union of all events
    # Every unit is treated by exactly one event, so treated_unit == 1 everywhere
    assert (df["treated_unit"] == 1).all()
    # treatment is sum across events; since events are disjoint, max value is 1 (binary)
    assert df["treatment"].max() == 1
    assert df["treatment"].dtype == np.int8

    # per_event_columns helper
    treatment_col, treated_col, post_col = panel.per_event_columns("alpha")
    assert treatment_col == "treatment__alpha"
    assert treated_col == "treated_unit__alpha"
    assert post_col == "post__alpha"


def test_per_event_columns_raises_for_unknown_event() -> None:
    panel = staggered_did_panel()
    with pytest.raises(KeyError, match="known events"):
        panel.per_event_columns("does_not_exist")


def test_provenance_round_trips_through_parquet(tmp_path) -> None:  # type: ignore[no-untyped-def]
    panel = finance_event_study_panel()
    out = panel.to_parquet(tmp_path / "panel.parquet")
    reloaded = Panel.from_parquet(out)
    assert reloaded.provenance.data_source == "synthetic"
    assert reloaded.provenance.license == "MIT"
    assert reloaded.outcome_cols == ("returns", "abnormal_returns")
    assert reloaded.dimension == "ticker"
