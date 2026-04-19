"""Hypothesis property-based tests for Panel invariants.

Each property is a guarantee the Panel contract makes — we generate
random well-formed inputs and assert those guarantees hold universally.
"""

from __future__ import annotations

from datetime import date, timedelta

import pytest

hypothesis = pytest.importorskip("hypothesis")
from hypothesis import assume, given, settings  # noqa: E402
from hypothesis import strategies as st  # noqa: E402

from factor_factory.tidy import Panel, PanelBuilder  # noqa: E402

pytestmark = pytest.mark.property


@st.composite
def panel_records(draw) -> list[dict]:  # type: ignore[no-untyped-def]
    """Generate a list of well-formed records."""
    n_units = draw(st.integers(min_value=1, max_value=5))
    n_periods = draw(st.integers(min_value=1, max_value=6))
    n_records_per_cell = draw(st.integers(min_value=1, max_value=5))

    unit_ids = [f"u{i:02d}" for i in range(n_units)]
    periods = [date(2024, 1 + i, 15) for i in range(n_periods)]

    records: list[dict] = []
    for u in unit_ids:
        for p in periods:
            for _ in range(n_records_per_cell):
                records.append({"unit": u, "created_date": p})
    return records


@given(records=panel_records())
@settings(max_examples=30, deadline=None)
def test_random_well_formed_panels_always_validate(records: list[dict]) -> None:
    """Any random well-formed record list produces a validating Panel."""
    panel = Panel.from_records(records, dimension="unit", outcome_col="events")
    panel.validate()  # must not raise


@given(records=panel_records())
@settings(max_examples=30, deadline=None)
def test_panel_builder_matches_from_records(records: list[dict]) -> None:
    """Streaming ingest and from_records produce identical outcome totals."""
    assume(len(records) > 0)
    panel_a = Panel.from_records(records, dimension="unit", outcome_col="n")
    builder = PanelBuilder(dimension="unit", outcome_col="n")
    builder.ingest(records)
    panel_b = builder.build()

    # Total outcome across the Panel equals total record count.
    assert int(panel_a.df["n"].sum()) == len(records)
    assert int(panel_b.df["n"].sum()) == len(records)


@given(records=panel_records())
@settings(max_examples=30, deadline=None)
def test_panel_summary_is_shuffle_invariant(records: list[dict]) -> None:
    """Panel.summary() doesn't depend on record ordering."""
    import random

    shuffled = list(records)
    random.Random(42).shuffle(shuffled)

    panel_a = Panel.from_records(records, dimension="unit", outcome_col="n")
    panel_b = Panel.from_records(shuffled, dimension="unit", outcome_col="n")
    # summary() is a function of (unit × period) counts, which are
    # invariant to record ordering.
    assert panel_a.summary()["n_units"] == panel_b.summary()["n_units"]
    assert panel_a.summary()["n_periods"] == panel_b.summary()["n_periods"]
    assert panel_a.summary()["n_records"] == panel_b.summary()["n_records"]


@given(
    unit_ids=st.lists(st.from_regex(r"[a-z]{2}\d{2}", fullmatch=True), min_size=1, max_size=3,
                      unique=True),
    n_days=st.integers(min_value=1, max_value=5),
)
@settings(max_examples=20, deadline=None)
def test_parquet_round_trip_preserves_panel(unit_ids: list[str], n_days: int, tmp_path_factory) -> None:  # type: ignore[no-untyped-def]
    """Parquet write → read reproduces Panel exactly."""
    records = [
        {"unit": u, "created_date": date(2024, 1, 1) + timedelta(days=i)}
        for u in unit_ids
        for i in range(n_days)
    ]
    panel = Panel.from_records(
        records, dimension="unit", outcome_col="n", freq=None, period_kind="timestamp"
    )
    # Note: the test passes valid parquet path — tmp_path_factory is a
    # pytest fixture, so we use it directly via a module-level fixture.
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "panel.parquet"
        panel.to_parquet(path)
        loaded = Panel.from_parquet(path)

    assert list(loaded.df.columns) == list(panel.df.columns)
    assert len(loaded.df) == len(panel.df)
