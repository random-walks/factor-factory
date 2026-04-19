"""First-class jellycell integration.

Workarounds for known jellycell upstream bugs (filed as
``random-walks/jellycell`` #10–#15), the five canonical manuscript
renderers, and the ``scaffold`` command.
"""

from . import notebooks, tearsheets
from .cells import setup
from .figure import from_path

__all__ = ["from_path", "notebooks", "setup", "tearsheets"]
