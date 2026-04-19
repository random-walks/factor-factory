"""DiD engine Protocol + frozen result dataclass."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

import pandas as pd

from ...tidy.panel import Panel


@dataclass(frozen=True)
class DidResult:
    """Result of a single difference-in-differences estimation.

    Required-for-all-engines fields are first; optional method-specific
    extras live in ``cohort_atts`` / ``diagnostics`` / ``meta``.
    """

    method: str
    att: float
    se: float
    ci_95: tuple[float, float]
    p_value: float
    n: int

    cohort_atts: dict[int, float] | None = None
    cohort_ses: dict[int, float] | None = None
    diagnostics: dict[str, Any] | None = None
    meta: dict[str, Any] | None = field(default=None, repr=False)

    def to_dict(self) -> dict[str, Any]:
        """JSON-serializable dict (excludes ``meta`` to keep payload small)."""
        return {
            "method": self.method,
            "att": self.att,
            "se": self.se,
            "ci_95_lower": self.ci_95[0],
            "ci_95_upper": self.ci_95[1],
            "p_value": self.p_value,
            "n": self.n,
            "cohort_atts": self.cohort_atts,
            "cohort_ses": self.cohort_ses,
            "diagnostics": self.diagnostics,
        }

    def summary_table(self) -> pd.DataFrame:
        """One-row summary table for tearsheet rendering.

        Parity with ``DidResults.summary_table()`` (which stacks multiple
        results). Added in v1.1.0 (Batch 4) so every per-family ``Result``
        has the same API surface.
        """
        row = {
            "method": self.method,
            "att": self.att,
            "se": self.se,
            "ci_lo": self.ci_95[0],
            "ci_hi": self.ci_95[1],
            "p_value": self.p_value,
            "n": self.n,
        }
        return pd.DataFrame([row]).set_index("method")


class DidEngine(Protocol):
    """Protocol every DiD engine adapter must satisfy."""

    name: str

    def fit(
        self,
        panel: Panel,
        *,
        outcome: str,
        treatment: str = "treatment",
        cluster: str | None = None,
        **engine_specific_kwargs: Any,
    ) -> DidResult:
        """Fit the DiD model on ``panel`` and return a ``DidResult``."""
        ...
