"""Smoke tests for Batch-11 families: spatial, inequality, reporting_bias."""

from __future__ import annotations

import numpy as np
import pandas as pd

from factor_factory.engines.inequality import TheilEngine
from factor_factory.engines.reporting_bias import LatentEmEngine
from factor_factory.tidy import Panel
from factor_factory.tidy.contracts import PanelMetadata, Provenance


def _single_period_panel(values: list[float]) -> Panel:
    n = len(values)
    df = pd.DataFrame(
        {"unit_id": [f"u{i}" for i in range(n)], "period": [0] * n, "outcome": values}
    ).set_index(["unit_id", "period"])
    df.sort_index(inplace=True)
    meta = PanelMetadata(
        outcome_cols=("outcome",),
        period_kind="integer",
        freq=None,
        dimension="unit",
        provenance=Provenance(),
    )
    return Panel(df, meta)


def test_spatial_importable() -> None:
    from factor_factory.engines.spatial import estimate, registry  # noqa: F401

    assert isinstance(registry.available(), list)


def test_theil_recovers_zero_for_equal_distribution() -> None:
    panel = _single_period_panel([10.0] * 100)
    result = TheilEngine().fit(panel, outcome="outcome")
    # Perfect equality → Theil T = 0.
    assert abs(result.overall) < 1e-10


def test_theil_positive_for_unequal_distribution() -> None:
    panel = _single_period_panel([1.0, 1.0, 1.0, 1.0, 96.0])
    result = TheilEngine().fit(panel, outcome="outcome")
    assert result.overall > 0.1


def test_latent_em_runs() -> None:
    # Synthetic: 100 units, half report at p=0.8, half at p=0.2.
    rng = np.random.default_rng(0)
    n_units = 100
    is_reporter = rng.random(n_units) < 0.5
    p_true = np.where(is_reporter, 0.8, 0.2)
    exposures = np.full(n_units, 50)
    observed = rng.binomial(exposures, p_true)

    df = pd.DataFrame(
        {
            "unit_id": [f"u{i:03d}" for i in range(n_units)],
            "period": [0] * n_units,
            "outcome": observed,
            "exposure": exposures,
        }
    ).set_index(["unit_id", "period"])
    df.sort_index(inplace=True)
    meta = PanelMetadata(
        outcome_cols=("outcome",),
        period_kind="integer",
        freq=None,
        dimension="unit",
        provenance=Provenance(),
    )
    panel = Panel(df, meta)
    result = LatentEmEngine().fit(panel, outcome="outcome", exposure="exposure")
    # Reporter rate should be near 0.8, non-reporter near 0.2 (or vice-versa).
    # EM may swap the classes — check the higher of the two is near 0.8.
    max_p = max(result.p_reporter, result.p_non_reporter)
    min_p = min(result.p_reporter, result.p_non_reporter)
    assert 0.7 <= max_p <= 0.9
    assert 0.1 <= min_p <= 0.3
    assert result.n_em_iterations > 0
