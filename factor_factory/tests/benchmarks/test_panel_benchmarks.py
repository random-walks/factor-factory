"""Benchmarks for the Panel construction paths.

Run with ``pytest -m benchmark factor_factory/tests/benchmarks/``.
CI flags regressions > 2× via pytest-benchmark comparison.
"""

from __future__ import annotations

from datetime import date, timedelta

import pytest

pytest.importorskip("pytest_benchmark")

from factor_factory.tidy import Panel, PanelBuilder  # noqa: E402

pytestmark = pytest.mark.benchmark


def _records(n: int) -> list[dict]:
    return [
        {"unit": f"u{(i % 100):03d}", "created_date": date(2024, 1, 1) + timedelta(days=i % 365)}
        for i in range(n)
    ]


def test_from_records_10k(benchmark) -> None:  # type: ignore[no-untyped-def]
    records = _records(10_000)
    benchmark(Panel.from_records, records, dimension="unit", outcome_col="n", freq="ME")


def test_panel_builder_10k(benchmark) -> None:  # type: ignore[no-untyped-def]
    records = _records(10_000)

    def build() -> Panel:
        b = PanelBuilder(dimension="unit", outcome_col="n", freq="ME")
        b.ingest(records)
        return b.build()

    benchmark(build)
