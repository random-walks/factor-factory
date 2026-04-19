"""Smoke tests for Batch-10 families: changepoint, stl, panel_reg."""

from __future__ import annotations


def test_changepoint_importable() -> None:
    from factor_factory.engines.changepoint import estimate, registry  # noqa: F401

    assert isinstance(registry.available(), list)


def test_stl_importable() -> None:
    from factor_factory.engines.stl import estimate, registry  # noqa: F401

    assert isinstance(registry.available(), list)


def test_panel_reg_importable() -> None:
    from factor_factory.engines.panel_reg import estimate, registry  # noqa: F401

    assert isinstance(registry.available(), list)
