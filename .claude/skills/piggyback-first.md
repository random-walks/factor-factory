---
name: piggyback-first
description: Before writing engine math from scratch, consult docs/reference/piggyback-map.md to confirm no canonical upstream package exists to wrap. Triggers when adding a new adapter or implementing a statistical method.
---

# Piggyback-first

Factor-factory is an **adapter-first** framework. Before you write any math:

1. Open `docs/reference/piggyback-map.md`. Search for the method name (e.g. "Callaway-Sant'Anna", "causal forest", "Mann-Kendall").
2. **If there's a row for it**, you wrap the package listed. Do not reimplement.
3. **If there's no row**, check whether a well-maintained Python or R package exists:
   - PyPI: `pip index versions <guess>` or `https://pypi.org/project/<guess>/`
   - R: CRAN task views + the canonical paper's code supplement
   - If you find one, add a row to the piggyback map and wrap it.
4. **Only port from scratch** (anti-piggyback) when:
   - No maintained Python equivalent exists AND
   - The R package is too tangled to wrap cleanly AND
   - The method is small enough (~100–300 LOC) to port correctly

## Current anti-piggybacks (existing homegrown ports)

- `engines.sdid.SyntheticDidEngine` — Arkhangelsky 2021. Reference: R `synthdid`. Partial Python ports (`pysdid`) were stale.
- `engines.mediation.FourWayMediationEngine` — VanderWeele 2014. Reference: R `CMAverse`. `statsmodels.stats.mediation` only supports the 2-component decomposition; PyPI `mediation` is stale.
- `engines.event_study.market_adjusted` — trivial math; dep-free by design.
- (Planned) `engines.reporting_bias.latent_em` — no mature Python package for two-class latent-EM under-reporting estimation.

## What "wrap, don't reimplement" means

The adapter must:
- Import the upstream package (guarded by a lazy try/except at the family `__init__.py` level so the extras gate works)
- Translate the Panel + kwargs into whatever shape the upstream expects
- Translate the upstream's result back into the frozen `<Family>Result` dataclass
- Preserve the upstream's numeric output verbatim — no homegrown bias corrections or tweaks without a citation

If you catch yourself writing matrix math in an adapter that wraps a package, you're probably doing it wrong. Pause and confirm the upstream doesn't already have that API.

## Update the map

Any new adapter → add a row:

```
| Method | Piggyback: `<pkg>` | <anti-piggyback reason if applicable> |
```

CHANGELOG `### Added` entry notes the piggyback in parens.
