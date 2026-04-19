"""Pluggable engines.

Each method family lives under its own subpackage with a Protocol +
frozen Result dataclass + registry. See
``docs/og_context/03_specs/engine_protocol.md`` for the contract.

Currently shipped families:

- :mod:`factor_factory.engines.did` — TwfeEngine + CallawaySantannaEngine
- :mod:`factor_factory.engines.survival` — KaplanMeierEngine + CoxPHEngine
- :mod:`factor_factory.engines.event_study` — MarketAdjustedEngine
- :mod:`factor_factory.engines.sdid` — SyntheticDidEngine (closes a
  Python-ecosystem gap; no mature pkg before this)
- :mod:`factor_factory.engines.mediation` — FourWayMediationEngine
  (VanderWeele 2014 — closes a Python-ecosystem gap)

Planned families (Phase 2): rdd, scm, changepoint, stl, panel_reg,
inequality, oaxaca_blinder, spatial, reporting_bias, hawkes, het_te
(causal forests), dml (double ML), climate, diffusion.

Deliberately out of scope: GWAS / biobank-scale genetics — different
ops world (HPC, BGEN/VCF formats, JVM-backed ``hail``). See
``docs/supported-domains.md`` for rationale.
"""

from . import did, event_study, mediation, sdid, survival
from ._registry import EngineRegistry

__all__ = ["EngineRegistry", "did", "event_study", "mediation", "sdid", "survival"]
