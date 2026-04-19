"""Market-adjusted abnormal-return estimator (no benchmark column required).

The simplest event-study spec: AR_it = r_it - r_market_t, where
r_market_t is the cross-sectional average return of *non-treated*
units in period t. This avoids needing an external benchmark column
and is appropriate when the panel itself contains a control group.

For the proper Fama-French / CAPM market-model variant with an
explicit benchmark column, use ``MarketModelEngine`` instead.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

from ...tidy.panel import Panel
from ._base import EventStudyResult


class MarketAdjustedEngine:
    """Market-adjusted abnormal returns using never-treated units as benchmark."""

    name = "market_adjusted"

    def fit(
        self,
        panel: Panel,
        *,
        outcome: str,
        market_col: str | None = None,
        estimation_window: tuple[int, int] = (-120, -20),  # unused for this method
        event_window: tuple[int, int] = (-1, 1),
        **_engine_specific_kwargs: Any,
    ) -> EventStudyResult:
        if not panel.treatment_events:
            raise ValueError(
                "MarketAdjustedEngine requires panel.treatment_events to identify event dates."
            )

        df = panel.df
        if outcome not in df.columns:
            raise ValueError(f"Panel missing outcome column {outcome!r}.")

        # Build benchmark: cross-sectional average of "treated_unit==0" rows per period
        if "treated_unit" not in df.columns:
            raise ValueError(
                "MarketAdjustedEngine needs the 'treated_unit' aggregate column "
                "(produced automatically by Panel.from_records when "
                "treatment_events are passed)."
            )
        controls = df[df["treated_unit"] == 0]
        if controls.empty:
            raise ValueError(
                "MarketAdjustedEngine needs untreated units as the benchmark; "
                "all units are treated in this panel."
            )
        benchmark_per_period = controls.groupby(level="period")[outcome].mean()

        # For each treated unit + each event the unit belongs to, compute event-time AR
        ar_records: list[dict[str, Any]] = []
        per_unit_car: dict[str, float] = {}
        n_events = 0
        for ev in panel.treatment_events:
            if ev.treatment_date is None:
                continue  # only time-anchored events supported
            anchor = pd.Timestamp(ev.treatment_date)
            n_events += 1
            for unit in ev.treated_units:
                if unit not in df.index.get_level_values("unit_id"):
                    continue
                unit_returns = df.xs(unit, level="unit_id")[outcome]
                # event-time index: # of periods between observation and event date
                period_index: pd.DatetimeIndex = unit_returns.index  # type: ignore[assignment]
                event_time = (period_index - anchor).days
                window_mask = (event_time >= event_window[0]) & (event_time <= event_window[1])
                if not window_mask.any():
                    continue
                window_returns = unit_returns[window_mask]
                window_benchmark = benchmark_per_period.reindex(window_returns.index)
                ar = window_returns - window_benchmark
                car = float(ar.sum())
                per_unit_car[str(unit)] = per_unit_car.get(str(unit), 0.0) + car
                for et, ar_val in zip(event_time[window_mask], ar.to_numpy(), strict=True):
                    ar_records.append({"event_time": int(et), "ar": float(ar_val), "unit": unit})

        if not ar_records:
            raise ValueError(
                "No event-window observations found. Check that event dates fall "
                "inside the panel's date range."
            )

        ar_df = pd.DataFrame(ar_records)
        # AR averaged across units per event-time
        avg_ar_by_et = ar_df.groupby("event_time")["ar"].mean()
        ar_curve = pd.DataFrame(
            {
                "event_time": avg_ar_by_et.index.astype(int),
                "average_ar": avg_ar_by_et.to_numpy(),
            }
        )

        # Test statistic: average CAR across units, t-test against 0
        car_per_unit = np.array(list(per_unit_car.values()))
        car_mean = float(car_per_unit.mean())
        car_se = float(car_per_unit.std(ddof=1) / np.sqrt(len(car_per_unit)))
        if car_se > 0:
            t_stat = float(car_mean / car_se)
            p_value = float(2.0 * (1.0 - stats.t.cdf(abs(t_stat), df=len(car_per_unit) - 1)))
        else:
            t_stat = float("nan")
            p_value = 1.0

        # Single-day AR at event_time == 0
        zero_day = avg_ar_by_et.get(0, float("nan"))

        return EventStudyResult(
            method=self.name,
            n_events=int(len(per_unit_car)),
            average_abnormal_return=float(zero_day) if pd.notna(zero_day) else float("nan"),
            car_event_window=car_mean,
            car_se=car_se,
            car_t_stat=t_stat,
            car_p_value=p_value,
            abnormal_return_curve=ar_curve,
            per_unit_car={k: float(v) for k, v in per_unit_car.items()},
            estimation_window=estimation_window,
            event_window=event_window,
            diagnostics={
                "n_units_with_event_obs": int(len(per_unit_car)),
                "benchmark_method": "cross-sectional mean of never-treated units",
            },
        )
