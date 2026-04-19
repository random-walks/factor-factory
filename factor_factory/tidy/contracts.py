"""Pydantic schemas for the tidy layer.

These types are the public data contracts factor-factory commits to.
The design goal is **domain-agnostic** scaffolding — finance event
studies, RCT longitudinal data, agricultural yield trials, and
chemical assays should all fit the same shapes as NYC-style civic
data.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

# Treatment kinds. ``binary`` is the NYC-civic / DiD default.
# ``continuous`` covers dose-response, treatment intensity (e.g.,
# rainfall, fertilizer kg/ha, advertising spend). ``categorical``
# covers multi-arm RCTs and policy-bundle comparisons.
TreatmentKind = Literal["binary", "continuous", "categorical"]


class TreatmentEvent(BaseModel):
    """A single treatment event applied to a specified set of units.

    Parameters
    ----------
    name
        Short identifier (e.g., ``"rat_pilot"``, ``"vaccine_arm_A"``,
        ``"fed_rate_hike_2024-09"``). Used to derive per-event column
        names: ``treatment__<name>`` / ``treated__<name>`` /
        ``post__<name>``.
    description
        Free-form description for tearsheets and provenance.
    treated_units
        Units that participate in this event. Stored as a tuple of
        hashable identifiers (typically ``str``, but ``int`` /
        ``tuple[str, str]`` are equally accepted).
    treatment_date
        Onset date / period. Stored as ``date`` for back-compat;
        non-time periods (e.g., dose levels, days-from-event) live in
        ``period_value`` instead.
    period_value
        For non-time-based panels, the period at which treatment
        starts (e.g., dose threshold, days-from-event = 0). Mutually
        exclusive with ``treatment_date``: pass exactly one.
    dimension
        Which panel dimension the units belong to. Defaults to
        ``"unit"``. Use ``"community_district"`` / ``"tract"`` /
        ``"station"`` for civic data, ``"ticker"`` for finance,
        ``"patient_id"`` for clinical, ``"plot_id"`` for ag, etc.
    kind
        ``"binary"`` (the default), ``"continuous"``, or
        ``"categorical"``.
    intensity
        For ``kind="continuous"``, the per-unit treatment intensity
        (dose, exposure, advertising spend). Ignored otherwise.
    arm
        For ``kind="categorical"``, the arm label (``"placebo"``,
        ``"low_dose"``, ``"high_dose"``). Ignored otherwise.
    metadata
        Free-form dict for any additional event-level context that
        downstream renderers / engines may consume.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str = Field(..., min_length=1, max_length=64)
    description: str = ""
    treated_units: tuple[Any, ...]
    treatment_date: date | None = None
    period_value: float | int | None = None
    dimension: str = "unit"
    kind: TreatmentKind = "binary"
    intensity: float | None = None
    arm: str | None = None
    metadata: dict[str, Any] | None = None

    @model_validator(mode="before")
    @classmethod
    def _normalize_legacy_fields(cls, data: Any) -> Any:
        """Accept the legacy ``geography=`` kwarg as an alias for ``dimension=``."""
        if not isinstance(data, dict):
            return data
        data = dict(data)  # don't mutate caller's dict
        if "geography" in data:
            if "dimension" in data:
                raise ValueError(
                    "TreatmentEvent received both 'geography' and 'dimension' — "
                    "pass only 'dimension' (or 'geography' for back-compat)."
                )
            data["dimension"] = data.pop("geography")
        return data

    @model_validator(mode="after")
    def _validate_treatment_anchor(self) -> TreatmentEvent:
        if self.treatment_date is None and self.period_value is None:
            raise ValueError(
                f"TreatmentEvent {self.name!r} must specify either "
                "treatment_date (for time-based panels) or period_value "
                "(for non-time panels like dose-response)."
            )
        if self.treatment_date is not None and self.period_value is not None:
            raise ValueError(
                f"TreatmentEvent {self.name!r} got both treatment_date "
                "and period_value — pass exactly one."
            )
        if self.kind == "continuous" and self.intensity is None:
            raise ValueError(
                f"TreatmentEvent {self.name!r} kind='continuous' requires "
                "intensity= (e.g., dose level)."
            )
        if self.kind == "categorical" and self.arm is None:
            raise ValueError(
                f"TreatmentEvent {self.name!r} kind='categorical' requires "
                "arm= (e.g., 'placebo' / 'high_dose')."
            )
        if not self.treated_units:
            raise ValueError(
                f"TreatmentEvent {self.name!r} has no treated_units — pass "
                "at least one unit identifier."
            )
        return self


class Provenance(BaseModel):
    """Data-source provenance + publishing metadata.

    Surfaces in tearsheets so downstream consumers can cite the data
    source, check the license, and review ethics considerations
    without re-deriving them from notebook prose. Following the
    publishing-best-practices ethos: every analysis should make its
    data lineage legible.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    data_source: str | None = None
    """Where the data came from — URL, DOI, Socrata dataset id, etc."""

    license: str | None = None
    """Data license string (e.g., ``"CC-BY-4.0"``, ``"ODbL-1.0"``,
    ``"public-domain"``, ``"proprietary"``)."""

    ethics_note: str | None = None
    """IRB / data-ethics note. For human-subjects / population-health
    work, document IRB approval. For sensitive data, document
    aggregation / privacy-preserving steps."""

    citation: str | None = None
    """How to cite this data in a paper / report."""

    creator: str | None = None
    """Organization or author that produced the data."""

    dataset_version: str | None = None
    """Version / vintage tag of the source dataset (e.g.,
    ``"2024Q3"``, ``"v3.1"``)."""

    created_at: datetime | None = None
    """When the panel was constructed (UTC)."""


class PanelMetadata(BaseModel):
    """Provenance + structure metadata for a Panel.

    Carried alongside the DataFrame so the panel is self-describing
    on disk (saved to a ``.meta.json`` sidecar by ``Panel.to_parquet``).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    # ─── structure (always present) ──────────────────────────────────────
    outcome_cols: tuple[str, ...]
    """One or more outcome columns. The first is the *primary* outcome
    (returned by ``Panel.outcome_col``); secondaries are available via
    ``Panel.outcome_cols``."""

    period_kind: Literal["timestamp", "integer", "float", "ordinal"] = "timestamp"
    """Type of the period index level. ``timestamp`` for calendar
    time, ``integer`` for things like days-from-event, ``float`` for
    dose / temperature / continuous keys, ``ordinal`` for arbitrary
    orderable labels."""

    freq: str | None = "ME"
    """Pandas frequency string when ``period_kind == "timestamp"``;
    ``None`` otherwise. ``"ME"`` (month-end) is the civic-data
    convention; finance typically uses ``"D"``, RCTs ``"D"`` /
    ``"W"``, ag often skips period entirely."""

    dimension: str = "unit"
    """Name of the cross-sectional dimension (e.g.,
    ``"community_district"``, ``"ticker"``, ``"patient_id"``,
    ``"plot_id"``). Used as the unit-axis label in plots and
    tearsheets."""

    treatment_events: tuple[TreatmentEvent, ...] = ()
    """All treatment events on this panel (zero or more)."""

    weights_col: str | None = None
    """Optional column to use as observation weights (e.g.,
    ``"population"`` for ecological studies, ``"market_cap"`` for
    finance, ``"plot_area_ha"`` for ag)."""

    record_count: int = 0
    """Raw record count before tidying — provenance for the
    aggregation step."""

    provenance: Provenance = Field(default_factory=Provenance)
    """Data-source + publishing metadata. See :class:`Provenance`."""

    # ─── back-compat aliases ─────────────────────────────────────────────

    @property
    def outcome_col(self) -> str:
        """Primary outcome column (first entry of ``outcome_cols``)."""
        return self.outcome_cols[0]

    @property
    def geography(self) -> str:
        """Back-compat alias for :attr:`dimension`. Will warn in v0.2+."""
        return self.dimension

    @model_validator(mode="before")
    @classmethod
    def _normalize_legacy_fields(cls, data: Any) -> Any:
        """Accept the legacy ``outcome_col=`` and ``geography=`` kwargs.

        Old: ``PanelMetadata(geography="cd", outcome_col="x", ...)``
        New: ``PanelMetadata(dimension="cd", outcome_cols=("x",), ...)``
        """
        if not isinstance(data, dict):
            return data
        data = dict(data)
        if "outcome_col" in data:
            if "outcome_cols" in data:
                raise ValueError(
                    "PanelMetadata received both 'outcome_col' and 'outcome_cols' — "
                    "pass only one (prefer 'outcome_cols' for new code)."
                )
            data["outcome_cols"] = (data.pop("outcome_col"),)
        if "geography" in data:
            if "dimension" in data:
                raise ValueError(
                    "PanelMetadata received both 'geography' and 'dimension' — "
                    "pass only 'dimension' (or 'geography' for back-compat)."
                )
            data["dimension"] = data.pop("geography")
        return data

    @model_validator(mode="after")
    def _validate(self) -> PanelMetadata:
        if not self.outcome_cols:
            raise ValueError("PanelMetadata.outcome_cols must have at least one entry.")
        if self.period_kind != "timestamp" and self.freq is not None:
            raise ValueError(
                f"freq must be None when period_kind={self.period_kind!r}, got freq={self.freq!r}."
            )
        return self
