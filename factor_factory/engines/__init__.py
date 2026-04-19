"""Pluggable engines.

Each method family lives under its own subpackage (`did/`, `rdd/`, ...)
with a Protocol + frozen Result dataclass + registry. See
``docs/og_context/03_specs/engine_protocol.md`` for the contract.
"""

from . import did
from ._registry import EngineRegistry

__all__ = ["EngineRegistry", "did"]
