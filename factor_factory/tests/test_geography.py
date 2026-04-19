"""Tests for geography helpers."""

from __future__ import annotations

import pandas as pd

from factor_factory.tidy.geography import (
    BoundaryCollection,
    BoundaryFeature,
    centroids_from_boundaries,
    distance_matrix,
)


def _square(lon0: float, lat0: float, side: float = 0.01) -> dict:
    return {
        "type": "Polygon",
        "coordinates": [
            [
                [lon0, lat0],
                [lon0 + side, lat0],
                [lon0 + side, lat0 + side],
                [lon0, lat0 + side],
                [lon0, lat0],
            ]
        ],
    }


def test_centroids_from_boundaries_basic() -> None:
    coll = BoundaryCollection(
        features=(
            BoundaryFeature(geography_value="A", geometry=_square(-74.0, 40.7)),
            BoundaryFeature(geography_value="B", geometry=_square(-73.9, 40.7)),
        ),
        geography="cd",
        source="test",
    )
    centroids = centroids_from_boundaries(coll)
    assert set(centroids) == {"A", "B"}
    assert abs(centroids["A"][0] - (-74.0 + 0.005)) < 1e-9


def test_distance_matrix_symmetric() -> None:
    centroids = {
        "A": (-74.0, 40.7),
        "B": (-73.9, 40.7),
        "C": (-74.0, 40.8),
    }
    dm = distance_matrix(centroids)
    assert dm.shape == (3, 3)
    assert dm.loc["A", "A"] == 0.0
    assert dm.loc["A", "B"] == dm.loc["B", "A"]
    # ~0.1 deg lon at lat 40.7 is roughly 8.4 km
    assert 7.0 < dm.loc["A", "B"] < 10.0


def test_distance_matrix_empty() -> None:
    out = distance_matrix({})
    assert isinstance(out, pd.DataFrame)
    assert out.empty
