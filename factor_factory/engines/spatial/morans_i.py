"""Moran's I global + local spatial-autocorrelation via ``esda``.

References
----------
Moran, P. A. P. (1950). Notes on continuous stochastic phenomena.
*Biometrika*, 37(1/2), 17-23.

Anselin, L. (1995). Local indicators of spatial association — LISA.
*Geographical Analysis*, 27(2), 93-115.
"""

from __future__ import annotations

from typing import Any

from ...tidy.panel import Panel
from ._base import SpatialResult


class MoransIEngine:
    """Global + local Moran's I via esda."""

    name = "morans_i"

    def fit(
        self,
        panel: Panel,
        *,
        outcome: str,
        coordinates: tuple[str, str] = ("latitude", "longitude"),
        k_neighbors: int = 5,
        **_engine_specific_kwargs: Any,
    ) -> SpatialResult:
        try:
            import esda
            from libpysal.weights import KNN
        except ImportError as exc:  # pragma: no cover
            raise ImportError(
                "MoransIEngine requires `esda` + `libpysal`. Install via "
                "`pip install factor-factory[spatial]`."
            ) from exc

        df = panel.df.reset_index()
        # For a multi-period panel, collapse to unit-level means.
        agg = (
            df.groupby("unit_id")
            .agg({outcome: "mean", coordinates[0]: "first", coordinates[1]: "first"})
            .reset_index()
        )

        coords = list(zip(agg[coordinates[0]], agg[coordinates[1]], strict=True))
        w = KNN.from_array(coords, k=k_neighbors)
        w.transform = "r"

        y = agg[outcome].to_numpy(dtype=float)
        moran = esda.Moran(y, w, permutations=999)

        return SpatialResult(
            method=self.name,
            statistic=float(moran.I),
            p_value=float(moran.p_sim),
            z_score=float(moran.z_sim),
            local_statistics=None,
            n_units=int(len(y)),
            weights_type=f"KNN(k={k_neighbors})",
            diagnostics={"permutations": 999, "upstream": "esda.Moran"},
        )
