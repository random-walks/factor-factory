"""High-dimensional fixed-effects panel regression via ``pyfixest``.

References
----------
Correia, S. (2016). Linear models with high-dimensional fixed effects:
An efficient and feasible estimator. Working Paper.
(Stata ``reghdfe`` originator; ``pyfixest`` is the Python port.)

Reference implementation: https://py-econometrics.github.io/pyfixest/
"""

from __future__ import annotations

from typing import Any

from ...tidy.panel import Panel
from ._base import PanelRegResult


class PyfixestEngine:
    """HDFE panel regression via pyfixest."""

    name = "pyfixest"

    def fit(
        self,
        panel: Panel,
        *,
        outcome: str,
        regressors: tuple[str, ...],
        fixed_effects: tuple[str, ...] = (),
        cluster: str | None = None,
        **_engine_specific_kwargs: Any,
    ) -> PanelRegResult:
        try:
            import pyfixest as pf
        except ImportError as exc:  # pragma: no cover
            raise ImportError(
                "PyfixestEngine requires `pyfixest`. Install via "
                "`pip install factor-factory[panel-reg]`."
            ) from exc

        df = panel.df.reset_index()

        # Build a Wilkinson-style formula: outcome ~ regressor1 + regressor2 | fe1 + fe2
        rhs = " + ".join(regressors) if regressors else "1"
        fe_part = f" | {' + '.join(fixed_effects)}" if fixed_effects else ""
        formula = f"{outcome} ~ {rhs}{fe_part}"

        fit = pf.feols(formula, data=df, vcov={"CRV1": cluster} if cluster else "iid")
        tidy_df = fit.tidy()

        coefficients = {row["Coefficient"]: float(row["Estimate"]) for _, row in tidy_df.iterrows()}
        std_errors = {row["Coefficient"]: float(row["Std. Error"]) for _, row in tidy_df.iterrows()}
        p_values = {row["Coefficient"]: float(row["Pr(>|t|)"]) for _, row in tidy_df.iterrows()}
        cis = {
            row["Coefficient"]: (float(row["2.5%"]), float(row["97.5%"]))
            for _, row in tidy_df.iterrows()
        }

        import contextlib

        r_squared = None
        with contextlib.suppress(Exception):
            r_squared = float(fit._r2)

        return PanelRegResult(
            method=self.name,
            coefficients=coefficients,
            std_errors=std_errors,
            p_values=p_values,
            confidence_intervals=cis,
            r_squared=r_squared,
            n_observations=int(fit._N),
            n_fixed_effects=len(fixed_effects),
            fixed_effects=fixed_effects,
            cluster=cluster,
            diagnostics={"formula": formula, "upstream": "pyfixest.feols"},
        )
