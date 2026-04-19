"""Tests for the generalized TreatmentEvent + per-event column attachment."""

from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd
import pytest

from factor_factory.tidy import Panel, TreatmentEvent


def _make_records(units: list[str], periods: list[date]) -> list[dict]:
    return [{"u": u, "created_date": p} for u in units for p in periods]


def test_per_event_columns_for_single_event() -> None:
    units = ["A", "B", "C", "D"]
    periods = [date(2024, 1, 31), date(2024, 7, 31), date(2024, 12, 31)]
    records = _make_records(units, periods)
    event = TreatmentEvent(
        name="pilot",
        treated_units=("A", "B"),
        treatment_date=date(2024, 6, 1),
        dimension="u",
    )
    panel = Panel.from_records(
        records,
        dimension="u",
        freq="ME",
        treatment_events=(event,),
    )
    df = panel.df

    # Per-event columns present
    for col in ("treatment__pilot", "treated_unit__pilot", "post__pilot"):
        assert col in df.columns

    # Aggregate columns also present (single binary event)
    assert "treatment" in df.columns
    assert "treated_unit" in df.columns
    assert "post" in df.columns

    # Per-event mirrors aggregate when only one event
    np.testing.assert_array_equal(df["treatment"].to_numpy(), df["treatment__pilot"].to_numpy())


def test_per_event_columns_with_two_disjoint_events() -> None:
    units = ["A", "B", "C", "D", "E", "F"]
    periods = pd.date_range("2024-01-31", periods=12, freq="ME").to_pydatetime()
    records = _make_records(units, [d.date() for d in periods])
    events = (
        TreatmentEvent(
            name="alpha",
            treated_units=("A", "B"),
            treatment_date=date(2024, 4, 1),
            dimension="u",
        ),
        TreatmentEvent(
            name="beta",
            treated_units=("C", "D"),
            treatment_date=date(2024, 8, 1),
            dimension="u",
        ),
    )
    panel = Panel.from_records(records, dimension="u", freq="ME", treatment_events=events)
    df = panel.df

    # Per-event columns disambiguated
    assert df["treated_unit__alpha"].xs("A", level="unit_id").iloc[0] == 1
    assert df["treated_unit__beta"].xs("A", level="unit_id").iloc[0] == 0

    # Aggregate treated_unit is the union
    assert (df["treated_unit"].xs("A", level="unit_id") == 1).all()
    assert (df["treated_unit"].xs("C", level="unit_id") == 1).all()
    assert (df["treated_unit"].xs("E", level="unit_id") == 0).all()

    # Aggregate post is OR across events: at least one event's post mask
    last_period = periods[-1].date()
    assert df.loc[("A", pd.Timestamp(last_period)), "post"] == 1


def test_continuous_treatment_event() -> None:
    units = ["A", "B", "C", "D"]
    periods = [date(2024, 1, 31), date(2024, 7, 31), date(2024, 12, 31)]
    records = _make_records(units, periods)
    event = TreatmentEvent(
        name="dose",
        treated_units=("A", "B"),
        treatment_date=date(2024, 6, 1),
        dimension="u",
        kind="continuous",
        intensity=2.5,
    )
    panel = Panel.from_records(records, dimension="u", freq="ME", treatment_events=(event,))
    df = panel.df

    assert df["treatment__dose"].dtype == np.float64
    assert df["treatment"].dtype == np.float64
    treated_post = df[df["treatment__dose"] > 0]["treatment__dose"]
    assert np.allclose(treated_post.unique(), [2.5])


def test_categorical_treatment_event_produces_arm_column() -> None:
    units = ["A", "B", "C", "D"]
    periods = [date(2024, 1, 31), date(2024, 7, 31), date(2024, 12, 31)]
    records = _make_records(units, periods)
    event = TreatmentEvent(
        name="vaccine",
        treated_units=("A", "B"),
        treatment_date=date(2024, 6, 1),
        dimension="u",
        kind="categorical",
        arm="active_arm",
    )
    panel = Panel.from_records(records, dimension="u", freq="ME", treatment_events=(event,))
    df = panel.df

    assert "arm__vaccine" in df.columns
    arm_values = set(df["arm__vaccine"].unique())
    assert arm_values == {"active_arm", "control"}
    # No aggregate `treatment` column when only categorical events present
    assert "treatment" not in df.columns


def test_treatment_event_validation_rejects_missing_anchor() -> None:
    with pytest.raises(ValueError, match="treatment_date.*period_value"):
        TreatmentEvent(name="bad", treated_units=("A",), dimension="u")


def test_treatment_event_validation_rejects_both_anchors() -> None:
    with pytest.raises(ValueError, match="exactly one"):
        TreatmentEvent(
            name="bad",
            treated_units=("A",),
            treatment_date=date(2024, 1, 1),
            period_value=5,
            dimension="u",
        )


def test_treatment_event_continuous_requires_intensity() -> None:
    with pytest.raises(ValueError, match="intensity"):
        TreatmentEvent(
            name="bad",
            treated_units=("A",),
            treatment_date=date(2024, 1, 1),
            dimension="u",
            kind="continuous",
        )


def test_treatment_event_categorical_requires_arm() -> None:
    with pytest.raises(ValueError, match="arm"):
        TreatmentEvent(
            name="bad",
            treated_units=("A",),
            treatment_date=date(2024, 1, 1),
            dimension="u",
            kind="categorical",
        )


def test_treatment_event_empty_treated_units_rejected() -> None:
    with pytest.raises(ValueError, match="no treated_units"):
        TreatmentEvent(
            name="bad",
            treated_units=(),
            treatment_date=date(2024, 1, 1),
            dimension="u",
        )


def test_legacy_geography_kwarg_aliases_to_dimension() -> None:
    """Old TreatmentEvent(geography="x", ...) call sites still work."""
    ev = TreatmentEvent(
        name="legacy",
        treated_units=("A",),
        treatment_date=date(2024, 1, 1),
        geography="community_district",
    )
    assert ev.dimension == "community_district"


def test_period_value_anchor_for_non_time_panel() -> None:
    """For float-period panels, TreatmentEvent uses period_value not treatment_date."""
    units = ["C1", "C2"]
    concentrations = [0.1, 1.0, 10.0, 100.0]
    records = [{"u": u, "period": c, "response": 0.5} for u in units for c in concentrations]
    event = TreatmentEvent(
        name="threshold",
        treated_units=("C1",),
        period_value=1.0,
        dimension="compound",
        kind="binary",
    )
    panel = Panel.from_records(
        records,
        dimension="u",
        freq=None,
        period_kind="float",
        treatment_events=(event,),
        outcome_col="n",
    )
    df = panel.df
    # C1 at concentration >= 1.0 is treated
    assert df.loc[("C1", 1.0), "treatment__threshold"] == 1
    assert df.loc[("C1", 0.1), "treatment__threshold"] == 0
    assert df.loc[("C2", 100.0), "treatment__threshold"] == 0
