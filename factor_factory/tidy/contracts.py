"""Pydantic schemas for the tidy layer."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class TreatmentEvent(BaseModel):
    """A single treatment event applied to a specified set of units."""

    model_config = ConfigDict(frozen=True)

    name: str = Field(..., min_length=1)
    description: str = ""
    treated_units: tuple[str, ...]
    treatment_date: date
    geography: str


class PanelMetadata(BaseModel):
    """Provenance and structure metadata for a Panel."""

    model_config = ConfigDict(frozen=True)

    geography: str
    freq: str = "ME"
    treatment_events: tuple[TreatmentEvent, ...] = ()
    outcome_col: str = "complaint_count"
    record_count: int = 0
