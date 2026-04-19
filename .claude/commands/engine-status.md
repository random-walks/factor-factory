---
description: Report the 18-family engine roadmap status. Counts which families are shipping, which are stub-only, which are absent.
---

Read `factor_factory/engines/` and cross-reference against the 18 families listed in `docs/og_context/06_post_v0.1_roadmap.md` (did, survival, event_study, sdid, mediation + rdd, scm, het_te, dml, changepoint, stl, panel_reg, inequality, spatial, reporting_bias, hawkes, climate, diffusion).

For each family, determine status by inspecting the filesystem:

- **shipping** — `_base.py` exists, at least one adapter `.py` exists (not just `_base.py` or `__init__.py`), and there's ≥1 test file at `factor_factory/tests/test_engines/test_<family>_*.py`
- **scaffolded** — `_base.py` exists but no non-`_base` adapter file, or tests absent
- **absent** — no directory

Print a three-column markdown table: Family | Status | Adapters (comma-separated list of files found, or "—" if none). Sort by status (shipping first, then scaffolded, then absent) and then alphabetically within each bucket.

At the bottom print the summary line: `N / 18 shipping, M scaffolded, K absent.`

Do not modify files.
