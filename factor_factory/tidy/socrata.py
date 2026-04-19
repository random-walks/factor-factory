"""Socrata adapter Protocol + thin convenience wrapper.

Concrete adapters live in domain packages (``nyc311.io``, etc.). This
module pins the Protocol shape so downstream packages can plug into
``Panel.from_records`` without re-implementing the bulk fetch
mechanics each time.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import date
from pathlib import Path
from typing import Protocol


class SocrataAdapter(Protocol):
    """Protocol for fetching records from a Socrata-style open data API."""

    base_url: str
    dataset_id: str

    def fetch(
        self,
        *,
        filters: dict[str, str],
        start_date: date,
        end_date: date,
        cache_dir: Path,
        chunk_size: int = 5000,
    ) -> list[Path]:
        """Fetch records matching ``filters`` and date range, cache as CSV."""
        ...

    def load(self, paths: list[Path]) -> list[dict[str, object]]:
        """Load cached CSVs as a flat list of record dicts."""
        ...


def bulk_fetch(
    adapter: SocrataAdapter,
    *,
    filters: dict[str, str],
    start_date: date,
    end_date: date,
    cache_dir: Path,
    on_progress: Callable[[str, int, int], None] | None = None,
) -> list[Path]:
    """Bulk-fetch + cache wrapper. Delegates to ``adapter.fetch``."""
    if on_progress is not None:
        on_progress("starting", 0, 1)
    paths = adapter.fetch(
        filters=filters, start_date=start_date, end_date=end_date, cache_dir=cache_dir
    )
    if on_progress is not None:
        on_progress("done", 1, 1)
    return paths
