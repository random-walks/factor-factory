"""Cox proportional-hazards regression via ``lifelines``.

Citation: Cox, D. R. (1972). Regression models and life-tables.
Journal of the Royal Statistical Society: Series B, 34(2), 187–202.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from ...tidy.panel import Panel
from ._base import SurvivalResult
from .kaplan_meier import _flatten_to_subject_table


class CoxPHEngine:
    """Cox proportional-hazards regression with optional Schoenfeld test.

    Returns covariate coefficients (log hazard ratios), hazard ratios,
    Wald p-values, 95% confidence intervals, plus per-covariate
    proportional-hazards (Schoenfeld residual) p-values.
    """

    name = "cox_ph"

    def fit(
        self,
        panel: Panel,
        *,
        duration_col: str = "duration",
        event_col: str = "event",
        covariates: tuple[str, ...] = (),
        cluster: str | None = None,
        strata: str | tuple[str, ...] | None = None,
        run_proportional_hazards_test: bool = True,
        **_engine_specific_kwargs: Any,
    ) -> SurvivalResult:
        try:
            from lifelines import CoxPHFitter
        except ImportError as exc:  # pragma: no cover
            raise ImportError(
                "CoxPHEngine requires the `lifelines` package. "
                "Install via `pip install factor-factory[survival]`."
            ) from exc

        if not covariates:
            raise ValueError(
                "CoxPHEngine requires at least one covariate. For "
                "covariate-free survival use the KaplanMeierEngine."
            )

        df = _flatten_to_subject_table(panel, duration_col, event_col)
        # Normalize strata to tuple form for downstream handling.
        if strata is not None and isinstance(strata, str):
            strata_tuple: tuple[str, ...] = (strata,)
        elif strata is not None:
            strata_tuple = tuple(strata)
        else:
            strata_tuple = ()

        keep_cols = [duration_col, event_col, *covariates, *strata_tuple]
        if cluster is not None:
            keep_cols.append(cluster)
        missing = [c for c in (*covariates, *strata_tuple) if c not in df.columns]
        if missing:
            raise ValueError(
                f"Panel missing covariate/strata column(s) {missing}. Got: {list(df.columns)}."
            )
        sub = df[keep_cols].copy().astype({duration_col: float, event_col: int})

        cph = CoxPHFitter()
        cph.fit(
            sub,
            duration_col=duration_col,
            event_col=event_col,
            cluster_col=cluster,
            strata=list(strata_tuple) if strata_tuple else None,
            robust=cluster is not None,
        )
        summary = cph.summary

        coefficients = {c: float(summary.loc[c, "coef"]) for c in covariates}
        hazard_ratios = {c: float(summary.loc[c, "exp(coef)"]) for c in covariates}
        p_values = {c: float(summary.loc[c, "p"]) for c in covariates}
        cis = {
            c: (
                float(summary.loc[c, "coef lower 95%"]),
                float(summary.loc[c, "coef upper 95%"]),
            )
            for c in covariates
        }

        ph_test_p: dict[str, float] | None = None
        if run_proportional_hazards_test:
            try:
                ph_results = cph.check_assumptions(sub, p_value_threshold=0.05, show_plots=False)
                # check_assumptions returns a list of summary tables; coerce to dict.
                ph_test_p = _extract_ph_test_pvalues(ph_results, covariates)
            except Exception:  # pragma: no cover - lifelines occasionally raises
                ph_test_p = None

        n_subjects = int(len(sub))
        n_events = int(sub[event_col].sum())

        return SurvivalResult(
            method=self.name,
            median_survival=None,  # Cox PH is semi-parametric — no closed-form median
            n_subjects=n_subjects,
            n_events=n_events,
            coefficients=coefficients,
            hazard_ratios=hazard_ratios,
            p_values=p_values,
            confidence_intervals=cis,
            proportional_hazards_test=ph_test_p,
            diagnostics={
                "concordance_index": float(cph.concordance_index_),
                "log_likelihood": float(cph.log_likelihood_),
                "n_covariates": len(covariates),
            },
        )


def _extract_ph_test_pvalues(
    ph_results: list[Any], covariates: tuple[str, ...]
) -> dict[str, float] | None:
    """Best-effort extraction of per-covariate Schoenfeld p-values."""
    if not ph_results:
        return None
    out: dict[str, float] = {}
    for cov in covariates:
        for entry in ph_results:
            try:
                if cov in entry.index and "p" in entry.columns:
                    out[cov] = float(entry.loc[cov, "p"])
                    break
            except (AttributeError, KeyError):  # pragma: no cover
                continue
    return out or None


def _isnan(x: float) -> bool:
    return bool(np.isnan(x))  # pragma: no cover
