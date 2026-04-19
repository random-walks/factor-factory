"""Per-record companion view that retains lat/lon for record-level analyses."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, replace
from datetime import date
from math import asin, cos, radians, sin, sqrt

import numpy as np
import pandas as pd
from numpy.typing import NDArray

_EARTH_KM = 6371.0


@dataclass(frozen=True)
class RecordView:
    """Per-record DataFrame retaining lat/lon, period, unit_id.

    Required for record-level RDD via rdrobust and within-unit spatial
    heterogeneity analysis. Built by ``Panel.from_records`` when
    ``record_view=True``.
    """

    df: pd.DataFrame  # required columns: latitude, longitude, unit_id, period
    schema_version: int = 1

    REQUIRED_COLUMNS = ("latitude", "longitude", "unit_id", "period")

    def __post_init__(self) -> None:
        missing = [c for c in self.REQUIRED_COLUMNS if c not in self.df.columns]
        if missing:
            raise ValueError(
                f"RecordView missing required columns: {missing}. Got {list(self.df.columns)}."
            )

    def filter(
        self,
        *,
        period_start: date | pd.Timestamp | None = None,
        period_end: date | pd.Timestamp | None = None,
        unit_ids: tuple[str, ...] | None = None,
    ) -> RecordView:
        """Sub-select records by period range or unit ID set."""
        df = self.df
        if period_start is not None:
            df = df[df["period"] >= pd.Timestamp(period_start)]
        if period_end is not None:
            df = df[df["period"] <= pd.Timestamp(period_end)]
        if unit_ids is not None:
            df = df[df["unit_id"].isin(unit_ids)]
        return replace(self, df=df.reset_index(drop=True))

    def distance_to_point(self, lon: float, lat: float) -> pd.Series:
        """Haversine distance in km from each record to a single point."""
        rec_lat = self.df["latitude"].astype(float).to_numpy()
        rec_lon = self.df["longitude"].astype(float).to_numpy()
        return pd.Series(
            _haversine_km(rec_lon, rec_lat, lon, lat),
            index=self.df.index,
            name="distance_km",
        )


def _haversine_km(
    lon1: NDArray[np.floating] | Sequence[float],
    lat1: NDArray[np.floating] | Sequence[float],
    lon2: float,
    lat2: float,
) -> NDArray[np.floating]:
    """Vectorized haversine distance in kilometers (one point vs. many)."""
    lon1_r = np.radians(np.asarray(lon1, dtype=float))
    lat1_r = np.radians(np.asarray(lat1, dtype=float))
    lon2_r = radians(float(lon2))
    lat2_r = radians(float(lat2))
    dlon = lon2_r - lon1_r
    dlat = lat2_r - lat1_r
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1_r) * cos(lat2_r) * np.sin(dlon / 2) ** 2
    out: NDArray[np.floating] = 2 * _EARTH_KM * np.arcsin(np.sqrt(a))
    return out


def _scalar_haversine_km(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    lon1_r, lat1_r, lon2_r, lat2_r = (radians(v) for v in (lon1, lat1, lon2, lat2))
    dlon = lon2_r - lon1_r
    dlat = lat2_r - lat1_r
    a = sin(dlat / 2) ** 2 + cos(lat1_r) * cos(lat2_r) * sin(dlon / 2) ** 2
    return 2 * _EARTH_KM * asin(sqrt(a))
