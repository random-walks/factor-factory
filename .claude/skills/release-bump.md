---
name: release-bump
description: One-screen rubric for deciding patch vs minor vs major. Triggers when closing a PR or about to run /bump.
---

# Release bump rubric

Factor-factory follows jellycell's **minimum-bump** policy: patch bumps are cheap, hoard nothing. Cut releases frequently.

## Decision tree

```
Did the diff touch any contract invariant (Panel / Engine Protocol / Tearsheet JSON)?
├── Yes, but purely additive (new optional field, new adapter, new family) → minor
├── Yes, and breaking (renamed field, removed field, changed required signature) → major (post-1.0) OR minor (pre-1.0)
└── No contract touch → continue

Is the change user-visible (new public API, new cookbook-worthy behavior, new adapter)?
├── Yes → minor
└── No → continue

Is the change a bug fix, docs tidy, internal refactor, dep bump that isn't breaking, new fixture, new test?
└── Yes → patch
```

## Rules of thumb

- **When in doubt, patch.** You can always cut another release tomorrow.
- **"If the change is worth merging, it's worth a bump"** — even doc-only cleanups land under a patch bump once a week, not once a quarter.
- **Major bumps are expensive.** They force downstream adopters to read the CHANGELOG. Earn them.
- **Pre-1.0:** breaking changes are minor per SemVer convention; no majors until the first stable release cuts.
- **Post-1.0:** breaking contract changes are **always** major. No exceptions.

## Batch cadence during the v0.2 → v1.12 roadmap

Each batch in `docs/og_context/06_post_v0.1_roadmap.md` ends with a minor bump (new engine family or substantial framework addition). Intra-batch follow-up PRs use patch bumps.

## What goes into the CHANGELOG entry

Short. Specific. Link citations.

```
## [1.4.0] — 2026-05-15

### Added
- `engines.rdd.rd_robust` — Regression Discontinuity via `rdrobust`
  (Calonico-Cattaneo-Titiunik 2014, https://doi.org/10.3982/ECTA11757).
  Supports sharp + fuzzy RDD, MSE-optimal bandwidth, robust bias-corrected SEs.
```

Not:

```
- Added RDD stuff (#47)
```

## Final step

After running `/bump`, review the generated CHANGELOG section. Rewrite any thin "stuff" entries into specific claims with citations. Then `git commit`.
