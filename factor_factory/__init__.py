"""factor-factory — shared factor-model + analysis-pipeline framework.

Default install ships the tidy + diagnostics + jellycell layers. Engine
families are optional extras; install via e.g. ``pip install
factor-factory[did]``.

Top-level surface:

    import factor_factory as ff

    panel = ff.Panel.from_records(...)
    results = ff.engines.did.estimate(panel, methods=("twfe",), ...)
    ff.diagnostics.standardized_mean_differences(panel, ...)
    ff.jellycell.tearsheets.methodology(project="my-showcase")
"""

from . import diagnostics, engines, factors, jellycell
from ._version import __version__
from .tidy import Panel, PanelMetadata, RecordView, TreatmentEvent

__all__ = [
    "Panel",
    "PanelMetadata",
    "RecordView",
    "TreatmentEvent",
    "__version__",
    "diagnostics",
    "engines",
    "factors",
    "jellycell",
]
