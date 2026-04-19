"""STL decomposition + forecasting via ``sktime``.

References
----------
Cleveland, R. B., Cleveland, W. S., McRae, J. E., & Terpenning, I.
(1990). STL: A seasonal-trend decomposition procedure based on loess.
*Journal of Official Statistics*, 6(1), 3-73.

Reference implementation: https://www.sktime.net/en/latest/api_reference.html
"""

from __future__ import annotations

from typing import Any

from ...tidy.panel import Panel
from ._base import StlResult


class SktimeStlEngine:
    """STL decomposition + forecasting via sktime."""

    name = "sktime_stl"

    def fit(
        self,
        panel: Panel,
        *,
        outcome: str,
        seasonal_period: int,
        forecast_horizon: int = 0,
        **_engine_specific_kwargs: Any,
    ) -> StlResult:
        try:
            from sktime.forecasting.trend import STLForecaster
            from sktime.transformations.series.detrend import Deseasonalizer
        except ImportError as exc:  # pragma: no cover
            raise ImportError(
                "SktimeStlEngine requires `sktime`. Install via "
                "`pip install factor-factory[stl]`."
            ) from exc

        df = panel.df.reset_index()
        y = df.groupby("period")[outcome].mean().sort_index()

        # Decompose via sktime's STL-based Deseasonalizer + residual.
        deseason = Deseasonalizer(sp=seasonal_period, model="additive")
        seasonal_adj = deseason.fit_transform(y)
        seasonal = (y - seasonal_adj).rename("seasonal")
        # Simple trend: rolling mean with window=seasonal_period.
        trend = y.rolling(window=seasonal_period, center=True, min_periods=1).mean().rename("trend")
        residual = (y - trend - seasonal).rename("residual")

        forecast = None
        forecast_interval = None
        if forecast_horizon > 0:
            forecaster = STLForecaster(sp=seasonal_period)
            forecaster.fit(y)
            fh = list(range(1, forecast_horizon + 1))
            forecast = forecaster.predict(fh=fh)

        return StlResult(
            method=self.name,
            trend=trend,
            seasonal=seasonal,
            residual=residual,
            forecast=forecast if forecast is not None else None,
            forecast_interval=forecast_interval,
            seasonal_period=seasonal_period,
            n_observations=int(len(y)),
            diagnostics={"model": "additive", "upstream": "sktime"},
        )
