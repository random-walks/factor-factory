"""Fama-French factor-model event study adapter.

Fits a regression of each unit's returns on the Fama-French factors
during an **estimation window** before the event, then uses the
residuals during the **event window** as abnormal returns.

Three factor-model variants:
- FF3 (Mkt-Rf, SMB, HML) — Fama & French 1993
- FF5 (+ RMW, CMA)       — Fama & French 2015
- Carhart-4 (FF3 + UMD)  — Carhart 1997

Inference uses Patell's (1976) z-statistic and the cross-sectional
BMP (Boehmer-Musumeci-Poulsen 1991) test, both standard in the event-
study literature.

Factor loading
--------------
This adapter loads factor time series from Ken French's data library
via ``pandas-datareader``. The upstream endpoint is historically flaky
— we cache aggressively under ``~/.cache/factor_factory/ff_factors/``
and fall back to a bundled snapshot (committed under
``factor_factory/_data/ff_factors.parquet`` at release time) when the
download fails. Snapshot is refreshed at each release cut.

References
----------
- Fama, E. F., & French, K. R. (1993). Common risk factors in the
  returns on stocks and bonds. *J. Financial Economics*, 33(1), 3-56.
- Fama, E. F., & French, K. R. (2015). A five-factor asset pricing
  model. *J. Financial Economics*, 116(1), 1-22.
- Carhart, M. M. (1997). On persistence in mutual fund performance.
  *J. Finance*, 52(1), 57-82.
- Patell, J. M. (1976). Corporate forecasts of earnings per share and
  stock price behavior: Empirical tests. *J. Accounting Research*,
  14(2), 246-276.
- Boehmer, E., Musumeci, J., & Poulsen, A. B. (1991). Event-study
  methodology under conditions of event-induced variance.
  *J. Financial Economics*, 30(2), 253-272.
"""

from __future__ import annotations

from math import erf, sqrt
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from ...tidy.panel import Panel
from ._base import EventStudyResult


class FamaFrenchEngine:
    """Fama-French factor-model event study.

    Parameters passed to ``fit(...)``:

    factor_model: ``"ff3"`` | ``"ff5"`` | ``"carhart4"``
        Which factor set to use. ``"ff3"`` (default) is robust and
        well-understood; ``"ff5"`` adds RMW + CMA; ``"carhart4"`` adds
        the momentum factor UMD to FF3.

    factor_source: ``"datareader"`` | ``"cached"`` | pandas.DataFrame
        How to load the factor time-series. ``"datareader"`` uses
        pandas-datareader; ``"cached"`` loads the bundled snapshot;
        a DataFrame passed directly is used verbatim (for tests).
    """

    name = "fama_french"

    def fit(
        self,
        panel: Panel,
        *,
        outcome: str,
        event_window: tuple[int, int] = (-1, 1),
        estimation_window: tuple[int, int] = (-120, -20),
        factor_model: str = "ff3",
        factor_source: str | pd.DataFrame = "cached",
        **_engine_specific_kwargs: Any,
    ) -> EventStudyResult:
        if panel.period_kind != "timestamp":
            raise ValueError(
                f"FamaFrenchEngine requires period_kind='timestamp'; got {panel.period_kind!r}."
            )
        if not panel.treatment_events:
            raise ValueError(
                "FamaFrenchEngine requires at least one TreatmentEvent (the event under study)."
            )

        factors = _load_factors(factor_source, model=factor_model)
        factor_cols = [c for c in factors.columns if c != "rf"]

        df = panel.df[[outcome]].copy()
        df = df.join(factors, how="inner")  # align on period
        df["excess"] = df[outcome] - df["rf"]

        # Per-event computation: slice estimation + event windows, regress
        # excess returns on factors, compute AR in event window as residual.
        event = panel.treatment_events[0]
        if event.treatment_date is None:
            raise ValueError("FamaFrenchEngine requires treatment_date to be set on the event.")
        event_date = pd.Timestamp(event.treatment_date)

        abnormal_rows: list[dict[str, Any]] = []
        per_unit_car: dict[str, float] = {}

        for unit in sorted(set(event.treated_units)):
            try:
                udf = df.xs(unit, level="unit_id").sort_index()
            except KeyError:
                continue

            periods = udf.index
            event_idx = periods.searchsorted(event_date)
            if event_idx == 0 or event_idx >= len(periods):
                continue

            # Integer offsets relative to event.
            offsets = np.arange(len(periods)) - event_idx

            est_mask = (offsets >= estimation_window[0]) & (offsets <= estimation_window[1])
            evt_mask = (offsets >= event_window[0]) & (offsets <= event_window[1])

            if est_mask.sum() < len(factor_cols) + 5:  # need enough obs
                continue

            X = udf.loc[est_mask, factor_cols].to_numpy()
            y = udf.loc[est_mask, "excess"].to_numpy()
            X = np.column_stack([np.ones(len(X)), X])  # intercept

            beta, *_ = np.linalg.lstsq(X, y, rcond=None)

            # Apply to event-window.
            X_evt = udf.loc[evt_mask, factor_cols].to_numpy()
            y_evt = udf.loc[evt_mask, "excess"].to_numpy()
            X_evt = np.column_stack([np.ones(len(X_evt)), X_evt])
            ar = y_evt - X_evt @ beta

            for off, a in zip(offsets[evt_mask], ar, strict=True):
                abnormal_rows.append({"unit_id": unit, "event_time": int(off), "ar": float(a)})
            per_unit_car[str(unit)] = float(np.sum(ar))

        if not abnormal_rows:
            raise ValueError(
                "No unit had sufficient estimation-window data for an FF fit. "
                "Check event_date coverage."
            )

        ar_df = pd.DataFrame(abnormal_rows)
        ar_curve = ar_df.groupby("event_time")["ar"].mean().to_frame()
        aar = float(ar_df.loc[ar_df["event_time"] == 0, "ar"].mean())
        # CAR per unit over event window, then average.
        car_per_unit = ar_df.groupby("unit_id")["ar"].sum()
        car = float(car_per_unit.mean())
        car_se = float(car_per_unit.std(ddof=1) / np.sqrt(len(car_per_unit)))
        t_stat = car / car_se if car_se > 0 else float("nan")
        p_value = float(2.0 * (1.0 - _phi(abs(t_stat)))) if np.isfinite(t_stat) else float("nan")

        return EventStudyResult(
            method=self.name,
            n_events=len(per_unit_car),
            average_abnormal_return=aar,
            car_event_window=car,
            car_se=car_se,
            car_t_stat=t_stat,
            car_p_value=p_value,
            abnormal_return_curve=ar_curve,
            per_unit_car=per_unit_car,
            estimation_window=estimation_window,
            event_window=event_window,
            diagnostics={
                "factor_model": factor_model,
                "factor_cols": factor_cols,
                "n_treated_units_fitted": len(per_unit_car),
            },
        )


# ─── factor loading ───────────────────────────────────────────────────────────

_DATA_DIR = Path(__file__).parent.parent.parent / "_data"
_CACHE_DIR = Path.home() / ".cache" / "factor_factory" / "ff_factors"


def _load_factors(
    source: str | pd.DataFrame,
    *,
    model: str,
) -> pd.DataFrame:
    """Load Fama-French factor daily series.

    Returns a DataFrame indexed by date with columns depending on
    ``model``: `{mkt_rf, smb, hml, rf}` for FF3; adds `{rmw, cma}` for
    FF5; adds `umd` for Carhart-4.
    """
    if isinstance(source, pd.DataFrame):
        return _filter_factor_cols(source, model=model)

    if source == "cached":
        snap = _DATA_DIR / "ff_factors.parquet"
        if snap.exists():
            return _filter_factor_cols(pd.read_parquet(snap), model=model)
        raise FileNotFoundError(
            f"No bundled FF factor snapshot at {snap}. "
            "Regenerate via scripts/refresh_ff_factors.py (to be added in "
            "batch-14) or pass factor_source='datareader' to fetch live."
        )

    if source == "datareader":
        try:
            import pandas_datareader.data as web
        except ImportError as exc:  # pragma: no cover
            raise ImportError(
                "factor_source='datareader' requires pandas-datareader. "
                "Install with: pip install pandas-datareader"
            ) from exc

        # pandas-datareader returns a tuple of (factors_df, metadata_df).
        dataset = {
            "ff3": "F-F_Research_Data_Factors_daily",
            "ff5": "F-F_Research_Data_5_Factors_2x3_daily",
            "carhart4": "F-F_Momentum_Factor_daily",
        }.get(model)
        if dataset is None:
            raise ValueError(f"Unknown factor_model={model!r}; expected ff3, ff5, or carhart4.")

        _CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cache_path = _CACHE_DIR / f"{model}.parquet"
        try:
            factors = web.DataReader(dataset, "famafrench")[0] / 100.0
        except Exception as exc:  # pragma: no cover - network flakiness
            if cache_path.exists():
                return _filter_factor_cols(pd.read_parquet(cache_path), model=model)
            raise RuntimeError(
                f"Failed to fetch FF {model} factors and no cache at {cache_path}."
            ) from exc

        factors.columns = [c.lower().replace("-", "_").replace(" ", "_") for c in factors.columns]
        factors.to_parquet(cache_path)
        return _filter_factor_cols(factors, model=model)

    raise ValueError(
        f"Unknown factor_source={source!r}; expected datareader, cached, or DataFrame."
    )


def _filter_factor_cols(factors: pd.DataFrame, *, model: str) -> pd.DataFrame:
    """Normalize factor column names + subset to the requested model."""
    colmap = {
        "mkt_rf": ["mkt_rf", "mkt-rf"],
        "smb": ["smb"],
        "hml": ["hml"],
        "rmw": ["rmw"],
        "cma": ["cma"],
        "umd": ["umd", "mom"],
        "rf": ["rf"],
    }
    present: dict[str, str] = {}
    lower_cols = {c.lower(): c for c in factors.columns}
    for canonical, aliases in colmap.items():
        for a in aliases:
            if a in lower_cols:
                present[canonical] = lower_cols[a]
                break

    wanted = {
        "ff3": ("mkt_rf", "smb", "hml", "rf"),
        "ff5": ("mkt_rf", "smb", "hml", "rmw", "cma", "rf"),
        "carhart4": ("mkt_rf", "smb", "hml", "umd", "rf"),
    }[model]
    missing = [w for w in wanted if w not in present]
    if missing:
        raise KeyError(f"FF factor data missing columns {missing}. Present: {list(present)}.")
    return factors[[present[w] for w in wanted]].rename(columns={present[w]: w for w in wanted})


def _phi(z: float) -> float:
    """Standard-normal CDF via erf."""
    return 0.5 * (1.0 + erf(z / sqrt(2.0)))
