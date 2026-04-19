"""Geographic boundary loading + centroid + distance helpers.

Phase-1 scope: a domain-agnostic ``BoundaryCollection`` data type, an
adapter registry, and pairwise haversine distance. The default
``"nyc_geo_toolkit"`` source is a shim — it raises ``ImportError``
until the upstream package is available. Downstream packages (or
tests) register their own boundary sources.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from .record_view import _haversine_km


@dataclass(frozen=True)
class BoundaryFeature:
    """A single geographic feature (polygon or multipolygon)."""

    geography_value: str
    geometry: dict[str, Any]  # GeoJSON-style; convert with shapely.shape() as needed
    properties: dict[str, Any] | None = None


@dataclass(frozen=True)
class BoundaryCollection:
    """A collection of features for a named geographic layer."""

    features: tuple[BoundaryFeature, ...]
    geography: str
    source: str

    def __iter__(self) -> Iterable[BoundaryFeature]:
        return iter(self.features)

    def __len__(self) -> int:
        return len(self.features)


# ─── adapter registry ──────────────────────────────────────────────────────

BoundarySourceAdapter = Callable[[str], BoundaryCollection]
_SOURCES: dict[str, BoundarySourceAdapter] = {}


def register_boundary_source(name: str, adapter: BoundarySourceAdapter) -> None:
    """Register a callable that maps ``layer -> BoundaryCollection``."""
    _SOURCES[name] = adapter


def _nyc_geo_toolkit_adapter(layer: str) -> BoundaryCollection:
    try:
        import nyc_geo_toolkit  # type: ignore[import-not-found]
    except ImportError as exc:  # pragma: no cover - tested by absence
        raise ImportError(
            "load_boundaries(source='nyc_geo_toolkit') requires the "
            "nyc-geo-toolkit package. Install it or pass a different `source` "
            "(see factor_factory.tidy.geography.register_boundary_source)."
        ) from exc

    return nyc_geo_toolkit.load_layer(layer)  # type: ignore[no-any-return]


register_boundary_source("nyc_geo_toolkit", _nyc_geo_toolkit_adapter)


# ─── public API ────────────────────────────────────────────────────────────


def load_boundaries(layer: str, *, source: str = "nyc_geo_toolkit") -> BoundaryCollection:
    """Load a named geographic boundary layer via the registered source."""
    if source not in _SOURCES:
        raise KeyError(
            f"Unknown boundary source '{source}'. "
            f"Available: {sorted(_SOURCES)}. "
            "Register one via factor_factory.tidy.geography.register_boundary_source."
        )
    return _SOURCES[source](layer)


def centroids_from_boundaries(
    collection: BoundaryCollection,
) -> dict[str, tuple[float, float]]:
    """Extract ``(lon, lat)`` centroids keyed by ``geography_value``.

    Uses shapely's representative point for stability with multipolygons.
    """
    from shapely.geometry import shape

    out: dict[str, tuple[float, float]] = {}
    for feat in collection.features:
        geom = shape(feat.geometry)
        c = geom.centroid
        out[feat.geography_value] = (float(c.x), float(c.y))
    return out


def distance_matrix(centroids: dict[str, tuple[float, float]]) -> pd.DataFrame:
    """Pairwise haversine distance in kilometers; symmetric DataFrame."""
    if not centroids:
        return pd.DataFrame()

    units = sorted(centroids)
    coords = np.array([centroids[u] for u in units], dtype=float)  # (n, 2): lon, lat
    n = len(units)
    out = np.zeros((n, n), dtype=float)
    for i in range(n):
        out[i] = _haversine_km(coords[:, 0], coords[:, 1], coords[i, 0], coords[i, 1])
    df = pd.DataFrame(out, index=units, columns=units)
    df.index.name = "unit_id"
    df.columns.name = "unit_id"
    return df
