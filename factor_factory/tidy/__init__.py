"""Tidy layer: panel construction + geography + Socrata adapter Protocol."""

from . import geography, socrata
from .contracts import PanelMetadata, TreatmentEvent
from .panel import Panel
from .record_view import RecordView

__all__ = [
    "Panel",
    "PanelMetadata",
    "RecordView",
    "TreatmentEvent",
    "geography",
    "socrata",
]
