# CLAUDE.md

Dense one-pager for agents working in this repo. Canonical wider guide is still [`AGENTS.md`](AGENTS.md) (AGENTS.md spec format, read by Cursor / Codex / Copilot / Aider / Zed). This file layers Claude-Code-specific conventions on top.

## Canonical contracts (§0.2 of the roadmap)

Three invariants. Breaking any of them = **major** version bump. Additive changes = **minor**. Everything else = **patch**. Full detail: [`docs/og_context/06_post_v0.1_roadmap.md#02-contract-invariants-lock-these-before-we-scale`](docs/og_context/06_post_v0.1_roadmap.md).

1. **Panel contract** — `docs/design-contracts.md`. Panel shape, `period_kind` variants, treatment-column naming, provenance.
2. **Engine Protocol contract** — `docs/og_context/03_specs/engine_protocol.md`. Frozen `<Family>Result` + `<Family>Engine` Protocol per family.
3. **Tearsheet JSON contract** — snapshot at `docs/reference/contracts.md`. `<family>_results.json` schema read by jellycell templates.

Touch a contract → bump the `SNAPSHOT_VERSION` in `docs/reference/contracts.md` + CHANGELOG `### Contracts` note. Run `/contract-check` before opening a PR.

## Piggyback-first

Before writing engine math, consult [`docs/reference/piggyback-map.md`](docs/reference/piggyback-map.md). We wrap; we don't reimplement. Two existing anti-piggybacks (`engines.sdid`, `engines.mediation`) document why.

## Pipeline dependency order

```
raw records → tidy → (factors) → diagnostics → engines → jellycell (reporting)
```

Higher layers may import lower layers; never the reverse. Violations fail review.

## Engine-family status + roadmap

| Shipping (v0.1) | Planned (v0.2+ — see roadmap) |
|---|---|
| did (twfe, callaway_santanna) | did (sun_abraham, borusyak_jaravel_spiess) — Batch 6 |
| survival (kaplan_meier, cox_ph) | survival (stratified) — Batch 6 |
| event_study (market_adjusted) | event_study (fama_french) — Batch 6 |
| sdid (synthetic_did) | rdd — Batch 7 |
| mediation (four_way, linear-linear) | scm (pysyncon, augmented) — Batch 8 |
| | het_te, dml — Batch 9 |
| | changepoint, stl, panel_reg — Batch 10 |
| | spatial, inequality, reporting_bias — Batch 11 |
| | hawkes, climate, diffusion — Batch 12 |

Run `/engine-status` to see the live status.

## Jellycell pin

Default deps pin `jellycell[server]>=1.4.0,<2`. Any turnkey integration work (tearsheet renderers, `cells.setup()` workaround, scaffold CLI) must stay compatible with this floor — which admits upstream `jellycell.tearsheets.*` (1.4.0+) alongside factor_factory's five fixed-schema renderers. See roadmap §0.4.

## Dev commands

```
make dev               # uv sync --all-extras --dev
make test              # full suite (~30s)
make lint              # ruff + mypy strict
make format            # ruff format + fix
make docs              # live Sphinx preview at :5190 (post-Batch-1)
make docs-build        # sphinx-build -W (CI mode)
make release-check     # preflight for tag push
```

## Claude slash-commands (`.claude/commands/`)

- `/engine-status` — 18-family roadmap progress
- `/bump [patch|minor|major]` — bump `_version.py` + roll CHANGELOG (stops before commit)
- `/contract-check` — diff-audit against the three contracts
- `/add-engine <family>` — scaffold a new engine family
- `/release-check` — preflight for tag push (no side effects)
- `/release [patch|minor|major] [--direct]` — full preflight + bump + commit + tag + open release PR (default); `--direct` pushes main + tag instead (needs permission rule)

## Skills (`.claude/skills/`) — always loaded as reminders

- `engine-protocol` — ceremony when touching `_base.py` or `Result` dataclasses
- `piggyback-first` — consult the map before writing math
- `fixture-parity` — every adapter needs a truth-tracking fixture + conformance test
- `release-bump` — patch/minor/major rubric
- `tearsheet-json-contract` — additive-safe / renaming-breaking

## Agent surface (scaffold CLI)

```
python -m factor_factory scaffold <dir>     # new showcase
factor-factory scaffold <dir>               # same, via entry point
```

Scaffolded showcase emits 5 jellycell tearsheets: METHODOLOGY, DIAGNOSTICS_CHECKLIST, FINDINGS, MANUSCRIPT, AUDIT.

## Versioning policy

**Frequent and small.** Target 1–2 releases per week during v0.2 → v1.12 fan-out. Patch is default. See `.claude/skills/release-bump.md`. During the v1.0 roadmap, batches merge as a single branch (`feat/v1.0-roadmap`) and release tags are cut afterwards in an ordered sweep — see roadmap §0.6.

## Pre-merge checklist (mirrors PR template)

- [ ] `make lint && make test && make docs-build` green
- [ ] `/contract-check` clean
- [ ] CHANGELOG `[Unreleased]` entry written
- [ ] New extras folded into `all`
- [ ] New engine → piggyback-map row + supported-domains row + cookbook stub + conformance fixture
- [ ] Citations (DOI + ref R pkg URL) in adapter docstring
