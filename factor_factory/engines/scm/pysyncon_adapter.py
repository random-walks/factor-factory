"""Synthetic-Control Method via ``pysyncon``.

References
----------
Abadie, A., Diamond, A., & Hainmueller, J. (2010). Synthetic control
methods for comparative case studies: Estimating the effect of
California's tobacco control program. *JASA*, 105(490), 493-505.
https://doi.org/10.1198/jasa.2009.ap08746

Reference implementation: ``pysyncon`` (https://pypi.org/project/pysyncon/).
"""

from __future__ import annotations

from typing import Any

import numpy as np

from ...tidy.panel import Panel
from ._base import ScmResult


class PysynconEngine:
    """Classic synthetic-control via ``pysyncon``.

    Expects a single-treated-unit, single-date treatment block. For
    multiple treated units, use ``engines.sdid`` or the augmented SCM
    below.
    """

    name = "pysyncon"

    def fit(
        self,
        panel: Panel,
        *,
        outcome: str,
        treatment: str = "treatment",
        predictors: tuple[str, ...] = (),
        **_engine_specific_kwargs: Any,
    ) -> ScmResult:
        try:
            from pysyncon import Dataprep, Synth
        except ImportError as exc:  # pragma: no cover
            raise ImportError(
                "PysynconEngine requires the `pysyncon` package. "
                "Install via `pip install factor-factory[scm]`."
            ) from exc

        if not panel.treatment_events:
            raise ValueError(
                "PysynconEngine requires panel.treatment_events (single event, "
                "single treated unit)."
            )

        event = panel.treatment_events[0]
        treated_unit = list(event.treated_units)[0]
        treatment_period = event.treatment_date or event.period_value

        df = panel.df.reset_index()
        periods = sorted(df["period"].unique())
        pre_periods = [p for p in periods if p < treatment_period]
        post_periods = [p for p in periods if p >= treatment_period]
        all_units = df["unit_id"].unique().tolist()
        controls = [u for u in all_units if u != treated_unit]

        dataprep = Dataprep(
            foo=df,
            predictors=list(predictors) if predictors else [outcome],
            predictors_op="mean",
            time_predictors_prior=pre_periods,
            special_predictors=[],
            dependent=outcome,
            unit_variable="unit_id",
            time_variable="period",
            treatment_identifier=treated_unit,
            controls_identifier=controls,
            time_optimize_ssr=pre_periods,
        )
        synth = Synth()
        synth.fit(dataprep=dataprep)

        donor_weights = {c: float(w) for c, w in zip(controls, synth.W, strict=True)}
        synth_path = (
            synth.W
            @ df[df["unit_id"].isin(controls)]
            .pivot_table(index="unit_id", columns="period", values=outcome)
            .loc[controls]
            .to_numpy()
        )
        treated_path = df[df["unit_id"] == treated_unit].sort_values("period")[outcome].to_numpy()
        gap = treated_path - synth_path

        pre_mask = np.array([p < treatment_period for p in periods])
        pre_rmspe = float(np.sqrt(np.mean(gap[pre_mask] ** 2)))
        post_rmspe = float(np.sqrt(np.mean(gap[~pre_mask] ** 2)))
        att = float(np.mean(gap[~pre_mask]))

        return ScmResult(
            method=self.name,
            att=att,
            std_error=None,
            pre_period_rmspe=pre_rmspe,
            post_period_rmspe=post_rmspe,
            donor_weights=donor_weights,
            predictor_weights=None,
            placebo_pvalue=None,  # full placebo permutation deferred
            n_donor=len(controls),
            n_pre=len(pre_periods),
            n_post=len(post_periods),
            diagnostics={
                "treated_unit": str(treated_unit),
                "treatment_period": str(treatment_period),
                "predictors": list(predictors) if predictors else [outcome],
            },
        )
