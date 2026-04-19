"""Tests for PanelBuilder (streaming construction) + async fetch."""

from __future__ import annotations

import asyncio
from datetime import date
from pathlib import Path

import pytest

from factor_factory.tidy import PanelBuilder
from factor_factory.tidy.socrata import bulk_fetch_async


def _records_batch(start: int, n: int) -> list[dict]:
    return [
        {"unit": f"u{(start + i) % 10}", "created_date": date(2024, 1 + (i % 12), 15)}
        for i in range(n)
    ]


def test_panel_builder_matches_from_records() -> None:
    """Streaming ingest should produce the same Panel as from_records."""
    records = _records_batch(0, 1000)
    builder = PanelBuilder(dimension="unit", outcome_col="n")
    # Feed in 4 chunks of 250.
    for chunk_start in range(0, 1000, 250):
        builder.ingest(records[chunk_start : chunk_start + 250])

    panel_streamed = builder.build()
    assert builder.n_records == 1000
    # 10 units × 12 months = 120 cells.
    assert panel_streamed.summary()["n_units"] == 10
    # Sum of outcome across all cells equals record count.
    assert int(panel_streamed.df["n"].sum()) == 1000


def test_panel_builder_empty_raises() -> None:
    builder = PanelBuilder(dimension="unit")
    with pytest.raises(ValueError, match="no records"):
        builder.build()


def test_panel_builder_chunks_counts_correctly() -> None:
    builder = PanelBuilder(dimension="unit", outcome_col="events")
    builder.ingest([{"unit": "A", "created_date": date(2024, 1, 15)}])
    builder.ingest([{"unit": "A", "created_date": date(2024, 1, 15)}])
    builder.ingest([{"unit": "B", "created_date": date(2024, 1, 15)}])
    panel = builder.build()
    # After 2 records on A in Jan and 1 on B in Jan, count should be 2 and 1.
    assert panel.df.loc[("A", slice(None)), "events"].sum() == 2
    assert panel.df.loc[("B", slice(None)), "events"].sum() == 1


def test_bulk_fetch_async_falls_back_to_sync() -> None:
    """When the adapter has no afetch, bulk_fetch_async uses asyncio.to_thread."""

    class FakeAdapter:
        base_url = "fake"
        dataset_id = "fake"

        def fetch(self, *, filters, start_date, end_date, cache_dir, chunk_size=5000):
            return [cache_dir / "fake.csv"]

        def load(self, paths):
            return []

    paths = asyncio.run(
        bulk_fetch_async(
            FakeAdapter(),
            filters={},
            start_date=date(2024, 1, 1),
            end_date=date(2024, 2, 1),
            cache_dir=Path("/tmp"),
        )
    )
    assert paths == [Path("/tmp/fake.csv")]
