"""Matrix-completion Synthetic Control (Athey et al. 2021).

Instead of restricting to convex donor weights, matrix-completion SCM
treats the panel as a low-rank matrix with missing post-treatment
treated cells, and imputes those cells via singular value thresholding.

References
----------
Athey, S., Bayati, M., Doudchenko, N., Imbens, G., & Khosravi, K.
(2021). Matrix completion methods for causal panel data models.
*JASA*, 116(536), 1716-1730.
https://doi.org/10.1080/01621459.2021.1891924

Reference implementation: ``mcnnm`` / R ``gsynth``. This is a
simplified homegrown port using scipy's SVD + soft-thresholding.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from ...tidy.panel import Panel
from ._base import ScmResult


class MatrixCompletionEngine:
    """Matrix-completion SCM via singular value thresholding."""

    name = "matrix_completion"

    def fit(
        self,
        panel: Panel,
        *,
        outcome: str,
        treatment: str = "treatment",
        rank_penalty: float = 1.0,
        max_iter: int = 500,
        tol: float = 1e-5,
        **_engine_specific_kwargs: Any,
    ) -> ScmResult:
        if not panel.treatment_events:
            raise ValueError("MatrixCompletionEngine requires a treatment event.")

        event = panel.treatment_events[0]
        treated_unit = list(event.treated_units)[0]
        treatment_period = event.treatment_date or event.period_value
        if panel.period_kind == "timestamp" and treatment_period is not None:
            treatment_period = pd.Timestamp(treatment_period)

        df = panel.df.reset_index()
        wide = df.pivot_table(index="period", columns="unit_id", values=outcome).sort_index()
        Y = wide.to_numpy(dtype=float)
        periods = list(wide.index)

        # Mask: True = observed (to use in fit), False = missing (to impute).
        mask = np.ones_like(Y, dtype=bool)
        treated_col = wide.columns.get_loc(treated_unit)
        for i, p in enumerate(periods):
            if p >= treatment_period:
                mask[i, treated_col] = False

        # Singular-value-thresholding iteration (a.k.a. soft-impute).
        Y_fill = np.where(mask, Y, 0.0)
        prev_norm = -np.inf
        for _ in range(max_iter):
            U, s, Vt = np.linalg.svd(Y_fill, full_matrices=False)
            s_shrunk = np.maximum(s - rank_penalty, 0.0)
            rank = int(np.sum(s_shrunk > 0))
            if rank == 0:
                break
            Y_hat = (U[:, :rank] * s_shrunk[:rank]) @ Vt[:rank, :]
            Y_fill = np.where(mask, Y, Y_hat)
            new_norm = float(np.linalg.norm(Y_fill - Y_hat, "fro"))
            if abs(new_norm - prev_norm) < tol:
                break
            prev_norm = new_norm

        # ATT = observed - imputed, averaged over treated-post cells.
        post_treated_mask = (~mask)  # cells we imputed
        gap = Y - Y_hat
        att = float(np.mean(gap[post_treated_mask])) if post_treated_mask.any() else 0.0

        # Pre-period residuals on the observed panel → pre_rmspe diagnostic.
        pre_mask_treated = np.zeros_like(mask, dtype=bool)
        for i, p in enumerate(periods):
            if p < treatment_period:
                pre_mask_treated[i, treated_col] = True
        pre_rmspe = float(
            np.sqrt(np.mean(gap[pre_mask_treated] ** 2))
        ) if pre_mask_treated.any() else float("nan")
        post_rmspe = float(
            np.sqrt(np.mean(gap[post_treated_mask] ** 2))
        ) if post_treated_mask.any() else float("nan")

        pre_periods = [p for p in periods if p < treatment_period]
        post_periods = [p for p in periods if p >= treatment_period]

        return ScmResult(
            method=self.name,
            att=att,
            std_error=None,
            pre_period_rmspe=pre_rmspe,
            post_period_rmspe=post_rmspe,
            donor_weights={},  # not applicable for matrix completion
            predictor_weights=None,
            placebo_pvalue=None,
            n_donor=int(Y.shape[1] - 1),
            n_pre=len(pre_periods),
            n_post=len(post_periods),
            diagnostics={
                "rank_penalty": rank_penalty,
                "final_rank": int(rank),
                "method": "soft-impute SVD (Athey et al. 2021)",
            },
        )
