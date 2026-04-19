"""Diagnostic primitives shipped in v0.1 (the four required-everywhere ones)."""

from .assertions import multi_index_assertions
from .balance import standardized_mean_differences
from .residuals import residual_diagnostics
from .trends import parallel_trends_plot

__all__ = [
    "multi_index_assertions",
    "parallel_trends_plot",
    "residual_diagnostics",
    "standardized_mean_differences",
]
