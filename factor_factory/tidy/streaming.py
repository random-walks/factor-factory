"""Streaming Panel builder for >10M-record datasets.

``Panel.from_records`` materializes the full record list in memory. For
very large datasets (10M+ records), use ``PanelBuilder`` instead: accept
record chunks incrementally, accumulate counts into a small state dict,
and emit a ``Panel`` at ``.build()`` time.

The trade-off: streaming gives up random access to the original records,
so custom ``record_extra_extractor`` callbacks aren't supported (the
builder only maintains aggregated counts). For use-cases that need the
RecordView, fall back to ``Panel.from_records`` with enough RAM.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Iterable
from datetime import UTC, datetime
from typing import Any

import numpy as np
import pandas as pd

from .contracts import PanelMetadata, Provenance, TreatmentEvent
from .panel import Panel, _attach_treatment_columns, _balanced_index, _coerce_period


class PanelBuilder:
    """Incremental Panel builder for large record streams.

    Usage::

        builder = PanelBuilder(dimension="unit", outcome_col="events")
        for chunk in iter_huge_dataset_in_chunks():
            builder.ingest(chunk)
        panel = builder.build()

    The builder maintains a ``Counter[(unit_id, period)]`` that grows with
    unique cells only, not with record count. Memory is O(n_units × n_periods),
    not O(n_records).
    """

    def __init__(
        self,
        *,
        dimension: str,
        outcome_col: str = "n",
        freq: str | None = "ME",
        period_kind: str = "timestamp",
        treatment_events: tuple[TreatmentEvent, ...] = (),
        provenance: Provenance | None = None,
        unit_id_extractor: Callable[[Any], Any] | None = None,
        period_extractor: Callable[[Any], Any] | None = None,
    ) -> None:
        self._dimension = dimension
        self._outcome_col = outcome_col
        self._freq = freq
        self._period_kind = period_kind
        self._treatment_events = treatment_events
        self._provenance = provenance or Provenance(created_at=datetime.now(UTC))
        self._counts: Counter[tuple[Any, Any]] = Counter()
        self._record_count = 0

        if unit_id_extractor is None:

            def default_unit_extract(rec: Any) -> Any:
                if isinstance(rec, dict):
                    return rec[dimension]
                return getattr(rec, dimension)

            unit_id_extractor = default_unit_extract

        if period_extractor is None:

            def default_period_extract(rec: Any) -> Any:
                if isinstance(rec, dict):
                    return rec.get("period") or rec.get("created_date")
                return getattr(rec, "period", None) or getattr(rec, "created_date", None)

            period_extractor = default_period_extract

        self._unit_id_extractor = unit_id_extractor
        self._period_extractor = period_extractor

    def ingest(self, records: Iterable[Any]) -> PanelBuilder:
        """Accept another batch of records. Returns self for chaining."""
        for rec in records:
            unit_id = self._unit_id_extractor(rec)
            raw_period = self._period_extractor(rec)
            period = _coerce_period(raw_period, period_kind=self._period_kind, freq=self._freq)
            self._counts[(unit_id, period)] += 1
            self._record_count += 1
        return self

    def build(self) -> Panel:
        """Materialize the accumulated counts into a validated Panel."""
        if not self._counts:
            raise ValueError("PanelBuilder received no records.")

        rows = [
            {"unit_id": u, "period": p, self._outcome_col: c}
            for (u, p), c in self._counts.items()
        ]
        df = pd.DataFrame(rows).set_index(["unit_id", "period"]).sort_index()

        units = sorted(df.index.get_level_values("unit_id").unique())
        full_index = _balanced_index(
            units=units,
            periods_seen=df.index.get_level_values("period"),
            period_kind=self._period_kind,
            freq=self._freq,
        )
        df = df.reindex(full_index, fill_value=0)
        df[self._outcome_col] = df[self._outcome_col].astype(np.float64)
        df = _attach_treatment_columns(df, self._treatment_events, period_kind=self._period_kind)
        df = df.sort_index()

        metadata = PanelMetadata(
            outcome_cols=(self._outcome_col,),
            period_kind=self._period_kind,  # type: ignore[arg-type]
            freq=self._freq,
            dimension=self._dimension,
            treatment_events=self._treatment_events,
            weights_col=None,
            record_count=self._record_count,
            provenance=self._provenance,
        )
        return Panel(df, metadata)

    @property
    def n_records(self) -> int:
        return self._record_count

    @property
    def n_cells(self) -> int:
        """Number of unique (unit, period) cells accumulated so far."""
        return len(self._counts)
