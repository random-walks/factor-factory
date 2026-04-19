"""Parallel-trends visualization for DiD pre-flight checks."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

import pandas as pd

from ..tidy.panel import Panel

if TYPE_CHECKING:  # pragma: no cover
    import matplotlib.axes
    import matplotlib.figure


def parallel_trends_plot(
    panel: Panel,
    *,
    treated_col: str = "treated_unit",
    outcome_col: str | None = None,
    treatment_date: date | pd.Timestamp | None = None,
    ax: matplotlib.axes.Axes | None = None,
) -> matplotlib.figure.Figure:
    """Plot mean outcome over time for treated vs. control units.

    Useful as a pre-DiD parallel-trends visual. If the panel carries
    treatment events and ``treatment_date`` is omitted, the first
    event's date is used.
    """
    import matplotlib.figure as _mfig
    import matplotlib.pyplot as plt

    df = panel.df
    if treated_col not in df.columns:
        raise ValueError(f"Panel missing treated_col '{treated_col}'. Columns: {list(df.columns)}.")

    outcome = outcome_col or panel.outcome_col
    if outcome not in df.columns:
        raise ValueError(f"Panel missing outcome column '{outcome}'.")

    if treatment_date is None and panel.treatment_events:
        treatment_date = panel.treatment_events[0].treatment_date

    grouped = (
        df.groupby([treated_col, df.index.get_level_values("period")])[outcome].mean().unstack(0)
    )
    # rename 0/1 columns to control/treated for the legend
    rename = {0: "Control", 1: "Treated"}
    grouped = grouped.rename(columns=rename)

    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 5))
    else:
        host_fig = ax.figure
        if not isinstance(host_fig, _mfig.Figure):
            raise TypeError("ax.figure must be a top-level Figure, not a SubFigure.")
        fig = host_fig

    for col in ("Control", "Treated"):
        if col in grouped.columns:
            ax.plot(grouped.index, grouped[col], marker="o", label=col, linewidth=1.5)

    if treatment_date is not None:
        # axvline is type-stubbed as float-only but matplotlib accepts datetimes.
        ax.axvline(
            pd.Timestamp(treatment_date),  # type: ignore[arg-type]
            color="black",
            linestyle="--",
            alpha=0.6,
            label="Treatment date",
        )

    ax.set_xlabel("Period")
    ax.set_ylabel(f"Mean {outcome}")
    ax.set_title(f"Parallel trends — {outcome}")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig
