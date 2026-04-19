"""Two-way fixed-effects DiD adapter via ``linearmodels.PanelOLS``.

The TWFE estimator is the workhorse single-engine baseline. With
two-way FE and clustered SEs it recovers the canonical DiD coefficient
in the no-staggered-rollout case (and the negative-weights average in
the staggered-rollout case — see Goodman-Bacon 2021 for caveats).
"""

from __future__ import annotations

from typing import Any

from ...tidy.panel import Panel
from ._base import DidResult


class TwfeEngine:
    """Two-way fixed-effects DiD via ``linearmodels.PanelOLS``.

    Citation: Wooldridge 2010 (Econometric Analysis of Cross Section
    and Panel Data, ch. 10) — the canonical TWFE write-up.
    """

    name = "twfe"

    def fit(
        self,
        panel: Panel,
        *,
        outcome: str,
        treatment: str = "treatment",
        cluster: str | None = None,
        **_engine_specific_kwargs: Any,
    ) -> DidResult:
        try:
            from linearmodels.panel import PanelOLS
        except ImportError as exc:  # pragma: no cover
            raise ImportError(
                "TwfeEngine requires the `linearmodels` package. "
                "Install via `pip install factor-factory[did]`."
            ) from exc

        df = panel.df
        if outcome not in df.columns:
            raise ValueError(f"Panel missing outcome column '{outcome}'.")
        if treatment not in df.columns:
            raise ValueError(
                f"Panel missing treatment column '{treatment}'. "
                "Build the panel with treatment_events= or pre-compute the column."
            )

        y = df[[outcome]]
        x = df[[treatment]]

        if cluster is not None:
            cov_kwargs: dict[str, Any] = {
                "cov_type": "clustered",
                "cluster_entity": True,
            }
        else:
            cov_kwargs = {"cov_type": "robust"}

        model = PanelOLS(y, x, entity_effects=True, time_effects=True)
        result = model.fit(**cov_kwargs)

        att = float(result.params[treatment])
        se = float(result.std_errors[treatment])
        ci = result.conf_int().loc[treatment]
        # linearmodels uses 'lower'/'upper' column names
        lo = float(ci.iloc[0])
        hi = float(ci.iloc[1])
        p = float(result.pvalues[treatment])
        n = int(result.nobs)

        return DidResult(
            method=self.name,
            att=att,
            se=se,
            ci_95=(lo, hi),
            p_value=p,
            n=n,
            diagnostics={
                "r_squared": float(result.rsquared),
                "r_squared_within": float(result.rsquared_within),
            },
            meta={"raw_summary": str(result.summary)},
        )
