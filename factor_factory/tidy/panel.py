"""The central ``Panel`` data structure.

A ``Panel`` is a ``MultiIndex(unit_id, period)`` DataFrame plus
``PanelMetadata``. Every layer of factor-factory consumes and produces
panels.

See ``docs/og_context/03_specs/panel_contract.md`` for the full schema.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Iterable, Sequence
from datetime import date, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .contracts import PanelMetadata, TreatmentEvent
from .record_view import RecordView

# Names of framework-aware columns.
_TREATMENT = "treatment"
_TREATED_UNIT = "treated_unit"
_POST = "post"
_POPULATION = "population"


def _coerce_to_timestamp(value: Any) -> pd.Timestamp:
    """Convert a date / datetime / parseable string to ``pd.Timestamp``."""
    if isinstance(value, pd.Timestamp):
        return value
    if isinstance(value, (date, datetime)):
        return pd.Timestamp(value)
    return pd.Timestamp(str(value))


def _default_unit_id_extractor(geography: str) -> Callable[[Any], str]:
    """Return an extractor that reads ``record[geography]`` (or attribute)."""

    def extract(record: Any) -> str:
        if isinstance(record, dict):
            value = record.get(geography)
        else:
            value = getattr(record, geography, None)
        if value is None:
            raise KeyError(
                f"Record missing '{geography}' key/attribute and no unit_id_extractor supplied."
            )
        return str(value)

    return extract


def _default_period_extractor() -> Callable[[Any], pd.Timestamp]:
    """Return an extractor that reads ``record['created_date']`` (or attribute)."""

    def extract(record: Any) -> pd.Timestamp:
        if isinstance(record, dict):
            value = record.get("created_date") or record.get("period")
        else:
            value = getattr(record, "created_date", None) or getattr(record, "period", None)
        if value is None:
            raise KeyError(
                "Record missing 'created_date' / 'period' key/attribute and no "
                "period_extractor supplied."
            )
        return _coerce_to_timestamp(value)

    return extract


def _default_latlon_extractor() -> Callable[[Any], tuple[float, float] | None]:
    """Return an extractor that reads ``(latitude, longitude)`` if present."""

    def extract(record: Any) -> tuple[float, float] | None:
        if isinstance(record, dict):
            lat = record.get("latitude")
            lon = record.get("longitude")
        else:
            lat = getattr(record, "latitude", None)
            lon = getattr(record, "longitude", None)
        if lat is None or lon is None:
            return None
        return float(lat), float(lon)

    return extract


_PERIOD_FREQ_MAP = {"ME": "M", "QE": "Q", "YE": "Y"}


def _to_period_freq(freq: str) -> str:
    """Map pandas date_range freq codes to ``pd.Period`` freq codes.

    pandas ≥ 2.2 uses ``"ME"`` / ``"QE"`` / ``"YE"`` for end-anchored
    date_range frequencies, but ``pd.Period`` still wants ``"M"`` /
    ``"Q"`` / ``"Y"``. Keep them aligned.
    """
    return _PERIOD_FREQ_MAP.get(freq, freq)


def _bin_period(timestamp: pd.Timestamp, freq: str) -> pd.Timestamp:
    """Snap a timestamp to the end of its period for the given pandas freq."""
    period = pd.Period(timestamp, freq=_to_period_freq(freq))
    return period.end_time.normalize()


class Panel:
    """Tidied panel: ``MultiIndex(unit_id, period)`` DataFrame + metadata.

    Construct via ``Panel.from_records`` for the common case, or the
    ``__init__`` with a pre-built DataFrame for advanced usage. Every
    panel runs ``validate()`` on construction; mutating ``self.df``
    directly bypasses validation.
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
        return self.metadata.outcome_col

    @property
    def freq(self) -> str:
        return self.metadata.freq

    @property
    def geography(self) -> str:
        return self.metadata.geography

    @property
    def treatment_events(self) -> tuple[TreatmentEvent, ...]:
        return self.metadata.treatment_events

    @property
    def record_view(self) -> RecordView:
        """Companion lat/lon-preserving view. Required for record-level RDD."""
        if self._record_view is None:
            raise ValueError(
                "This Panel was built without record_view=True. "
                "Re-run Panel.from_records(..., record_view=True) for "
                "lat/lon-preserving views."
            )
        return self._record_view

    @property
    def has_record_view(self) -> bool:
        return self._record_view is not None

    @property
    def unit_ids(self) -> tuple[str, ...]:
        return tuple(self.df.index.get_level_values("unit_id").unique())

    @property
    def periods(self) -> pd.DatetimeIndex:
        return pd.DatetimeIndex(self.df.index.get_level_values("period").unique())

    # ─── construction ────────────────────────────────────────────────────

    @classmethod
    def from_records(
        cls,
        records: Sequence[Any] | Iterable[Any],
        *,
        geography: str,
        freq: str = "ME",
        treatment_events: tuple[TreatmentEvent, ...] = (),
        outcome_col: str = "complaint_count",
        record_view: bool = False,
        unit_id_extractor: Callable[[Any], str] | None = None,
        period_extractor: Callable[[Any], pd.Timestamp] | None = None,
        latlon_extractor: Callable[[Any], tuple[float, float] | None] | None = None,
    ) -> Panel:
        """Build a balanced panel from a sequence of records.

        Each record is mapped to ``(unit_id, period)`` via the
        extractors. Records are counted per cell to produce the
        ``outcome_col`` column. The grid is then completed (cartesian
        product of units and periods, missing cells filled with 0).
        """
        unit_id_extractor = unit_id_extractor or _default_unit_id_extractor(geography)
        period_extractor = period_extractor or _default_period_extractor()
        latlon_extractor = latlon_extractor or _default_latlon_extractor()

        rows: list[dict[str, Any]] = []
        record_rows: list[dict[str, Any]] = []
        for rec in records:
            unit_id = unit_id_extractor(rec)
            timestamp = period_extractor(rec)
            period = _bin_period(timestamp, freq)
            rows.append({"unit_id": unit_id, "period": period})
            if record_view:
                latlon = latlon_extractor(rec)
                if latlon is None:
                    continue
                lat, lon = latlon
                record_rows.append(
                    {
                        "unit_id": unit_id,
                        "period": period,
                        "latitude": lat,
                        "longitude": lon,
                    }
                )

        record_count = len(rows)
        if not rows:
            raise ValueError("Cannot build Panel from empty records.")

        raw = pd.DataFrame(rows)
        counts = raw.groupby(["unit_id", "period"]).size().rename(outcome_col).to_frame()

        units = sorted(counts.index.get_level_values("unit_id").unique())
        period_min = counts.index.get_level_values("period").min()
        period_max = counts.index.get_level_values("period").max()
        all_periods = pd.date_range(period_min, period_max, freq=freq)
        full_index = pd.MultiIndex.from_product([units, all_periods], names=["unit_id", "period"])
        df = counts.reindex(full_index, fill_value=0)
        df[outcome_col] = df[outcome_col].astype(np.float64)

        # Treatment columns derived from events
        df = _attach_treatment_columns(df, treatment_events)

        df = df.sort_index()

        metadata = PanelMetadata(
            geography=geography,
            freq=freq,
            treatment_events=treatment_events,
            outcome_col=outcome_col,
            record_count=record_count,
        )

        rv: RecordView | None = None
        if record_view:
            if not record_rows:
                raise ValueError(
                    "record_view=True requested but no records exposed lat/lon. "
                    "Pass a custom latlon_extractor."
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

        unit_dtype = idx.get_level_values("unit_id").dtype
        if unit_dtype is not np.dtype("O") and not pd.api.types.is_string_dtype(unit_dtype):
            raise ValueError(f"unit_id index level must be string-typed, got {unit_dtype}.")

        if not isinstance(idx.get_level_values("period"), pd.DatetimeIndex):
            raise ValueError("period index level must be DatetimeIndex (use freq='ME' or similar).")

        if self.outcome_col not in df.columns:
            raise ValueError(
                f"Panel missing outcome column '{self.outcome_col}'. "
                f"Got columns: {list(df.columns)}."
            )

        outcome_dtype = df[self.outcome_col].dtype
        if not pd.api.types.is_float_dtype(outcome_dtype):
            raise ValueError(
                f"Outcome column '{self.outcome_col}' must be float64, got {outcome_dtype}."
            )

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

        for col in (_TREATMENT, _TREATED_UNIT, _POST):
            if col in df.columns:
                if df[col].isna().any():
                    raise ValueError(f"Framework column '{col}' contains NaNs.")
                if not pd.api.types.is_integer_dtype(df[col]):
                    raise ValueError(
                        f"Framework column '{col}' must be int8 (or int), got {df[col].dtype}."
                    )

        # Treatment consistency: treatment == treated_unit & post (when all present)
        if all(c in df.columns for c in (_TREATMENT, _TREATED_UNIT, _POST)):
            derived = (df[_TREATED_UNIT] & df[_POST]).astype(np.int8)
            if not (df[_TREATMENT].astype(np.int8) == derived).all():
                raise ValueError(
                    "Inconsistent treatment columns: "
                    "'treatment' must equal 'treated_unit' & 'post'."
                )

    # ─── operations ──────────────────────────────────────────────────────

    def to_dataframe(self) -> pd.DataFrame:
        """Returns a copy of the underlying DataFrame."""
        return self.df.copy()

    def balance(self, *, fill_value: float = 0.0) -> Panel:
        """Return a new Panel with missing (unit, period) cells filled."""
        units = self.df.index.get_level_values("unit_id").unique()
        periods = pd.date_range(
            self.df.index.get_level_values("period").min(),
            self.df.index.get_level_values("period").max(),
            freq=self.freq,
        )
        full = pd.MultiIndex.from_product([units, periods], names=["unit_id", "period"])
        new_df = self.df.reindex(full, fill_value=fill_value).sort_index()
        return Panel(new_df, self.metadata, record_view=self._record_view)

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
            f"outcome={self.outcome_col!r} freq={self.freq!r}>"
        )


def _attach_treatment_columns(df: pd.DataFrame, events: tuple[TreatmentEvent, ...]) -> pd.DataFrame:
    """Attach treated_unit / post / treatment columns derived from events."""
    if not events:
        return df

    # For Phase 1 we collapse multiple events into a single set: any treated
    # unit at any time is treated. Per-event columns can be added in v0.2.
    treated_units: set[str] = set()
    earliest_treatment: pd.Timestamp | None = None
    for ev in events:
        treated_units.update(ev.treated_units)
        ts = pd.Timestamp(ev.treatment_date)
        earliest_treatment = ts if earliest_treatment is None else min(earliest_treatment, ts)

    df = df.copy()
    unit_ids = df.index.get_level_values("unit_id")
    periods = df.index.get_level_values("period")
    df[_TREATED_UNIT] = unit_ids.isin(treated_units).astype(np.int8)
    df[_POST] = (periods >= earliest_treatment).astype(np.int8)
    df[_TREATMENT] = (df[_TREATED_UNIT] & df[_POST]).astype(np.int8)
    return df
