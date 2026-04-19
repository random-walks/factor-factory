"""Partially-linear-regression DoubleML adapter.

Wraps ``doubleml.DoubleMLPLR``. PLR structure: Y = D·theta + g(X) + ε,
D = m(X) + u. theta is the treatment effect; g and m are fit via
cross-fit ML.

References
----------
Chernozhukov, V., Chetverikov, D., Demirer, M., Duflo, E., Hansen, C.,
Newey, W., & Robins, J. (2018). Double/debiased machine learning for
treatment and structural parameters. *The Econometrics Journal*,
21(1), C1-C68. https://doi.org/10.1111/ectj.12097
"""

from __future__ import annotations

from typing import Any

from ...tidy.panel import Panel
from ._base import DmlResult


class DmlPlrEngine:
    """DoubleML partially-linear-regression estimator."""

    name = "plr"

    def fit(
        self,
        panel: Panel,
        *,
        outcome: str,
        treatment: str = "treatment",
        covariates: tuple[str, ...] = (),
        n_folds: int = 5,
        score: str = "partialling out",
        **_engine_specific_kwargs: Any,
    ) -> DmlResult:
        try:
            from doubleml import DoubleMLData, DoubleMLPLR
            from sklearn.ensemble import RandomForestRegressor
        except ImportError as exc:  # pragma: no cover
            raise ImportError(
                "DmlPlrEngine requires the `DoubleML` package. "
                "Install via `pip install factor-factory[dml]`."
            ) from exc

        if not covariates:
            raise ValueError("DmlPlrEngine requires at least one covariate.")

        df = panel.df.reset_index()
        data = DoubleMLData(
            df,
            y_col=outcome,
            d_cols=treatment,
            x_cols=list(covariates),
        )
        est = DoubleMLPLR(
            obj_dml_data=data,
            ml_l=RandomForestRegressor(n_estimators=100, random_state=42),
            ml_m=RandomForestRegressor(n_estimators=100, random_state=42),
            n_folds=n_folds,
            score=score,
        )
        est.fit()

        coef = float(est.coef[0])
        se = float(est.se[0])
        t_stat = float(est.t_stat[0])
        p_value = float(est.pval[0])
        ci = est.confint()
        ci_lo = float(ci.iloc[0, 0])
        ci_hi = float(ci.iloc[0, 1])

        return DmlResult(
            method=self.name,
            coef=coef,
            std_error=se,
            t_stat=t_stat,
            p_value=p_value,
            ci_95=(ci_lo, ci_hi),
            n_units=int(len(df)),
            n_folds=n_folds,
            diagnostics={"score": score, "upstream": "doubleml.DoubleMLPLR"},
        )
