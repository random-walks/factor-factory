"""Event-study engine Protocol + frozen result dataclass.

Event studies measure abnormal returns around a discrete event date
(earnings announcement, merger, regulatory action, policy
announcement). Different from DiD: typically a single event date per
treated unit, with the analysis focused on a tight event window
rather than long-run treatment effects.

References: MacKinlay, A. C. (1997). Event Studies in Economics and
Finance. Journal of Economic Literature, 35(1), 13–39. Patell, J. M.
(1976). Corporate forecasts of earnings per share and stock price
behavior. Journal of Accounting Research, 14(2), 246–276.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

import pandas as pd

from ...tidy.panel import Panel


@dataclass(frozen=True)
class EventStudyResult:
    """Result of a single event-study run.

    Domain: corporate finance (M&A, earnings, IPO), policy events
    (rate hikes, regulatory announcements), pharmaceutical news
    (FDA approval), any "single date jolts asset price" analysis.
    """

    method: str
    n_events: int

    # Average abnormal return on the event day (CAR with window=[0,0])
    average_abnormal_return: float
    car_event_window: float  # cumulative abnormal return over the chosen window
    car_se: float
    car_t_stat: float
    car_p_value: float

    # Per-period AR averaged across treated units (timeline indexed by
    # event-time, e.g., -5..+20)
    abnormal_return_curve: pd.DataFrame | None = None

    # Per-unit cumulative abnormal returns
    per_unit_car: dict[str, float] | None = None

    # Pre / post window definitions used
    estimation_window: tuple[int, int] | None = None
    event_window: tuple[int, int] | None = None

    diagnostics: dict[str, Any] | None = None
    meta: dict[str, Any] | None = field(default=None, repr=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "method": self.method,
            "n_events": self.n_events,
            "average_abnormal_return": self.average_abnormal_return,
            "car_event_window": self.car_event_window,
            "car_se": self.car_se,
            "car_t_stat": self.car_t_stat,
            "car_p_value": self.car_p_value,
            "estimation_window": (list(self.estimation_window) if self.estimation_window else None),
            "event_window": list(self.event_window) if self.event_window else None,
            "diagnostics": self.diagnostics,
        }


class EventStudyEngine(Protocol):
    """Protocol every event-study adapter must satisfy."""

    name: str

    def fit(
        self,
        panel: Panel,
        *,
        outcome: str,
        market_col: str | None = None,
        estimation_window: tuple[int, int] = (-120, -20),
        event_window: tuple[int, int] = (-1, 1),
        **engine_specific_kwargs: Any,
    ) -> EventStudyResult:
        """Fit the event-study model on ``panel``."""
        ...
