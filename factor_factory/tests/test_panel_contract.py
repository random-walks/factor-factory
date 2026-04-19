"""Tests for ``factor_factory.tidy.Panel`` contract + invariants."""

from __future__ import annotations

from datetime import date

import pandas as pd
import pytest

from factor_factory.tidy import Panel, TreatmentEvent
from factor_factory.tidy.contracts import PanelMetadata

from ._fixtures.synthetic_panels import (
    large_treatment_effect_with_spillover_panel,
    small_treatment_effect_panel,
    unbalanced_panel,
)


def test_small_treatment_panel_validates() -> None:
    panel = small_treatment_effect_panel()
    panel.validate()
    assert panel.outcome_col == "outcome"
    assert len(panel.unit_ids) == 50
    assert len(panel.periods) == 24


def test_large_panel_has_expected_treatment_columns() -> None:
    panel = large_treatment_effect_with_spillover_panel()
    df = panel.df
    assert "treatment" in df.columns
    assert "treated_unit" in df.columns
    assert "post" in df.columns
    # treatment must equal treated_unit & post
    derived = (df["treated_unit"] & df["post"]).astype("int8")
    assert (df["treatment"] == derived).all()


def test_unbalanced_panel_fails_validation() -> None:
    panel = small_treatment_effect_panel()
    bad_df = unbalanced_panel()
    with pytest.raises(ValueError, match="unbalanced"):
        Panel(bad_df, panel.metadata)


def test_panel_from_records_basic() -> None:
    records = [
        {"community_district": "MN-01", "created_date": "2024-01-15"},
        {"community_district": "MN-01", "created_date": "2024-02-15"},
        {"community_district": "MN-02", "created_date": "2024-01-15"},
        {"community_district": "MN-02", "created_date": "2024-02-15"},
        {"community_district": "MN-02", "created_date": "2024-02-20"},
    ]
    panel = Panel.from_records(
        records,
        geography="community_district",
        freq="ME",
        outcome_col="complaint_count",
    )
    df = panel.df
    assert set(panel.unit_ids) == {"MN-01", "MN-02"}
    # MN-02 in February has two records
    feb_end = pd.Timestamp("2024-02-29")
    assert df.loc[("MN-02", feb_end), "complaint_count"] == 2.0
    assert df.loc[("MN-01", feb_end), "complaint_count"] == 1.0


def test_panel_from_records_with_treatment_event() -> None:
    records = [
        {"community_district": "MN-01", "created_date": "2024-01-15"},
        {"community_district": "MN-01", "created_date": "2024-08-15"},
        {"community_district": "MN-02", "created_date": "2024-01-15"},
        {"community_district": "MN-02", "created_date": "2024-08-15"},
    ]
    event = TreatmentEvent(
        name="pilot",
        treated_units=("MN-01",),
        treatment_date=date(2024, 6, 1),
        geography="community_district",
    )
    panel = Panel.from_records(
        records,
        geography="community_district",
        freq="ME",
        treatment_events=(event,),
        outcome_col="complaint_count",
    )
    df = panel.df
    jan_end = pd.Timestamp("2024-01-31")
    aug_end = pd.Timestamp("2024-08-31")
    assert df.loc[("MN-01", jan_end), "treatment"] == 0
    assert df.loc[("MN-01", aug_end), "treatment"] == 1
    assert df.loc[("MN-02", aug_end), "treatment"] == 0  # control unit


def test_panel_record_view_round_trip() -> None:
    records = [
        {
            "community_district": "MN-01",
            "created_date": "2024-01-15",
            "latitude": 40.7,
            "longitude": -74.0,
        },
        {
            "community_district": "MN-01",
            "created_date": "2024-02-15",
            "latitude": 40.71,
            "longitude": -74.01,
        },
        {
            "community_district": "MN-02",
            "created_date": "2024-02-15",
            "latitude": 40.72,
            "longitude": -73.99,
        },
    ]
    panel = Panel.from_records(
        records,
        geography="community_district",
        freq="ME",
        record_view=True,
    )
    rv = panel.record_view
    assert len(rv.df) == 3
    assert "latitude" in rv.df.columns
    assert "longitude" in rv.df.columns
    distances = rv.distance_to_point(lon=-74.0, lat=40.7)
    assert distances.iloc[0] < 0.001  # ~zero distance for the first record


def test_panel_to_from_parquet(tmp_path) -> None:
    panel = small_treatment_effect_panel()
    out = panel.to_parquet(tmp_path / "panel.parquet")
    assert out.exists()
    assert out.with_suffix(".parquet.meta.json").exists()
    reloaded = Panel.from_parquet(out)
    pd.testing.assert_frame_equal(panel.df, reloaded.df)
    assert reloaded.outcome_col == panel.outcome_col


def test_panel_construction_rejects_non_numeric_outcome() -> None:
    """Outcomes must be numeric (any int/float). Object/string dtype is rejected."""
    panel = small_treatment_effect_panel()
    bad = panel.df.copy()
    bad["outcome"] = bad["outcome"].astype(str)
    metadata = PanelMetadata(
        geography="synthetic_unit",
        freq="ME",
        outcome_col="outcome",
        record_count=len(bad),
    )
    with pytest.raises(ValueError, match="numeric"):
        Panel(bad, metadata)


def test_panel_construction_accepts_integer_outcome() -> None:
    """RCT counts / survival indicators are integer outcomes — no float coercion forced."""
    panel = small_treatment_effect_panel()
    int_df = panel.df.copy()
    int_df["outcome"] = int_df["outcome"].round().astype("int64")
    metadata = PanelMetadata(
        geography="synthetic_unit",
        freq="ME",
        outcome_col="outcome",
        record_count=len(int_df),
    )
    rebuilt = Panel(int_df, metadata)
    assert rebuilt.df["outcome"].dtype == "int64"
