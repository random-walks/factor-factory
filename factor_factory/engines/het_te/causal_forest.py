"""Causal Forest via ``econml.dml.CausalForestDML``.

References
----------
- Wager, S., & Athey, S. (2018). Estimation and inference of
  heterogeneous treatment effects using random forests. *JASA*,
  113(523), 1228-1242.
- Athey, S., Tibshirani, J., & Wager, S. (2019). Generalized random
  forests. *Annals of Statistics*, 47(2), 1148-1178.

Reference implementation: ``econml.dml.CausalForestDML`` from
Microsoft's EconML package (https://econml.azurewebsites.net).
"""

from __future__ import annotations

from typing import Any

import numpy as np

from ...tidy.panel import Panel
from ._base import HetTeResult


class CausalForestEngine:
    """Causal Forest heterogeneous-effects estimator."""

    name = "causal_forest"

    def fit(
        self,
        panel: Panel,
        *,
        outcome: str,
        treatment: str = "treatment",
        covariates: tuple[str, ...] = (),
        discrete_treatment: bool = True,
        n_estimators: int = 200,
        min_samples_leaf: int = 10,
        random_state: int = 42,
        **_engine_specific_kwargs: Any,
    ) -> HetTeResult:
        try:
            from econml.dml import CausalForestDML
            from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
        except ImportError as exc:  # pragma: no cover
            raise ImportError(
                "CausalForestEngine requires the `econml` package. "
                "Install via `pip install factor-factory[het-te]`."
            ) from exc

        if not covariates:
            raise ValueError(
                "CausalForestEngine requires at least one covariate (CATE features)."
            )

        df = panel.df.reset_index()
        Y = df[outcome].to_numpy(dtype=float)
        T = df[treatment].to_numpy(dtype=float)
        X = df[list(covariates)].to_numpy(dtype=float)

        est = CausalForestDML(
            model_t=RandomForestClassifier(n_estimators=100, random_state=random_state)
            if discrete_treatment
            else RandomForestRegressor(n_estimators=100, random_state=random_state),
            model_y=RandomForestRegressor(n_estimators=100, random_state=random_state),
            n_estimators=n_estimators,
            min_samples_leaf=min_samples_leaf,
            discrete_treatment=discrete_treatment,
            random_state=random_state,
        )
        est.fit(Y=Y, T=T, X=X)
        cate = est.effect(X)
        ate = float(np.mean(cate))

        # ATE inference via econml.ate_inference() if available.
        ate_se = float("nan")
        try:
            ate_inf = est.ate_inference(X=X)
            ate_se = float(ate_inf.stderr_mean())
        except Exception:
            pass

        # Feature-importance proxy: the fitted forest's feature_importances_.
        feature_importances: dict[str, float] = {}
        try:
            importances = est.feature_importances()
            feature_importances = {c: float(v) for c, v in zip(covariates, importances, strict=True)}
        except Exception:
            pass

        return HetTeResult(
            method=self.name,
            ate=ate,
            ate_std_error=ate_se,
            cate_predictions=np.asarray(cate, dtype=float),
            cate_std_errors=None,
            treatment_effect_heterogeneity_pvalue=None,
            feature_importances=feature_importances or None,
            n_units=int(len(Y)),
            diagnostics={
                "discrete_treatment": discrete_treatment,
                "n_estimators": n_estimators,
                "upstream": "econml.dml.CausalForestDML",
            },
        )
