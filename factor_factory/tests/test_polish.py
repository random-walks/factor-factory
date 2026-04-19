"""Tests for the Batch-4 framework-polish additions.

Covers:
- ``Panel.attach_treatment_columns()`` public method
- ``Panel.validate(strict=False)`` fast path
- ``Panel.summary()`` convenience
- ``from_records`` early ``record_view_columns`` schema check
- ``<Family>Result.summary_table()`` parity across DiD / Survival /
  EventStudy / SDID / Mediation
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

import pandas as pd
import pytest

from factor_factory.tidy import Panel, TreatmentEvent


def _records() -> list[dict[str, Any]]:
    return [
        {"unit": "A", "created_date": date(2024, 1, 15), "latitude": 40.0, "longitude": -74.0},
        {"unit": "A", "created_date": date(2024, 2, 15), "latitude": 40.0, "longitude": -74.0},
        {"unit": "B", "created_date": date(2024, 1, 15), "latitude": 40.1, "longitude": -74.1},
        {"unit": "B", "created_date": date(2024, 2, 15), "latitude": 40.1, "longitude": -74.1},
    ]


def _small_panel() -> Panel:
    return Panel.from_records(_records(), dimension="unit", outcome_col="n")


# ─── Panel.summary ───────────────────────────────────────────────────────────


def test_panel_summary_shape() -> None:
    panel = _small_panel()
    summary = panel.summary()
    assert summary["n_units"] == 2
    assert summary["n_periods"] == 2
    assert summary["n_records"] == 4
    assert summary["period_kind"] == "timestamp"
    assert summary["dimension"] == "unit"
    assert summary["outcome_cols"] == ["n"]
    assert summary["n_outcomes"] == 1
    assert summary["n_treatment_events"] == 0
    assert summary["treated_unit_share"] is None  # no treatment column yet
    assert summary["has_record_view"] is False
    assert "provenance" in summary


def test_panel_summary_with_treatment() -> None:
    panel = Panel.from_records(
        _records(),
        dimension="unit",
        outcome_col="n",
        treatment_events=(
            TreatmentEvent(
                name="policy",
                treated_units=("A",),
                treatment_date=date(2024, 2, 1),
                dimension="unit",
            ),
        ),
    )
    summary = panel.summary()
    assert summary["n_treatment_events"] == 1
    assert summary["treatment_event_names"] == ["policy"]
    assert summary["treated_unit_share"] == pytest.approx(0.5)


# ─── Panel.attach_treatment_columns ──────────────────────────────────────────


def test_attach_treatment_columns_returns_new_panel() -> None:
    panel = _small_panel()
    event = TreatmentEvent(
        name="policy",
        treated_units=("A",),
        treatment_date=date(2024, 2, 1),
        dimension="unit",
    )
    new_panel = panel.attach_treatment_columns((event,))
    assert "treatment__policy" in new_panel.df.columns
    assert "treated_unit__policy" in new_panel.df.columns
    assert "post__policy" in new_panel.df.columns
    # Original unchanged
    assert "treatment__policy" not in panel.df.columns
    # Metadata reflects attachment
    assert len(new_panel.treatment_events) == 1


def test_attach_treatment_columns_forbids_overwrite() -> None:
    event = TreatmentEvent(
        name="policy",
        treated_units=("A",),
        treatment_date=date(2024, 2, 1),
        dimension="unit",
    )
    panel = Panel.from_records(
        _records(),
        dimension="unit",
        outcome_col="n",
        treatment_events=(event,),
    )
    with pytest.raises(ValueError, match="would overwrite"):
        panel.attach_treatment_columns((event,))


def test_attach_treatment_columns_replace_true_overwrites() -> None:
    event = TreatmentEvent(
        name="policy",
        treated_units=("A",),
        treatment_date=date(2024, 2, 1),
        dimension="unit",
    )
    panel = Panel.from_records(
        _records(),
        dimension="unit",
        outcome_col="n",
        treatment_events=(event,),
    )
    new_panel = panel.attach_treatment_columns((event,), replace=True)
    assert "treatment__policy" in new_panel.df.columns


# ─── Panel.validate(strict) ──────────────────────────────────────────────────


def test_validate_strict_default() -> None:
    panel = _small_panel()
    panel.validate()  # strict=True by default; must pass


def test_validate_strict_false_fast_path() -> None:
    panel = _small_panel()
    panel.validate(strict=False)  # must also pass — same panel


def test_init_validate_false_skips_invariants() -> None:
    # Construct a deliberately unbalanced df (drop one row) and skip validation.
    panel = _small_panel()
    mutated = panel.df.iloc[:3].copy()
    # strict check would reject this — but validate=False should allow it.
    Panel(mutated, panel.metadata, validate=False)


# ─── record_view_columns early schema check ──────────────────────────────────


def test_record_view_missing_columns_raises() -> None:
    # Records have no latitude / longitude; request them.
    records = [
        {"unit": "A", "created_date": date(2024, 1, 15)},
        {"unit": "A", "created_date": date(2024, 2, 15)},
    ]
    with pytest.raises(ValueError, match="record_view_columns"):
        Panel.from_records(
            records,
            dimension="unit",
            outcome_col="n",
            record_view=True,
            record_view_columns=("latitude", "longitude"),
        )


def test_record_view_partial_columns_ok() -> None:
    # Records have latitude but not longitude — should work (at least one col present).
    records = [
        {"unit": "A", "created_date": date(2024, 1, 15), "latitude": 40.0},
        {"unit": "A", "created_date": date(2024, 2, 15), "latitude": 40.0},
    ]
    panel = Panel.from_records(
        records,
        dimension="unit",
        outcome_col="n",
        record_view=True,
        record_view_columns=("latitude", "longitude"),
    )
    assert panel.has_record_view


# ─── Result.summary_table() parity ───────────────────────────────────────────


def test_did_result_summary_table() -> None:
    from factor_factory.engines.did import DidResult

    result = DidResult(
        method="twfe",
        att=1.2,
        se=0.3,
        ci_95=(0.6, 1.8),
        p_value=0.001,
        n=100,
    )
    df = result.summary_table()
    assert isinstance(df, pd.DataFrame)
    assert df.index.name == "method"
    assert "att" in df.columns
    assert df.loc["twfe", "att"] == 1.2


def test_sdid_result_summary_table() -> None:
    from factor_factory.engines.sdid import SdidResult

    result = SdidResult(
        method="sdid",
        att=4.5,
        se=0.25,
        ci_95=(4.0, 5.0),
        p_value=0.001,
        n=500,
        n_treated=5,
        n_control=45,
    )
    df = result.summary_table()
    assert df.loc["sdid", "att"] == 4.5
    assert df.loc["sdid", "n_treated"] == 5


def test_survival_result_summary_table() -> None:
    from factor_factory.engines.survival import SurvivalResult

    result = SurvivalResult(
        method="cox_ph",
        median_survival=42.0,
        n_subjects=200,
        n_events=80,
        hazard_ratios={"treatment": 0.75, "age": 1.02},
        p_values={"treatment": 0.01, "age": 0.03},
    )
    df = result.summary_table()
    assert "hr[treatment]" in df.columns
    assert df.loc["cox_ph", "n_events"] == 80


def test_event_study_result_summary_table() -> None:
    from factor_factory.engines.event_study import EventStudyResult

    result = EventStudyResult(
        method="market_adjusted",
        n_events=50,
        average_abnormal_return=0.002,
        car_event_window=0.01,
        car_se=0.003,
        car_t_stat=3.33,
        car_p_value=0.001,
    )
    df = result.summary_table()
    assert df.loc["market_adjusted", "car"] == 0.01


def test_mediation_result_summary_table() -> None:
    from factor_factory.engines.mediation import MediationResult

    result = MediationResult(
        method="four_way",
        n_subjects=1000,
        treatment="A",
        mediator="M",
        outcome="Y",
        total_effect=4.1,
        cde=2.0,
        int_ref=0.15,
        int_med=0.45,
        pie=1.5,
        decomposition_residual=0.0,
    )
    df = result.summary_table()
    assert df.loc["four_way", "cde"] == 2.0
    assert df.loc["four_way", "total_effect"] == 4.1


# ─── Provenance shape in summary ─────────────────────────────────────────────


def test_panel_summary_provenance_serializes() -> None:
    panel = _small_panel()
    summary = panel.summary()
    prov = summary["provenance"]
    # created_at is ISO-formatted for JSON.
    if prov["created_at"] is not None:
        datetime.fromisoformat(prov["created_at"])
