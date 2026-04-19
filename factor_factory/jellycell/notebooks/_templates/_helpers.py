"""Project-local helpers for __PROJECT__.

Kept thin on purpose — most of the heavy lifting lives in
``factor_factory``. Add domain-specific extractors / loaders here as
the project grows.
"""

from __future__ import annotations

from typing import Any


def load_records() -> list[dict[str, Any]]:
    """Replace with a real data loader (e.g., a Socrata adapter call).

    The default returns an empty list so the scaffold runs cleanly even
    before a data source is wired up.
    """
    return []
