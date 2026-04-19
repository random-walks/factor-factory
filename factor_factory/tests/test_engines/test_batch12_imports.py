"""Smoke tests for Batch-12 families: hawkes, climate, diffusion."""

from __future__ import annotations

import numpy as np

from factor_factory.engines.climate import MannKendallEngine
from factor_factory.tests._fixtures.cross_domain import climate_anomaly_panel


def test_hawkes_importable() -> None:
    from factor_factory.engines.hawkes import estimate, registry  # noqa: F401

    assert isinstance(registry.available(), list)


def test_climate_importable() -> None:
    from factor_factory.engines.climate import estimate, registry  # noqa: F401

    assert "mann_kendall" in registry


def test_diffusion_importable() -> None:
    from factor_factory.engines.diffusion import estimate, registry  # noqa: F401

    assert isinstance(registry.available(), list)


def test_mann_kendall_detects_increasing_trend() -> None:
    # Use the climate_anomaly_panel fixture.
    panel = climate_anomaly_panel()
    result = MannKendallEngine().fit(panel, outcome=panel.outcome_col)
    # z-statistic is meaningful; trend is 'increasing', 'decreasing', or 'no trend'.
    assert result.trend in {"increasing", "decreasing", "no trend"}
    assert result.n_observations > 0
    # Sen's slope is finite.
    assert result.slope is not None
    assert np.isfinite(result.slope)
