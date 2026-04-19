"""Synthetic DiD (Arkhangelsky, Athey, Hirshberg, Imbens, Wager 2021).

This is a homegrown implementation rather than a wrapper because no
mature Python package exists. The math follows the AER paper directly;
inference uses the jackknife (recommended for the multi-treated-unit
case in Arkhangelsky 2021 §3.4).

Citation
--------
Arkhangelsky, D., Athey, S., Hirshberg, D. A., Imbens, G. W., & Wager,
S. (2021). Synthetic Difference-in-Differences. *American Economic
Review*, 111(12), 4088-4118. https://doi.org/10.1257/aer.20190159

The reference R package is ``synthdid`` from the Stanford team:
https://synth-inference.github.io/synthdid/. This Python port should
recover the same point estimates on the canonical California-Prop-99
example to within numerical tolerance; SEs may differ slightly due to
implementation details of the jackknife.

Algorithm summary (per AER paper §2)
------------------------------------
Given an N × T panel with N_tr treated units (in a contiguous block
starting at period T_pre + 1) and N_co control units:

1. **Unit weights ω̂** solve a regularized SCM-style problem:

   ω̂ = argmin_{ω₀, ω ∈ Ω} Σ_{t=1}^{T_pre} (ω₀ + Σ_i ω_i Y_{it,co} - Ȳ_{t,tr})²
       + ζ² T_pre ‖ω‖²
   Ω = {ω ∈ ℝ^{N_co} : ω ≥ 0, Σ ω_i = 1}
   ζ = (N_tr · T_post)^{1/4} · σ̂   (σ̂ = std of first-differenced control outcomes)

2. **Time weights λ̂** solve the dual problem on the time axis:

   λ̂ = argmin_{λ₀, λ ∈ Λ} Σ_i (λ₀ + Σ_{t≤T_pre} λ_t Y_{it,co} - Ȳ_{i,post,co})²
   Λ = {λ ∈ ℝ^{T_pre} : λ ≥ 0, Σ λ_t = 1}

3. **Final τ̂** is a weighted-FE regression:

   τ̂_sdid = argmin_{τ,μ,α,β} Σ_{it} (Y_it - μ - α_i - β_t - τ W_it)² ω̃_i λ̃_t

   with ω̃_i = ω̂_i for control / 1/N_tr for treated, and λ̃_t = λ̂_t
   for pre / 1/T_post for post.

4. **Inference via jackknife** (per §3.4):
   τ̂^{(-j)} computed dropping treated unit j; SE = sqrt((N_tr - 1) /
   N_tr · Σ_j (τ̂^{(-j)} - τ̂)²).
"""

from __future__ import annotations

from math import erf, sqrt
from typing import Any

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from ...tidy.panel import Panel
from ._base import SdidResult, _pivot_panel_to_matrix


class SyntheticDidEngine:
    """Synthetic Difference-in-Differences (Arkhangelsky et al. 2021).

    Use cases: panel-data settings where parallel-trends is suspect
    but the standard SCM single-treated-unit assumption is too narrow
    (e.g., several states adopt a policy at the same time). For
    staggered rollout (different units treated at different times),
    use :class:`engines.did.CallawaySantannaEngine` instead.
    """

    name = "sdid"

    def fit(
        self,
        panel: Panel,
        *,
        outcome: str,
        treatment: str = "treatment",
        cluster: str | None = None,
        n_jackknife_max: int = 200,
        **_engine_specific_kwargs: Any,
    ) -> SdidResult:
        if not panel.treatment_events:
            raise ValueError(
                "SyntheticDidEngine requires panel.treatment_events to identify the treated block."
            )
        if panel.period_kind not in ("timestamp", "integer"):
            raise ValueError(
                "SDID requires period_kind in {'timestamp', 'integer'}; got "
                f"{panel.period_kind!r}."
            )

        Y, W = _pivot_panel_to_matrix(panel, outcome, treatment)

        # Identify treated units + treatment-onset period.
        treated_unit_mask = (W.sum(axis=1) > 0).to_numpy()  # any-period treated
        if not treated_unit_mask.any():
            raise ValueError("No treated units found in the panel.")
        # Onset period: first column index where any treated unit has W=1.
        onset_per_unit = W.where(W > 0).apply(lambda row: row.first_valid_index(), axis=1)
        treated_onsets = onset_per_unit[treated_unit_mask]
        if treated_onsets.nunique() != 1:
            raise ValueError(
                "SDID requires a single treatment-onset date for all treated "
                f"units. Found onsets: {sorted(treated_onsets.unique())}. "
                "For staggered rollout, use CallawaySantannaEngine."
            )
        onset_period = treated_onsets.iloc[0]
        period_index = list(Y.columns)
        onset_idx = period_index.index(onset_period)

        Y_pre = Y.iloc[:, :onset_idx].to_numpy(dtype=float)
        Y_post = Y.iloc[:, onset_idx:].to_numpy(dtype=float)

        Y_tr_pre = Y_pre[treated_unit_mask]
        Y_co_pre = Y_pre[~treated_unit_mask]
        Y_co_post = Y_post[~treated_unit_mask]

        n_tr = int(treated_unit_mask.sum())
        n_co = int((~treated_unit_mask).sum())
        t_pre = Y_pre.shape[1]
        t_post = Y_post.shape[1]
        if n_co < 2:
            raise ValueError(
                f"SDID needs ≥ 2 control units; got {n_co}. Add never-treated units to the panel."
            )
        if t_pre < 2:
            raise ValueError(f"SDID needs ≥ 2 pre-treatment periods; got {t_pre}.")

        omega = _solve_unit_weights(Y_co_pre, Y_tr_pre, n_tr=n_tr, t_post=t_post)
        lam = _solve_time_weights(Y_co_pre, Y_co_post)

        treated_indices = np.where(treated_unit_mask)[0]
        control_indices = np.where(~treated_unit_mask)[0]
        att = _weighted_did_att(Y, treated_indices, control_indices, onset_idx, omega, lam)

        se = _jackknife_se(
            Y,
            treated_indices,
            control_indices,
            onset_idx,
            omega_baseline=omega,
            lam=lam,
            n_jackknife_max=n_jackknife_max,
        )
        # 95% CI via normal approximation (per AER §3.4)
        lo = att - 1.96 * se
        hi = att + 1.96 * se
        z = att / se if se > 0 else float("nan")
        p_value = float(2.0 * (1.0 - _phi(abs(z)))) if not np.isnan(z) else 1.0

        control_unit_ids = list(Y.index[~treated_unit_mask])
        pre_periods = period_index[:onset_idx]

        return SdidResult(
            method=self.name,
            att=float(att),
            se=float(se),
            ci_95=(float(lo), float(hi)),
            p_value=p_value,
            n=int(Y.shape[0] * Y.shape[1]),
            unit_weights={u: float(w) for u, w in zip(control_unit_ids, omega, strict=True)},
            time_weights={p: float(w) for p, w in zip(pre_periods, lam, strict=True)},
            n_treated=n_tr,
            n_control=n_co,
            n_pre=t_pre,
            n_post=t_post,
            diagnostics={
                "onset_period": str(onset_period),
                "unit_weight_max": float(omega.max()),
                "unit_weight_effective_n": float(1.0 / (omega**2).sum()),
                "inference": "jackknife",
            },
        )


# ─── solvers ───────────────────────────────────────────────────────────────


def _solve_unit_weights(
    Y_co_pre: np.ndarray,
    Y_tr_pre: np.ndarray,
    *,
    n_tr: int,
    t_post: int,
) -> np.ndarray:
    """Solve for synthetic-control unit weights ω̂ (Arkhangelsky 2021 eq. 3.1).

    Includes the regularization term ζ² T_pre ‖ω‖² with
    ζ = (N_tr · T_post)^{1/4} · σ̂.
    """
    n_co, t_pre = Y_co_pre.shape
    treated_avg_pre = Y_tr_pre.mean(axis=0)  # (T_pre,)

    # σ̂ from first-differenced control outcomes (paper §3.3)
    diffs = np.diff(Y_co_pre, axis=1)  # (N_co, T_pre - 1)
    sigma_sq = float(np.var(diffs, ddof=1)) if diffs.size > 1 else 1.0
    zeta = (n_tr * t_post) ** 0.25 * np.sqrt(sigma_sq)
    reg = zeta**2 * t_pre

    # Variables: omega_0 (intercept) + omega (N_co weights summing to 1)
    # We optimize omega freely on simplex via softmax-style? No, use scipy
    # constrained optimization with bounds + linear constraint.

    def objective(params: np.ndarray) -> float:
        omega_0 = params[0]
        omega = params[1:]
        synthetic = omega_0 + Y_co_pre.T @ omega  # (T_pre,)
        residual = synthetic - treated_avg_pre
        loss = float(residual @ residual + reg * (omega @ omega))
        return loss

    def grad(params: np.ndarray) -> np.ndarray:
        omega_0 = params[0]
        omega = params[1:]
        synthetic = omega_0 + Y_co_pre.T @ omega
        residual = synthetic - treated_avg_pre
        g0 = 2.0 * residual.sum()
        g_omega = 2.0 * (Y_co_pre @ residual + reg * omega)
        return np.concatenate([[g0], g_omega])

    x0 = np.concatenate([[0.0], np.full(n_co, 1.0 / n_co)])
    bounds = [(None, None)] + [(0.0, None)] * n_co
    constraints = [{"type": "eq", "fun": lambda x: x[1:].sum() - 1.0}]

    result = minimize(
        objective,
        x0,
        jac=grad,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        options={"maxiter": 500, "ftol": 1e-10},
    )
    omega: np.ndarray = np.clip(result.x[1:], 0.0, None)
    omega = omega / omega.sum()  # numerical safety
    return omega


def _solve_time_weights(Y_co_pre: np.ndarray, Y_co_post: np.ndarray) -> np.ndarray:
    """Solve for time weights λ̂ (Arkhangelsky 2021 eq. 3.2).

    Match the post-period control average using a convex combination
    of pre-period control observations.
    """
    n_co, t_pre = Y_co_pre.shape
    target = Y_co_post.mean(axis=1)  # (N_co,) — per-control post-mean

    def objective(params: np.ndarray) -> float:
        lam_0 = params[0]
        lam = params[1:]
        synthetic = lam_0 + Y_co_pre @ lam  # (N_co,)
        residual = synthetic - target
        return float(residual @ residual)

    def grad(params: np.ndarray) -> np.ndarray:
        lam_0 = params[0]
        lam = params[1:]
        synthetic = lam_0 + Y_co_pre @ lam
        residual = synthetic - target
        g0 = 2.0 * residual.sum()
        g_lam = 2.0 * Y_co_pre.T @ residual
        return np.concatenate([[g0], g_lam])

    x0 = np.concatenate([[0.0], np.full(t_pre, 1.0 / t_pre)])
    bounds = [(None, None)] + [(0.0, None)] * t_pre
    constraints = [{"type": "eq", "fun": lambda x: x[1:].sum() - 1.0}]

    result = minimize(
        objective,
        x0,
        jac=grad,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        options={"maxiter": 500, "ftol": 1e-10},
    )
    lam: np.ndarray = np.clip(result.x[1:], 0.0, None)
    lam = lam / lam.sum()
    return lam


def _weighted_did_att(
    Y: pd.DataFrame,
    treated_indices: np.ndarray,
    control_indices: np.ndarray,
    onset_idx: int,
    omega: np.ndarray,
    lam: np.ndarray,
) -> float:
    """Final SDID ATT via weighted two-way DiD (closed-form for binary block treatment).

    For the canonical block-treatment design (treated units × post periods),
    the SDID estimator reduces to:

      τ̂ = Y̅_tr,post - Y̅_tr,pre,λ - Y̅_co,post,ω + Y̅_co,pre,(ω,λ)

    where the bars are weighted means.
    """
    if len(treated_indices) == 0:
        raise ValueError("Need at least one treated unit to compute ATT.")
    if len(control_indices) != len(omega):
        raise ValueError(
            f"omega has length {len(omega)} but {len(control_indices)} control units were supplied."
        )

    Y_arr = Y.to_numpy(dtype=float)
    Y_tr_pre = Y_arr[treated_indices, :onset_idx]  # (N_tr, T_pre)
    Y_tr_post = Y_arr[treated_indices, onset_idx:]  # (N_tr, T_post)
    Y_co_pre = Y_arr[control_indices, :onset_idx]  # (N_co, T_pre)
    Y_co_post = Y_arr[control_indices, onset_idx:]  # (N_co, T_post)

    # 1/N_tr × 1/T_post over treated × post block
    treated_post_avg = Y_tr_post.mean()
    # weighted by λ over treated × pre block (then averaged across treated units)
    treated_pre_lam = (Y_tr_pre @ lam).mean()
    # weighted by ω over control × post block (then averaged across post periods)
    control_post_omega = (omega @ Y_co_post).mean()
    # weighted by ω × λ over control × pre block
    control_pre_omega_lam = float(omega @ Y_co_pre @ lam)

    return float(treated_post_avg - treated_pre_lam - control_post_omega + control_pre_omega_lam)


def _jackknife_se(
    Y: pd.DataFrame,
    treated_indices: np.ndarray,
    control_indices: np.ndarray,
    onset_idx: int,
    *,
    omega_baseline: np.ndarray,
    lam: np.ndarray,
    n_jackknife_max: int = 200,
) -> float:
    """Jackknife SE: drop one treated unit at a time, recompute ATT.

    Per Arkhangelsky 2021 §3.4: this is the recommended inference
    procedure when ``n_treated ≥ 2``. Following the R ``synthdid``
    package, we hold ``omega`` and ``lam`` fixed at their baseline
    values across leave-out iterations (re-solving them per iteration
    is correct but ~N_tr × slower for negligible accuracy gain).
    """
    n_tr = len(treated_indices)
    if n_tr < 2:
        # With one treated unit, jackknife is degenerate. Fall back to a
        # placebo-style sigma estimate from control first-differences.
        Y_arr = Y.to_numpy(dtype=float)
        Y_co_pre = Y_arr[control_indices, :onset_idx]
        diffs = np.diff(Y_co_pre, axis=1)
        sigma = float(np.std(diffs, ddof=1)) if diffs.size > 1 else 1.0
        return float(sigma / np.sqrt(Y_arr.shape[1] - onset_idx))

    indices = treated_indices
    if n_tr > n_jackknife_max:
        rng = np.random.default_rng(42)
        indices = rng.choice(treated_indices, size=n_jackknife_max, replace=False)

    base_att = _weighted_did_att(
        Y, treated_indices, control_indices, onset_idx, omega_baseline, lam
    )
    leave_out_atts: list[float] = []
    for j in indices:
        leave_out_treated = np.array([i for i in treated_indices if i != j])
        att_jk = _weighted_did_att(
            Y, leave_out_treated, control_indices, onset_idx, omega_baseline, lam
        )
        leave_out_atts.append(att_jk)

    leave_out_arr = np.array(leave_out_atts)
    # Standard jackknife variance: ((N_tr - 1) / N_tr) * Σ (τ̂^{(-j)} - τ̂)²
    var = ((n_tr - 1) / n_tr) * float(np.sum((leave_out_arr - base_att) ** 2))
    return float(np.sqrt(var))


def _phi(z: float) -> float:
    """Standard-normal CDF via erf."""
    return 0.5 * (1.0 + erf(z / sqrt(2.0)))
