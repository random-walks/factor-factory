"""Per-record companion view for record-level analyses.

A ``RecordView`` is a flat per-record DataFrame that lives alongside
the aggregated ``Panel``. Required columns: ``unit_id`` and ``period``
(matching the parent panel). Beyond that, any per-record columns are
allowed: lat/lon for spatial / RDD analyses, clinical covariates for
patient-level work, asset-level metadata for finance, etc.

Geographic convenience: when ``latitude`` and ``longitude`` columns
are present, ``distance_to_point()`` returns the haversine distance
from each record to a target lon/lat — useful as the running variable
for record-level RDD via rdrobust.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, replace
from datetime import date
from math import asin, cos, radians, sin, sqrt
from typing import Any

import numpy as np
import pandas as pd
from numpy.typing import NDArray

_EARTH_KM = 6371.0


@dataclass(frozen=True)
class RecordView:
    """Per-record DataFrame retaining ``(unit_id, period)`` plus arbitrary extras.

    Required columns: ``unit_id``, ``period``. Conventional optional
    columns include ``latitude`` / ``longitude`` (for spatial work)
    but any extras are allowed.
    """

    df: pd.DataFrame
    schema_version: int = 1

    REQUIRED_COLUMNS = ("unit_id", "period")

    def __post_init__(self) -> None:
        missing = [c for c in self.REQUIRED_COLUMNS if c not in self.df.columns]
        if missing:
            raise ValueError(
                f"RecordView missing required columns: {missing}. Got {list(self.df.columns)}."
            )

    @property
    def has_latlon(self) -> bool:
        return "latitude" in self.df.columns and "longitude" in self.df.columns

    def filter(
        self,
        *,
        period_start: date | pd.Timestamp | int | float | None = None,
        period_end: date | pd.Timestamp | int | float | None = None,
        unit_ids: tuple[Any, ...] | None = None,
    ) -> RecordView:
        """Sub-select records by period range or unit ID set."""
        df = self.df
        if period_start is not None:
            anchor = pd.Timestamp(period_start) if isinstance(period_start, date) else period_start
            df = df[df["period"] >= anchor]
        if period_end is not None:
            anchor = pd.Timestamp(period_end) if isinstance(period_end, date) else period_end
            df = df[df["period"] <= anchor]
        if unit_ids is not None:
            df = df[df["unit_id"].isin(unit_ids)]
        return replace(self, df=df.reset_index(drop=True))

    def distance_to_point(self, lon: float, lat: float) -> pd.Series:
        """Haversine distance in km from each record to a single point.

        Requires ``latitude`` and ``longitude`` columns; raises ``ValueError``
        otherwise.
        """
        if not self.has_latlon:
            raise ValueError(
                "distance_to_point requires latitude + longitude columns on "
                f"the RecordView. Got: {list(self.df.columns)}."
            )
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
