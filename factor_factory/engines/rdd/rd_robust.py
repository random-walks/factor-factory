"""Regression-Discontinuity adapter via the ``rdrobust`` package.

Wraps the canonical Calonico-Cattaneo-Titiunik (2014) robust
bias-corrected RDD estimator. Supports sharp + fuzzy designs,
MSE-optimal bandwidth selection, and robust SE construction.

References
----------
Calonico, S., Cattaneo, M. D., & Titiunik, R. (2014). Robust
nonparametric confidence intervals for regression-discontinuity
designs. *Econometrica*, 82(6), 2295-2326.
https://doi.org/10.3982/ECTA11757

Reference Python implementation: ``rdrobust`` on PyPI
(https://pypi.org/project/rdrobust/), which wraps the R ``rdrobust``.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from ...tidy.panel import Panel
from ._base import RddResult


class RdRobustEngine:
    """RDD via ``rdrobust`` (Calonico-Cattaneo-Titiunik 2014)."""

    name = "rd_robust"

    def fit(
        self,
        panel: Panel,
        *,
        outcome: str,
        running_variable: str,
        cutoff: float = 0.0,
        design: str = "sharp",
        treatment: str | None = None,
        polynomial_order: int = 1,
        kernel: str = "triangular",
        bwselect: str = "mserd",
        covariates: tuple[str, ...] = (),
        cluster: str | None = None,
        **_engine_specific_kwargs: Any,
    ) -> RddResult:
        try:
            from rdrobust import rdrobust
        except ImportError as exc:  # pragma: no cover
            raise ImportError(
                "RdRobustEngine requires the `rdrobust` package. "
                "Install via `pip install factor-factory[rdd]`."
            ) from exc

        if design not in ("sharp", "fuzzy"):
            raise ValueError(f"design must be 'sharp' or 'fuzzy', got {design!r}.")
        if design == "fuzzy" and treatment is None:
            raise ValueError(
                "Fuzzy RDD requires a treatment column name (the binary receipt indicator)."
            )

        df = panel.df.reset_index() if panel.df.index.nlevels > 0 else panel.df
        y = df[outcome].to_numpy(dtype=float)
        x = df[running_variable].to_numpy(dtype=float)
        fuzzy = df[treatment].to_numpy(dtype=float) if design == "fuzzy" and treatment else None
        covs = df[list(covariates)].to_numpy() if covariates else None
        clust = df[cluster].to_numpy() if cluster else None

        # Map our kernel names to rdrobust's one-letter codes.
        kernel_map = {"triangular": "tri", "uniform": "uni", "epanechnikov": "epa"}
        k_code = kernel_map.get(kernel, kernel)

        result = rdrobust(
            y=y,
            x=x,
            c=cutoff,
            p=polynomial_order,
            kernel=k_code,
            bwselect=bwselect,
            fuzzy=fuzzy,
            covs=covs,
            cluster=clust,
        )

        # rdrobust returns an object with coef / se / pv / ci / bws / N_h etc.
        # Robust (bias-corrected) row is the second; conventional is first.
        estimate = float(np.asarray(result.coef).flatten()[0])
        std_error = float(np.asarray(result.se).flatten()[0])
        p_value = float(np.asarray(result.pv).flatten()[0])
        ci = np.asarray(result.ci)
        ci_lo = float(ci.flatten()[0])
        ci_hi = float(ci.flatten()[1])
        bandwidth = float(np.asarray(result.bws).flatten()[0])

        n_h = getattr(result, "N_h", None)
        n_effective = int(np.sum(np.asarray(n_h))) if n_h is not None else int(len(y))

        first_stage_f: float | None = None
        if design == "fuzzy":
            # rdrobust's fuzzy output has a first_stage attribute (varies by
            # version); fall back to None if absent.
            fs = getattr(result, "first_stage", None)
            if fs is not None:
                try:
                    first_stage_f = float(getattr(fs, "F", float("nan")))
                except Exception:
                    first_stage_f = None

        return RddResult(
            method=self.name,
            design=design,
            cutoff=cutoff,
            estimate=estimate,
            std_error=std_error,
            ci_95=(ci_lo, ci_hi),
            p_value=p_value,
            bandwidth=bandwidth,
            kernel=kernel,
            polynomial_order=polynomial_order,
            n_effective=n_effective,
            n_total=int(len(y)),
            first_stage_f=first_stage_f,
            diagnostics={
                "bwselect": bwselect,
                "covariates": list(covariates),
                "cluster": cluster,
            },
        )
