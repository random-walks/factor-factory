"""Pluggable engines.

Each method family lives under its own subpackage with a Protocol +
frozen Result dataclass + registry. See
``docs/og_context/03_specs/engine_protocol.md`` for the contract.

Currently shipped families:
- :mod:`factor_factory.engines.did` — TwfeEngine + CallawaySantannaEngine
- :mod:`factor_factory.engines.survival` — KaplanMeierEngine + CoxPHEngine
- :mod:`factor_factory.engines.event_study` — MarketAdjustedEngine

Planned families (Phase 2): rdd, scm, changepoint, stl, panel_reg,
inequality, oaxaca_blinder, spatial, reporting_bias, hawkes, het_te
(causal forests), dml (double ML), sdid, mediation, climate, diffusion.
"""

from . import did, event_study, survival
from ._registry import EngineRegistry

__all__ = ["EngineRegistry", "did", "event_study", "survival"]
