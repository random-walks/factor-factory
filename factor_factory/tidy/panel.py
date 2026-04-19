"""The central ``Panel`` data structure.

A ``Panel`` is a ``MultiIndex(unit_id, period)`` DataFrame plus
``PanelMetadata``. Every layer of factor-factory consumes and produces
panels.

Design contract: panels are **domain-agnostic**. ``unit_id`` may be
any hashable (string ticker, integer patient id, tuple geographic
key); ``period`` may be a calendar timestamp, an integer day-from-event,
a continuous dose, or any orderable label. The same Panel shape
hosts NYC-civic, finance, RCT, agronomic, and chemistry data.

See ``docs/og_context/03_specs/panel_contract.md`` for the full schema.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Iterable, Sequence
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .contracts import PanelMetadata, Provenance, TreatmentEvent
from .record_view import RecordView

# Aggregate framework-aware columns. Per-event columns use the same
# stems with ``__<event_name>`` suffixes (see ``_attach_treatment_columns``).
_TREATMENT = "treatment"
_TREATED_UNIT = "treated_unit"
_POST = "post"


def _coerce_to_timestamp(value: Any) -> pd.Timestamp:
    """Convert a date / datetime / parseable string to ``pd.Timestamp``."""
    if isinstance(value, pd.Timestamp):
        return value
    if isinstance(value, (date, datetime)):
        return pd.Timestamp(value)
    return pd.Timestamp(str(value))


def _default_unit_id_extractor(dimension: str) -> Callable[[Any], Any]:
    """Return an extractor that reads ``record[dimension]`` (or attribute)."""

    def extract(record: Any) -> Any:
        if isinstance(record, dict):
            value = record.get(dimension)
        else:
            value = getattr(record, dimension, None)
        if value is None:
            raise KeyError(
                f"Record missing '{dimension}' key/attribute and no unit_id_extractor supplied."
            )
        return value

    return extract


def _default_period_extractor() -> Callable[[Any], Any]:
    """Return an extractor that reads ``record['period']`` (or ``created_date``)."""

    def extract(record: Any) -> Any:
        if isinstance(record, dict):
            value = record.get("period")
            if value is None:
                value = record.get("created_date")
        else:
            value = getattr(record, "period", None)
            if value is None:
                value = getattr(record, "created_date", None)
        if value is None:
            raise KeyError(
                "Record missing 'period' / 'created_date' key/attribute and no "
                "period_extractor supplied."
            )
        return value

    return extract


def _default_record_extra_extractor(
    columns: tuple[str, ...],
) -> Callable[[Any], dict[str, Any]]:
    """Return an extractor that pulls a tuple of extra columns from each record."""

    def extract(record: Any) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for col in columns:
            if isinstance(record, dict):
                out[col] = record.get(col)
            else:
                out[col] = getattr(record, col, None)
        return out

    return extract


_PERIOD_FREQ_MAP = {"ME": "M", "QE": "Q", "YE": "Y"}


def _to_period_freq(freq: str) -> str:
    """Map pandas date_range freq codes to ``pd.Period`` freq codes.

    pandas ≥ 2.2 uses ``"ME"`` / ``"QE"`` / ``"YE"`` for end-anchored
    date_range frequencies, but ``pd.Period`` still wants ``"M"`` /
    ``"Q"`` / ``"Y"``. Keep them aligned.
    """
    return _PERIOD_FREQ_MAP.get(freq, freq)


def _bin_timestamp(timestamp: pd.Timestamp, freq: str) -> pd.Timestamp:
    """Snap a timestamp to the end of its period for the given pandas freq."""
    period = pd.Period(timestamp, freq=_to_period_freq(freq))
    return period.end_time.normalize()


class Panel:
    """Tidied panel: ``MultiIndex(unit_id, period)`` DataFrame + metadata.

    Construct via :meth:`from_records` for the count-aggregation case,
    or call ``__init__`` directly with a pre-built wide DataFrame. Every
    panel runs :meth:`validate` on construction; mutating ``self.df``
    afterwards bypasses validation.
    """

    def __init__(
        self,
        df: pd.DataFrame,
        metadata: PanelMetadata,
        record_view: RecordView | None = None,
    ) -> None:
        self.df = df
        self.metadata = metadata
        self._record_view = record_view
        self.validate()

    # ─── properties ──────────────────────────────────────────────────────

    @property
    def outcome_col(self) -> str:
        """Primary outcome column."""
        return self.metadata.outcome_col

    @property
    def outcome_cols(self) -> tuple[str, ...]:
        """All outcome columns (primary first)."""
        return self.metadata.outcome_cols

    @property
    def freq(self) -> str | None:
        return self.metadata.freq

    @property
    def dimension(self) -> str:
        """Cross-sectional dimension name (e.g., ``"ticker"``, ``"plot_id"``)."""
        return self.metadata.dimension

    @property
    def geography(self) -> str:
        """Back-compat alias for :attr:`dimension`."""
        return self.metadata.dimension

    @property
    def period_kind(self) -> str:
        return self.metadata.period_kind

    @property
    def treatment_events(self) -> tuple[TreatmentEvent, ...]:
        return self.metadata.treatment_events

    @property
    def weights_col(self) -> str | None:
        return self.metadata.weights_col

    @property
    def weights(self) -> pd.Series | None:
        """Observation weight series, or ``None`` if no weights column set."""
        if self.weights_col is None:
            return None
        return self.df[self.weights_col]

    @property
    def provenance(self) -> Provenance:
        return self.metadata.provenance

    @property
    def record_view(self) -> RecordView:
        """Companion per-record view. Required for record-level RDD."""
        if self._record_view is None:
            raise ValueError(
                "This Panel was built without a record_view. Re-run "
                "Panel.from_records(..., record_view=True) (or pass record_view= "
                "to the constructor)."
            )
        return self._record_view

    @property
    def has_record_view(self) -> bool:
        return self._record_view is not None

    @property
    def unit_ids(self) -> tuple[Any, ...]:
        return tuple(self.df.index.get_level_values("unit_id").unique())

    @property
    def periods(self) -> pd.Index:
        return self.df.index.get_level_values("period").unique()

    # ─── construction ────────────────────────────────────────────────────

    @classmethod
    def from_records(
        cls,
        records: Sequence[Any] | Iterable[Any],
        *,
        dimension: str | None = None,
        geography: str | None = None,  # back-compat alias
        freq: str | None = "ME",
        period_kind: str = "timestamp",
        treatment_events: tuple[TreatmentEvent, ...] = (),
        outcome_col: str = "n",
        record_view: bool = False,
        record_view_columns: tuple[str, ...] = ("latitude", "longitude"),
        weights_col: str | None = None,
        provenance: Provenance | None = None,
        unit_id_extractor: Callable[[Any], Any] | None = None,
        period_extractor: Callable[[Any], Any] | None = None,
        record_extra_extractor: Callable[[Any], dict[str, Any]] | None = None,
    ) -> Panel:
        """Build a balanced panel from a sequence of records.

        Each record is mapped to ``(unit_id, period)`` via the
        extractors. Records are counted per cell to produce the
        ``outcome_col`` column. The grid is then completed (cartesian
        product of units and periods, missing cells filled with 0).

        For non-time-based panels (dose-response, days-from-event), pass
        ``period_kind`` ∈ ``{"integer", "float", "ordinal"}`` and
        ``freq=None``.

        For analyses that need per-record per-unit context (lat/lon,
        clinical covariates, asset-level metadata), pass
        ``record_view=True`` plus a ``record_view_columns`` tuple of
        column names to retain on the companion ``RecordView``.
        """
        # Resolve dimension / geography aliases.
        if dimension is None and geography is None:
            raise TypeError(
                "Panel.from_records requires `dimension=` (preferred) or "
                "`geography=` (back-compat alias)."
            )
        if dimension is not None and geography is not None:
            raise TypeError("Pass only one of `dimension=` or `geography=`.")
        dim = dimension or geography
        assert dim is not None  # for mypy

        # Validate period_kind / freq combination.
        valid_kinds = {"timestamp", "integer", "float", "ordinal"}
        if period_kind not in valid_kinds:
            raise ValueError(f"period_kind must be one of {valid_kinds}, got {period_kind!r}.")
        if period_kind != "timestamp" and freq is not None:
            raise ValueError(
                f"freq must be None when period_kind={period_kind!r} "
                "(only timestamp panels can be re-binned by frequency)."
            )

        unit_id_extractor = unit_id_extractor or _default_unit_id_extractor(dim)
        period_extractor = period_extractor or _default_period_extractor()
        record_extra_extractor = record_extra_extractor or _default_record_extra_extractor(
            record_view_columns
        )

        rows: list[dict[str, Any]] = []
        record_rows: list[dict[str, Any]] = []
        for rec in records:
            unit_id = unit_id_extractor(rec)
            raw_period = period_extractor(rec)
            period = _coerce_period(raw_period, period_kind=period_kind, freq=freq)
            rows.append({"unit_id": unit_id, "period": period})
            if record_view:
                extras = record_extra_extractor(rec)
                if all(v is None for v in extras.values()):
                    continue
                extras["unit_id"] = unit_id
                extras["period"] = period
                record_rows.append(extras)

        record_count = len(rows)
        if not rows:
            raise ValueError("Cannot build Panel from empty records.")

        raw = pd.DataFrame(rows)
        counts = raw.groupby(["unit_id", "period"]).size().rename(outcome_col).to_frame()

        units = sorted(counts.index.get_level_values("unit_id").unique())
        full_index = _balanced_index(
            units=units,
            periods_seen=counts.index.get_level_values("period"),
            period_kind=period_kind,
            freq=freq,
        )
        df = counts.reindex(full_index, fill_value=0)
        df[outcome_col] = df[outcome_col].astype(np.float64)
        df = _attach_treatment_columns(df, treatment_events, period_kind=period_kind)
        df = df.sort_index()

        metadata = PanelMetadata(
            outcome_cols=(outcome_col,),
            period_kind=period_kind,  # type: ignore[arg-type]
            freq=freq,
            dimension=dim,
            treatment_events=treatment_events,
            weights_col=weights_col,
            record_count=record_count,
            provenance=provenance or Provenance(created_at=datetime.now(UTC)),
        )

        rv: RecordView | None = None
        if record_view:
            if not record_rows:
                raise ValueError(
                    "record_view=True requested but no records exposed any of the "
                    f"record_view_columns={record_view_columns}. Pass a custom "
                    "record_extra_extractor or extend record_view_columns."
                )
            rv = RecordView(pd.DataFrame(record_rows))

        return cls(df, metadata, record_view=rv)

    # ─── validation ──────────────────────────────────────────────────────

    def validate(self) -> None:
        """Raise ``ValueError`` if the panel violates any invariant."""
        df = self.df
        idx = df.index

        if not isinstance(idx, pd.MultiIndex):
            raise ValueError("Panel index must be a MultiIndex.")
        if list(idx.names) != ["unit_id", "period"]:
            raise ValueError(
                f"Panel index names must be ['unit_id', 'period'], got {list(idx.names)}."
            )
        if idx.has_duplicates:
            raise ValueError("Panel index has duplicate (unit_id, period) entries.")
        if bool(np.asarray(pd.isna(idx.get_level_values("unit_id"))).any()):
            raise ValueError("Panel has NaN in unit_id index level.")
        if bool(np.asarray(pd.isna(idx.get_level_values("period"))).any()):
            raise ValueError("Panel has NaN in period index level.")

        # Period dtype must match metadata.period_kind.
        period_index = idx.get_level_values("period")
        kind = self.metadata.period_kind
        if kind == "timestamp":
            if not isinstance(period_index, pd.DatetimeIndex):
                raise ValueError(
                    f"period_kind='timestamp' but period index is "
                    f"{type(period_index).__name__}, expected DatetimeIndex."
                )
        elif kind == "integer" and not pd.api.types.is_integer_dtype(period_index.dtype):
            raise ValueError(f"period_kind='integer' but period dtype is {period_index.dtype}.")
        elif kind == "float" and not pd.api.types.is_float_dtype(period_index.dtype):
            raise ValueError(f"period_kind='float' but period dtype is {period_index.dtype}.")
        # "ordinal" accepts any orderable type.

        # Outcome columns must all exist + be numeric.
        for outcome in self.outcome_cols:
            if outcome not in df.columns:
                raise ValueError(
                    f"Panel missing outcome column {outcome!r}. Got columns: {list(df.columns)}."
                )
            if not pd.api.types.is_numeric_dtype(df[outcome].dtype):
                raise ValueError(
                    f"Outcome column {outcome!r} must be numeric, got {df[outcome].dtype}."
                )

        # Weights column, if specified, must exist and be numeric.
        wcol = self.metadata.weights_col
        if wcol is not None:
            if wcol not in df.columns:
                raise ValueError(f"Panel missing weights column {wcol!r}.")
            if not pd.api.types.is_numeric_dtype(df[wcol].dtype):
                raise ValueError(f"Weights column {wcol!r} must be numeric, got {df[wcol].dtype}.")

        # Balanced check
        units = idx.get_level_values("unit_id").unique()
        periods = idx.get_level_values("period").unique()
        expected = len(units) * len(periods)
        if len(df) != expected:
            raise ValueError(
                f"Panel is unbalanced: have {len(df)} rows, expected "
                f"{expected} ({len(units)} units × {len(periods)} periods)."
            )

        # Sorted
        if not idx.is_monotonic_increasing:
            raise ValueError("Panel index must be sorted (unit_id, period).")

        # Framework-aware columns: integer / numeric, no NaNs.
        for col in (_TREATED_UNIT, _POST):
            if col in df.columns:
                if df[col].isna().any():
                    raise ValueError(f"Framework column '{col}' contains NaNs.")
                if not pd.api.types.is_integer_dtype(df[col]):
                    raise ValueError(
                        f"Framework column '{col}' must be int8 (or int), got {df[col].dtype}."
                    )

        if _TREATMENT in df.columns:
            if df[_TREATMENT].isna().any():
                raise ValueError(f"Framework column '{_TREATMENT}' contains NaNs.")
            if not pd.api.types.is_numeric_dtype(df[_TREATMENT]):
                raise ValueError(
                    f"Framework column '{_TREATMENT}' must be numeric "
                    f"(int for binary, float for continuous), got {df[_TREATMENT].dtype}."
                )

    # ─── operations ──────────────────────────────────────────────────────

    def to_dataframe(self) -> pd.DataFrame:
        """Returns a copy of the underlying DataFrame."""
        return self.df.copy()

    def balance(self, *, fill_value: float = 0.0) -> Panel:
        """Return a new Panel with missing (unit, period) cells filled."""
        units = self.df.index.get_level_values("unit_id").unique()
        periods_seen = self.df.index.get_level_values("period")
        full = _balanced_index(
            units=sorted(units),
            periods_seen=periods_seen,
            period_kind=self.metadata.period_kind,
            freq=self.metadata.freq,
        )
        new_df = self.df.reindex(full, fill_value=fill_value).sort_index()
        return Panel(new_df, self.metadata, record_view=self._record_view)

    def per_event_columns(self, event_name: str) -> tuple[str, str, str]:
        """Convenience: return the per-event column names for ``event_name``.

        Useful when fitting engines against staggered-rollout panels:

        >>> treatment_col, treated_col, post_col = panel.per_event_columns("policy_a")
        >>> result = engines.did.estimate(panel, methods=("twfe",), treatment=treatment_col)
        """
        names = (
            f"{_TREATMENT}__{event_name}",
            f"{_TREATED_UNIT}__{event_name}",
            f"{_POST}__{event_name}",
        )
        for name in names:
            if name not in self.df.columns:
                raise KeyError(
                    f"Per-event column {name!r} missing — known events: "
                    f"{[e.name for e in self.treatment_events]}."
                )
        return names

    # ─── persistence ─────────────────────────────────────────────────────

    def to_parquet(self, path: str | Path) -> Path:
        """Write panel.parquet + .meta.json sidecar."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.df.to_parquet(path)
        meta_path = path.with_suffix(path.suffix + ".meta.json")
        meta_payload = json.loads(self.metadata.model_dump_json())
        meta_path.write_text(json.dumps(meta_payload, indent=2, default=str))
        return path

    @classmethod
    def from_parquet(cls, path: str | Path) -> Panel:
        path = Path(path)
        meta_path = path.with_suffix(path.suffix + ".meta.json")
        df = pd.read_parquet(path)
        meta_payload = json.loads(meta_path.read_text())
        metadata = PanelMetadata.model_validate(meta_payload)
        return cls(df, metadata)

    # ─── repr ────────────────────────────────────────────────────────────

    def __repr__(self) -> str:
        return (
            f"<Panel n_units={len(self.unit_ids)} "
            f"n_periods={len(self.periods)} "
            f"outcomes={list(self.outcome_cols)} "
            f"period_kind={self.period_kind!r} "
            f"dimension={self.dimension!r}>"
        )


# ─── helpers ────────────────────────────────────────────────────────────────


def _coerce_period(raw: Any, *, period_kind: str, freq: str | None) -> Any:
    """Convert a raw period extractor output to the canonical period value."""
    if period_kind == "timestamp":
        ts = _coerce_to_timestamp(raw)
        if freq is None:
            return ts
        return _bin_timestamp(ts, freq)
    if period_kind == "integer":
        return int(raw)
    if period_kind == "float":
        return float(raw)
    return raw  # ordinal — pass through


def _balanced_index(
    *,
    units: list[Any],
    periods_seen: pd.Index,
    period_kind: str,
    freq: str | None,
) -> pd.MultiIndex:
    """Build a balanced ``MultiIndex(unit_id, period)`` for the union of cells."""
    full_periods: pd.Index
    if period_kind == "timestamp":
        period_min = periods_seen.min()
        period_max = periods_seen.max()
        if freq is not None:
            full_periods = pd.date_range(period_min, period_max, freq=freq)
        else:
            full_periods = periods_seen.unique().sort_values()
    else:
        full_periods = pd.Index(sorted(periods_seen.unique()))
    return pd.MultiIndex.from_product([units, full_periods], names=["unit_id", "period"])


def _event_anchor(ev: TreatmentEvent, period_kind: str) -> Any:
    """Return the per-event anchor (treatment_date or period_value)."""
    if ev.treatment_date is not None:
        if period_kind != "timestamp":
            raise ValueError(
                f"TreatmentEvent {ev.name!r} uses treatment_date but panel "
                f"period_kind={period_kind!r}. Use period_value= instead."
            )
        return pd.Timestamp(ev.treatment_date)
    if period_kind == "timestamp":
        raise ValueError(
            f"TreatmentEvent {ev.name!r} uses period_value but panel "
            f"period_kind='timestamp'. Use treatment_date= instead."
        )
    return ev.period_value


def _attach_treatment_columns(
    df: pd.DataFrame,
    events: tuple[TreatmentEvent, ...],
    *,
    period_kind: str = "timestamp",
) -> pd.DataFrame:
    """Attach per-event + aggregate treatment columns derived from events.

    For every event:
      - ``treated_unit__<name>``: 1 if unit is in event's treated_units
      - ``post__<name>``: 1 if period >= event's anchor
      - ``treatment__<name>``: depends on event ``kind``:
          binary       → ``treated_unit__<name> & post__<name>`` (int8)
          continuous   → above × ``intensity`` (float64)
          categorical  → ``arm__<name>`` populated with the arm string

    Aggregate columns (``treated_unit`` / ``post`` / ``treatment``) are
    produced for any binary/continuous events present:
      - ``treated_unit``: union of treated units across binary/continuous events
      - ``post``: OR across binary/continuous post masks
      - ``treatment``: sum of per-event treatment columns

    Categorical events do not contribute to aggregate columns; analysts
    should reference the per-event ``arm__<name>`` directly.
    """
    if not events:
        return df

    df = df.copy()
    units = df.index.get_level_values("unit_id")
    periods = df.index.get_level_values("period")

    bc_events: list[TreatmentEvent] = []  # binary + continuous (aggregable)
    for ev in events:
        treated_mask = np.asarray(units.isin(ev.treated_units))
        anchor = _event_anchor(ev, period_kind=period_kind)
        post_mask = np.asarray(periods >= anchor)

        df[f"{_TREATED_UNIT}__{ev.name}"] = treated_mask.astype(np.int8)
        df[f"{_POST}__{ev.name}"] = post_mask.astype(np.int8)

        if ev.kind == "binary":
            df[f"{_TREATMENT}__{ev.name}"] = (treated_mask & post_mask).astype(np.int8)
            bc_events.append(ev)
        elif ev.kind == "continuous":
            assert ev.intensity is not None  # validated upstream
            intensity_arr = (treated_mask & post_mask).astype(np.float64) * ev.intensity
            df[f"{_TREATMENT}__{ev.name}"] = intensity_arr
            bc_events.append(ev)
        else:  # categorical
            assert ev.arm is not None
            df[f"arm__{ev.name}"] = np.where(treated_mask & post_mask, ev.arm, "control")

    if bc_events:
        treated_agg = np.zeros(len(df), dtype=np.int8)
        post_agg = np.zeros(len(df), dtype=np.int8)
        treatment_agg = np.zeros(len(df), dtype=np.float64)
        for ev in bc_events:
            treated_agg |= df[f"{_TREATED_UNIT}__{ev.name}"].to_numpy().astype(np.int8)
            post_agg |= df[f"{_POST}__{ev.name}"].to_numpy().astype(np.int8)
            treatment_agg = treatment_agg + df[f"{_TREATMENT}__{ev.name}"].to_numpy()
        df[_TREATED_UNIT] = treated_agg
        df[_POST] = post_agg
        if all(ev.kind == "binary" for ev in bc_events):
            df[_TREATMENT] = treatment_agg.astype(np.int8)
        else:
            df[_TREATMENT] = treatment_agg.astype(np.float64)

    return df
