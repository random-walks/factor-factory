"""Common base types shared across engine families.

Each engine family (`did/`, `rdd/`, `scm/`, ...) defines its own
``Result`` dataclass and ``Engine`` Protocol in its own ``_base.py``.
This module just re-exports the registry helper for convenience.
"""

from __future__ import annotations

from ._registry import EngineRegistry

__all__ = ["EngineRegistry"]
