"""Tidy layer: panel construction + geography + Socrata adapter Protocol."""

from . import geography, socrata
from .contracts import PanelMetadata, Provenance, TreatmentEvent, TreatmentKind
from .panel import Panel
from .record_view import RecordView
from .streaming import PanelBuilder

__all__ = [
    "Panel",
    "PanelBuilder",
    "PanelMetadata",
    "Provenance",
    "RecordView",
    "TreatmentEvent",
    "TreatmentKind",
    "geography",
    "socrata",
]
