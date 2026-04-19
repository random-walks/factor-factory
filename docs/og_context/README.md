# `og_context/` — original-context handoff

Comprehensive design + spec + plan materials for `factor-factory`.
Authored during the design phase by the team that wrote
[blaise-website's `packages/python-showcase/`](https://github.com/random-walks/blaise-website/tree/main/packages/python-showcase)
showcase suite — the friction we hit there is the rationale for
this entire framework.

A new agent picking up this repo should be able to read this folder
end-to-end and have everything needed to implement v0.1 without
back-and-forth questions.

## What's in here

| File | Purpose |
|---|---|
| [`00_design_rationale.md`](00_design_rationale.md) | Why `factor-factory` exists. The pattern observation, the alternatives considered, the consumers. |
| [`01_architecture.md`](01_architecture.md) | Directory layout + Protocol pattern + optional-deps strategy + naming conventions. |
| [`02_implementation_plan.md`](02_implementation_plan.md) | Phase-by-phase roadmap (Phase 0 RFC → Phase 5 consumer cleanup) with acceptance gates per phase. |
| [`03_specs/`](03_specs/) | Detailed API specs per layer. Each is implementable in isolation. |
| [`04_downstream_changes.md`](04_downstream_changes.md) | What `nyc311`, `subway-access`, and `blaise-website`'s showcase suite must do once factor-factory v1.0 ships. |
| [`05_rfc_template.md`](05_rfc_template.md) | Template for engine-family RFCs (one per Phase 2 release). |

## Reading order

1. **`00_design_rationale.md`** — orientation. Why are we doing this?
2. **`01_architecture.md`** — what does the framework look like?
3. **`02_implementation_plan.md`** — what's the order of work?
4. **`03_specs/`** — pick whichever spec corresponds to the phase
   you're working on. They're cross-linked but self-contained.
5. **`04_downstream_changes.md`** — read once you've shipped enough
   for downstream consumers to start adopting; informs SemVer +
   migration timing.
6. **`05_rfc_template.md`** — copy-paste this whenever starting a
   new engine-family RFC.

## Provenance

Original design discussion happened in
[blaise-website PR #17](https://github.com/random-walks/blaise-website/pull/17)
(`packages/python-showcase`). Specifically:

- [`UPSTREAM_POSSIBLE_PACKAGES.md`](https://github.com/random-walks/blaise-website/blob/main/packages/python-showcase/UPSTREAM_POSSIBLE_PACKAGES.md) — the original PACKAGES #1 proposal
- [`UPSTREAM_ISSUES.md`](https://github.com/random-walks/blaise-website/blob/main/packages/python-showcase/UPSTREAM_ISSUES.md) — what's still upstream-pending after factor-factory ships
- [`FACTOR_FACTORY_PLAN.md`](https://github.com/random-walks/blaise-website/blob/main/packages/python-showcase/FACTOR_FACTORY_PLAN.md) — the originating plan doc; this `og_context/` folder expands and supersedes it

That conversation produced three blaise-website showcases
(`showcase-rat-containerization`, `showcase-resolution-equity`,
`showcase-subway-accessibility`) that are the **dogfood targets**
for factor-factory's first major version. Phase 3 of the
implementation plan rewrites those three showcases against
factor-factory; that's the acceptance signal that the framework is
ready for upstream consumer adoption (`nyc311`, `subway-access`).

## Decision log

Major decisions made during the design phase:

- **Naming**: `factor-factory` chosen over `anyfactor-lens`,
  `factorkit`, `panelforge`, `citypanel`, `lensfactor`, `facetkit`,
  `tidyfactor`, `factormill`. PyPI: `factor-factory`. Module:
  `factor_factory`.
- **Scope**: includes first-class jellycell integration baked into
  `factor_factory.jellycell.*` — absorbs what would otherwise have
  been a separate `tearsheet-studio` package. Reasoning: the
  scaffold-a-showcase-in-5-min capability is the multiplier that
  makes the framework worth doing.
- **License**: MIT, matching sibling random-walks packages.
- **Python**: `>=3.12` only. Matches current `nyc311`.
- **Optional engine deps**: every engine family is an extra
  (`[did]`, `[rdd]`, `[scm]`, etc.). Default install = tidy +
  diagnostics + jellycell only.
- **R-backed engines via rpy2**: deferred — Python-only for v0.1;
  revisit when we need `augsynth` or `rdmulti`/`rdlocrand`.
- **Backwards-compat shims in nyc311/subway-access**: kept for one
  major version (e.g., `nyc311 1.x` keeps the deprecated thin
  wrappers; `nyc311 2.0` drops them).
- **Versioning**: `v0.x` during dev; commit to v1.0 SemVer guarantees
  only after Phase 4 settles.

## Status

`v0.0.0`, design phase. Phase 0 = the RFC docs in this folder
(this is them). Phase 1 = repo skeleton + first DiD engine + jellycell
integration MVP. See [`02_implementation_plan.md`](02_implementation_plan.md)
for full phasing.
