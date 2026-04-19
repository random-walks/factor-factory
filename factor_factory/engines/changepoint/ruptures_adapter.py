"""Offline changepoint detection via ``ruptures``.

References
----------
Truong, C., Oudre, L., & Vayatis, N. (2020). Selective review of
offline change point detection methods. *Signal Processing*, 167,
107299.

Reference implementation: https://centre-borelli.github.io/ruptures-docs/
"""

from __future__ import annotations

from typing import Any

import numpy as np

from ...tidy.panel import Panel
from ._base import ChangepointResult


class RupturesEngine:
    """Offline changepoint detection via ruptures."""

    name = "ruptures"

    def fit(
        self,
        panel: Panel,
        *,
        outcome: str,
        model: str = "l2",
        algorithm: str = "pelt",
        penalty: float = 10.0,
        n_breaks: int | None = None,
        **_engine_specific_kwargs: Any,
    ) -> ChangepointResult:
        try:
            import ruptures as rpt
        except ImportError as exc:  # pragma: no cover
            raise ImportError(
                "RupturesEngine requires the `ruptures` package. "
                "Install via `pip install factor-factory[changepoint]`."
            ) from exc

        # Aggregate across units if multi-unit panel (take mean over units per period).
        df = panel.df.reset_index()
        y = df.groupby("period")[outcome].mean().to_numpy(dtype=float)

        algo_cls = {"pelt": rpt.Pelt, "binseg": rpt.Binseg, "window": rpt.Window}.get(
            algorithm, rpt.Pelt
        )
        algo = algo_cls(model=model).fit(y)
        if n_breaks is not None:
            breaks = algo.predict(n_bkps=n_breaks)
        else:
            breaks = algo.predict(pen=penalty)

        # ruptures' .predict() returns [..., len(y)] — strip the end marker.
        changepoints = [int(b) for b in breaks[:-1]]

        # Regime means.
        regime_means: list[float] = []
        start = 0
        for end in changepoints + [len(y)]:
            regime_means.append(float(np.mean(y[start:end])))
            start = end

        return ChangepointResult(
            method=self.name,
            changepoints=changepoints,
            regime_means=regime_means,
            n_regimes=len(regime_means),
            model=model,
            penalty=penalty if n_breaks is None else None,
            confidence=None,
            diagnostics={"algorithm": algorithm, "n_series_points": int(len(y))},
        )
