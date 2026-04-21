"""HetTe + DML conformance tests — both skipped when optional deps absent."""

from __future__ import annotations

import pytest


def test_het_te_importable() -> None:
    # Always importable even without econml (lazy try/except in __init__).
    from factor_factory.engines.het_te import estimate, registry  # noqa: F401

    assert isinstance(registry.available(), list)


def test_dml_importable() -> None:
    from factor_factory.engines.dml import estimate, registry  # noqa: F401

    assert isinstance(registry.available(), list)


@pytest.mark.skipif(
    pytest.importorskip("econml", reason="econml not installed") is None, reason="skip"
)
def test_causal_forest_if_econml() -> None:  # pragma: no cover — runs only when econml available
    import numpy as np

    from factor_factory.engines.het_te import estimate

    rng = np.random.default_rng(0)
    n = 500
    X = rng.normal(0, 1, size=(n, 2))
    T = (X[:, 0] + rng.normal(0, 1, size=n) > 0).astype(int)
    Y = 2.0 * T + X[:, 0] + rng.normal(0, 0.5, size=n)

    import pandas as pd

    from factor_factory.tidy import Panel
    from factor_factory.tidy.contracts import PanelMetadata, Provenance

    df = pd.DataFrame(
        {
            "outcome": Y,
            "treatment": T,
            "x1": X[:, 0],
            "x2": X[:, 1],
        }
    )
    df["unit_id"] = [f"u{i}" for i in range(n)]
    df["period"] = 0
    df = df.set_index(["unit_id", "period"]).sort_index()
    meta = PanelMetadata(
        outcome_cols=("outcome",),
        period_kind="integer",
        freq=None,
        dimension="unit",
        provenance=Provenance(),
    )
    panel = Panel(df, meta)
    results = estimate(
        panel,
        methods=("causal_forest",),
        outcome="outcome",
        treatment="treatment",
        covariates=("x1", "x2"),
        # econml 0.16+ requires n_estimators % subforest_size == 0 (default
        # subforest_size=4), so 48 instead of 50 — same statistical power.
        n_estimators=48,
    )
    r = results[0]
    # Should recover an ATE near 2.0.
    assert abs(r.ate - 2.0) < 1.0
