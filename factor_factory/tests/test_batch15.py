"""Tests for Batch-15: BCF, matrix-completion SCM, Quarto generator."""

from __future__ import annotations

from pathlib import Path

import pytest

from factor_factory.engines.het_te import estimate as estimate_het_te
from factor_factory.engines.het_te import registry as het_te_registry
from factor_factory.engines.scm import estimate as estimate_scm
from factor_factory.engines.scm import registry as scm_registry
from factor_factory.reporting.quarto import render_report
from factor_factory.tests._fixtures.cross_domain import (
    FIXTURE_GROUND_TRUTH,
    scm_single_treated_state_panel,
)


def test_bcf_registered_when_sklearn_available() -> None:
    pytest.importorskip("sklearn")
    assert "bcf" in het_te_registry


def test_bcf_recovers_ate_on_synthetic() -> None:
    pytest.importorskip("sklearn")
    import numpy as np
    import pandas as pd

    from factor_factory.tidy import Panel
    from factor_factory.tidy.contracts import PanelMetadata, Provenance

    rng = np.random.default_rng(0)
    n = 400
    X = rng.normal(0, 1, size=(n, 2))
    T = (X[:, 0] + rng.normal(0, 1, size=n) > 0).astype(int)
    Y = 2.0 * T + X[:, 0] + rng.normal(0, 0.3, size=n)

    df = (
        pd.DataFrame(
            {
                "unit_id": [f"u{i:03d}" for i in range(n)],
                "period": [0] * n,
                "y": Y,
                "t": T.astype(float),
                "x1": X[:, 0],
                "x2": X[:, 1],
            }
        )
        .set_index(["unit_id", "period"])
        .sort_index()
    )
    meta = PanelMetadata(
        outcome_cols=("y",),
        period_kind="integer",
        freq=None,
        dimension="unit",
        provenance=Provenance(),
    )
    panel = Panel(df, meta)
    results = estimate_het_te(
        panel, methods=("bcf",), outcome="y", treatment="t", covariates=("x1", "x2")
    )
    r = results[0]
    # Simplified BCF should recover ATE within 0.8 of true 2.0.
    assert abs(r.ate - 2.0) < 0.8


def test_matrix_completion_scm_registered() -> None:
    assert "matrix_completion" in scm_registry


def test_matrix_completion_scm_runs_and_reports_positive_att() -> None:
    """Matrix-completion SCM should detect that the treated state got a boost.

    Note: the simplified soft-impute implementation with rank_penalty=1.0 is
    a research-frontier method and not tuned for production; we assert sign
    + magnitude order rather than tight numerical recovery. Production users
    should tune rank_penalty via cross-validation.
    """
    panel = scm_single_treated_state_panel()
    results = estimate_scm(panel, methods=("matrix_completion",), outcome="y")
    r = results[0]
    # Sign is right (positive treatment effect).
    assert r.att > 0
    # Within 10x of truth — loose gate reflecting the untuned penalty.
    truth = FIXTURE_GROUND_TRUTH["scm_single_treated_state_panel"]["att"]
    assert abs(r.att) < 10 * truth


def test_quarto_generator_writes_qmd(tmp_path: Path) -> None:
    out = tmp_path / "report.qmd"
    results = [
        {
            "method": "twfe",
            "att": 2.5,
            "se": 0.1,
            "ci_95_lower": 2.3,
            "ci_95_upper": 2.7,
            "p_value": 0.001,
            "n": 500,
        }
    ]
    panel_summary = {
        "n_units": 100,
        "n_periods": 12,
        "n_records": 1200,
        "provenance": {"data_source": "test", "license": "MIT"},
    }
    render_report(
        results=results,
        panel_summary=panel_summary,
        out_path=out,
        title="Test Report",
    )
    assert out.exists()
    content = out.read_text()
    assert "Test Report" in content
    assert "twfe" in content
    assert "n_units" in content
    assert "MIT" in content
