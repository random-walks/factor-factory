# Post-v0.1 Roadmap — Batched Execution Plan

> **Status:** Authoritative plan as of 2026-04-19, after PR #1 (Phase-1 skeleton + Phase-2 engine families + SDID + Mediation) merged to `main`.
>
> **How to use this doc:** Each batch below is a self-contained PR-sized unit of work. Attach this file to the Claude Code session that opens the batch, point at the batch heading, and execute. Batches are ordered by dependency — earlier batches unblock later ones. Within a batch, tasks are executed linearly unless otherwise noted.
>
> **Style:** aggressive on coverage, robust on craft. Every engine adapter ships with: (a) frozen `Result` dataclass + `Engine` Protocol + registry entry, (b) canonical-paper citation + reference-implementation URL in the engine docstring, (c) truth-tracking conformance fixture, (d) per-engine entry in `docs/supported-domains.md`, (e) CHANGELOG entry, (f) mypy-strict + ruff clean + filtered warnings.

---

## 0. Strategic shape of the plan

### 0.1 What "done" looks like

By the end of this roadmap, factor-factory has:

- **18 engine families shipping** (5 today + 13 new), each with ≥1 adapter, a registry-backed `estimate()` dispatcher, and a truth-tracking conformance test.
- **A Sphinx + Read the Docs site** at `factor-factory.readthedocs.io` with MyST-rendered user docs, `autodoc2`-generated API reference, a per-engine cookbook, and `sphinx-llms-txt` agent-surface (curated `llms.txt` + full `llms-full.txt`).
- **PyPI publication automated** via trusted-publisher OIDC (no stored tokens), with `release.yml` triggered on `v*` tags.
- **Cross-platform CI** (ubuntu + macos + windows, py3.12 + py3.13 + py3.14-on-release).
- **First-class Claude Code infrastructure** under `.claude/` — agents, commands, skills, `launch.json` — mirrored from jellycell's pattern and adapted to factor-factory's contracts.
- **Committed `uv.lock`** gating dependency drift.
- **A migration guide** walking the two known downstream adopters (nyc311, subway-access) through the v0.1 → v0.2 upgrade.
- **Property-based tests (hypothesis), snapshot tests, and performance benchmarks** guarding the core contracts.
- **All Priority 5 "nice-to-haves"** landed (async Socrata fetch, multi-geography panels, matrix-completion SCM, BCF, Quarto generator).

### 0.2 Contract invariants (lock these before we scale)

Factor-factory's equivalent of jellycell's `§10` contracts — **breaking any of these is the ONLY reason to bump major**:

1. **Panel contract** — the shape documented in `docs/design-contracts.md` (`panel_col_ordering`, `period_kind` variants, treatment-column naming, provenance metadata). Adding columns is non-breaking; renaming/reordering is breaking.
2. **Engine Protocol contract** — the `Engine` Protocol + frozen `Result` dataclass shape per family documented in `docs/og_context/03_specs/engine_protocol.md`. `Result.to_dict()` JSON schema is part of this — tearsheet renderers consume it.
3. **Tearsheet JSON contract** — `did_results.json` / `survival_results.json` / etc. schemas that jellycell tearsheet templates read. Downstream showcase projects pin these.

**Ceremony on touch:** bump `MINOR_VERSION` of the affected contract snapshot (stored as `docs/reference/contracts.md`), regenerate the JSON-schema snapshot fixture, add a CHANGELOG note under `### Contracts`. Enforced by a `spec-check` Claude slash-command (shipped in Batch 0).

### 0.3 Versioning policy (minimum-bump, jellycell-inspired)

Factor-factory will land more engine families more quickly than jellycell lands features. To avoid version churn without being irresponsible:

| Change type | Bump | Example |
|---|---|---|
| Bug fix, docs, refactor, non-breaking dep bump, new fixture, internal tightening | **patch** | `0.3.2 → 0.3.3` |
| New engine adapter, new engine family, new public API (non-breaking addition), new extras group | **minor** | `0.3.3 → 0.4.0` |
| Break any contract in §0.2 (Panel shape / Engine Protocol / Tearsheet JSON) | **major** | `0.4.0 → 1.0.0` |
| Pre-1.0 (v0.x): treat breaking changes as **minor** per SemVer pre-1.0 convention | **minor** | `0.3.3 → 0.4.0` |

Ship **frequently and small** — aim for ~1–2 releases per week during the engine fan-out phase. A batch from this roadmap usually ends in a minor bump; individual follow-up PRs usually end in patch bumps.

**Hit 1.0.0** after: (a) first downstream adopter migrated, (b) Sphinx/RTD live, (c) PyPI trusted-publisher wired, (d) uv.lock committed, (e) all three contracts frozen with snapshot + ceremony. That's end of **Batch 3**.

### 0.4 Jellycell integration pin

Factor-factory depends on `jellycell[server]>=1.3.5,<2`. The `1.3.5` floor is load-bearing because it contains:

- **#16** — `setup` cells are never cached (our `cells.setup()` workaround #J1 relies on this).
- **#17** — `jc.figure` path-only form (our `figure.from_path()` helper relies on this).
- **#18** — `run` + `export` honor `--project` (the scaffold CLI's monorepo support relies on this).
- **#19** — `jc.table` ergonomics + pyarrow default.
- **#20** — tearsheet tag filtering (our per-engine tearsheet templates depend on this for scoping).
- **#22** — kernel-iopub hang diagnostics + retry.
- **#23** — docs/examples audit.

Any turnkey jellycell-adjacent code we ship (tearsheet renderers, scaffold CLI, `cells.setup()`) should gate on this floor. Set it in `pyproject.toml` default-dependencies **and** in the scaffold-emitted `pyproject.toml.j2` template so downstream showcases inherit it.

### 0.5 Piggyback map (adapter-first policy)

Factor-factory follows jellycell's "piggyback-first" principle: before writing math, check whether a canonical Python or R package already implements it. We wrap; we don't reimplement. **Exceptions** are documented inline and require: (a) reason the piggyback fails (scale, licensing, missing/stale package), (b) canonical paper citation, (c) reference implementation URL.

| Method | Piggyback | Anti-piggyback (why we wrap, don't reimplement) |
|---|---|---|
| TWFE DiD | `linearmodels` | — |
| Callaway-Sant'Anna DiD | `differences` | — |
| Sun-Abraham, BJS DiD | `differences` (check) else port | **anti**: stale PyPI `did` package |
| KM / Cox PH / stratified Cox | `lifelines` | — |
| Fama-French event study | `pandas-datareader` for factors + `statsmodels` for regression | — |
| Market-adjusted event study | homegrown (dep-free by design) | trivial math; no dep justified |
| Regression Discontinuity | `rdrobust` | canonical Calonico-Cattaneo-Titiunik |
| Synthetic Control | `pysyncon` | — |
| Augmented SCM | `pysyncon` (check) else port | Ben-Michael-Feller-Rothstein 2021 |
| Matrix-completion SCM | `pysyncon` (check) else port | Athey-Bayati-Doudchenko-Imbens-Khosravi |
| Synthetic DiD (SDID) | **anti** — homegrown | no maintained Python equivalent; R `synthdid` is canonical |
| Four-way Mediation | **anti** — homegrown | R `CMAverse` is canonical; PyPI `mediation` is stale |
| Causal Forests | `econml` | — |
| DoubleML | `DoubleML` | — |
| BCF | `bcf-py` if maintained else port from R `bcf` | research frontier |
| Changepoint (offline) | `ruptures` | — |
| Changepoint (Bayesian online) | `bayesloop` | — |
| STL / Prophet | `sktime` + `prophet` | — |
| Panel regression (fixed-effects fleet) | `pyfixest` | Stata `reghdfe`-equivalent |
| Inequality decomposition | `inequality` | — |
| Spatial econometrics | `esda` + `libpysal` + `spreg` | — |
| Hawkes processes | `tick` | — |
| Climate (xclim + Mann-Kendall) | `xclim` + `pymannkendall` | — |
| Network diffusion | `ndlib` | — |

Keep this table in sync inside `docs/reference/piggyback-map.md` (created in Batch 1); CHANGELOG notes the addition/removal of any entry.

### 0.6 Execution mode — single long-lived branch

This roadmap is being executed as a single continuous stream of commits on `feat/v1.0-roadmap`. Each batch lands as one (or a few closely-related) commit(s) with a `batch-N:` prefix in the subject. Merging happens **once** at the end of Batch 16 rather than per-batch, so that downstream consumers don't churn against 16 interim tags. Tagged releases (`v0.2`, `v0.3`, ..., `v1.12`) are cut at the corresponding merge commits on `main` afterwards in a single ordered sweep.

---

## Batch 0 — Claude Code infrastructure + release-adjacent cleanups

**Goal:** stand up the `.claude/` folder, fold in jellycell-parity development ergonomics (`Makefile`, `CONTRIBUTING.md`, PR template), and close the loose ends that block the Sphinx/RTD batch.

**Size:** ~1 day, ~20 files touched / created. Minor bump (`0.1.0 → 0.2.0`).

**Deliverables**

1. **`.claude/settings.local.json`** — permission allowlist for safe dev commands:
   - `Bash(uv:*)`, `Bash(pytest:*)`, `Bash(ruff:*)`, `Bash(mypy:*)`, `Bash(sphinx-*:*)`, `Bash(make:*)`, `Bash(factor-factory:*)`, `Bash(git *)`, `WebFetch`, `WebSearch`.
2. **`.claude/launch.json`** — three preview servers:
   - `docs-preview` — `sphinx-autobuild docs docs/_build/html --port 5190 --watch factor_factory`
   - `tearsheet-preview` — scaffold a demo showcase, run its `01_load.py`, `jellycell view`
   - `pytest-watch` — `ptw` or `pytest --lf --watch` over `factor_factory/tests`
3. **`.claude/agents/`** (2 agents):
   - **`engine-reviewer.md`** (sonnet) — review new engine PRs against the Protocol contract (frozen `Result`, registry registration, conformance fixture, citation in docstring, CHANGELOG entry, supported-domains.md row). Tools: `Glob, Grep, Read, Bash` (read-only).
   - **`contract-auditor.md`** (sonnet) — diff-only review against the three §0.2 contracts. Flags ceremony omissions. Read-only.
4. **`.claude/commands/`** (5 slash-commands):
   - **`/bump`** — parse arg (`patch|minor|major`, default patch), bump `factor_factory/_version.py`, move `[Unreleased]` block in CHANGELOG to the new version heading, open a suggested commit.
   - **`/engine-status`** — count shipped families vs the 18-family target; report next-up.
   - **`/contract-check`** — run the contract-auditor agent on the current diff.
   - **`/add-engine`** — interactive wizard that scaffolds a new engine family (create `engines/<family>/` with `_base.py`, `__init__.py`, adapter stub, conformance-test stub, fixture stub, CHANGELOG note, extras entry in `pyproject.toml`, `supported-domains.md` row). Mirrors jellycell's `/bump` pattern.
   - **`/release-check`** — preflight for a tag push: lint, test, docs build (`-W`), `hatch build`, version print, ensure CHANGELOG has no `[Unreleased]` left.
5. **`.claude/skills/`** (5 skills, mirroring jellycell's ergonomic-nudge pattern):
   - **`engine-protocol.md`** — pre-edit ceremony checklist when touching anything under `engines/<family>/_base.py` or `_registry.py`. Links the three contracts.
   - **`piggyback-first.md`** — nudge Claude to consult `docs/reference/piggyback-map.md` before writing engine math. Anti-piggybacks listed (SDID, mediation).
   - **`fixture-parity.md`** — reminder that every new engine needs a truth-tracking cross-domain fixture in `_fixtures/cross_domain.py` + parametrized conformance test.
   - **`release-bump.md`** — one-screen version-bump rubric (see §0.3).
   - **`tearsheet-json-contract.md`** — reminder that `to_dict()` shape is a downstream contract; adding keys is fine, renaming/removing is breaking.
6. **`CONTRIBUTING.md`** (top-level) — dev-setup, pre-merge checklist (lint / test / docs-build / docstrings / contract-touch-filled / CHANGELOG entry), RFC pointer (`docs/og_context/05_rfc_template.md`).
7. **`.github/PULL_REQUEST_TEMPLATE.md`** — short, non-bureaucratic:
   - Summary (1–3 bullets)
   - Batch ref (link to this doc + batch number)
   - Contract touches (Panel / Engine Protocol / Tearsheet JSON — tick box + ceremony done)
   - CHANGELOG updated
   - New extras / new family extras folded into `all` extras
8. **`Makefile`** — parity with jellycell:
   - `make dev` — `uv sync --all-extras --dev`
   - `make test`, `make test-engines`, `make test-cross-domain`
   - `make lint` — `ruff check && ruff format --check && mypy`
   - `make format` — `ruff format && ruff check --fix`
   - `make docs` — `sphinx-autobuild` (Batch 1 lands `docs/conf.py`; pre-Batch-1 this target prints a TODO)
   - `make docs-build` — `sphinx-build -W --keep-going`
   - `make release-check` — invoke the slash-command equivalent
   - `make clean` — remove `dist/`, `build/`, `docs/_build/`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`
9. **`CLAUDE.md` rewrite** — promote from stub to a dense one-pager like jellycell's: contracts, piggyback-first, dependency/layer order, dev commands, engine-family status table, agent surface (scaffold CLI flags), versioning policy.
10. **`docs/reference/piggyback-map.md`** — the table from §0.4, with a short preamble.
11. **Cleanup**: fix the Panel `validate()` always-on O(n) cost TODO and the `_attach_treatment_columns` private-path TODO are **deferred to Batch 4**; don't bundle here.

**Acceptance:** `/engine-status` and `/contract-check` run end-to-end. `make lint && make test` green. A fresh-clone developer can run `make dev && make test` and land in a working state.

---

## Batch 1 — Sphinx + Read the Docs site

**Goal:** consolidate the Markdown user docs into a browseable, versioned, search-indexed Sphinx site with auto-generated API reference and agent-surface (`llms.txt`).

**Size:** ~1–2 days, ~15 files touched/created. Minor bump (`0.2.0 → 0.3.0`).

**Deliverables**

1. **`docs/conf.py`** — Sphinx config:
   - Theme: `furo` (match jellycell).
   - Extensions: `sphinx.ext.intersphinx`, `myst_parser`, `autodoc2`, `sphinx_design`, `sphinx_copybutton`, `sphinxcontrib.bibtex`, `sphinx_llms_txt`.
   - `autodoc2_packages = ["factor_factory"]`, render output to `docs/apidocs/` as markdown, hide `__private`, hide `__dunder__`, skip `__main__`.
   - MyST extensions: `colon_fence, deflist, fieldlist, tasklist, linkify, substitution`; heading anchors depth 3.
   - Intersphinx: `python`, `pandas`, `numpy`, `scipy`, `matplotlib`, `jellycell`.
   - `sphinx-llms-txt`: curated `llms.txt` excludes `apidocs/**`; `llms-full.txt` includes everything.
   - `bibtex_bibfiles = ["references.bib"]` — bib entries for every canonical paper we cite (Arkhangelsky 2021, VanderWeele 2014, Callaway-Sant'Anna 2021, Sun-Abraham 2021, Calonico-Cattaneo-Titiunik 2014, etc.).
2. **`.readthedocs.yaml`** — Ubuntu 22.04, Python 3.12, `fail_on_warning: true`, `pip install . .[docs,all]`.
3. **`docs/index.md`** — Landing page: one-paragraph framing, "what's shipping today" matrix (linked to pages), install snippet, "where to next" (getting-started / supported-domains / engine cookbook / API reference).
4. **`docs/getting-started.md`** (migrate existing) — unchanged structure; MyST-formatted.
5. **`docs/supported-domains.md`** (migrate existing).
6. **`docs/design-contracts.md`** (migrate existing) — canonical Panel/TreatmentEvent/Provenance contract.
7. **`docs/jellycell-integration.md`** (migrate existing).
8. **`docs/reference/contracts.md`** — the three §0.2 contracts with **snapshot JSON schemas** auto-generated from the Result dataclasses + Panel attributes. This file is the `MINOR_VERSION` gate (ceremony on touch).
9. **`docs/reference/architecture.md`** — the 6-layer pipeline (tidy → factors → diagnostics → engines → reporting + jellycell), with the piggyback map inline.
10. **`docs/reference/piggyback-map.md`** — promoted to a first-class page.
11. **`docs/development/`** (5 pages):
    - `contributing.md` (summary + link to top-level `CONTRIBUTING.md`)
    - `adding-an-engine.md` (step-by-step: copy `engines/sdid/` shape, `/add-engine` wizard, conformance fixture, CHANGELOG, extras, supported-domains row, cookbook page)
    - `releasing.md` (the §0.3 policy, the PyPI trusted-publisher workflow, pre-release checklist)
    - `dev-setup.md` (`make dev`, editor hints, mypy/ruff knobs)
    - `testing.md` (pytest layout, hypothesis, snapshot, benchmarks)
12. **`docs/cookbook/`** (1 page per shipped engine, stub + 2–3 worked examples each — fleshed out in later batches):
    - `did-twfe.md`, `did-callaway-santanna.md`, `survival-km.md`, `survival-cox.md`, `event-study-market-adjusted.md`, `sdid.md`, `mediation-four-way.md`.
13. **`docs/apidocs/`** — generated by `autodoc2`, committed so RTD builds it (or `.gitignore`d + built at RTD time — match jellycell's choice).
14. **`pyproject.toml`** — add `docs` extra with pinned Sphinx stack.
15. **CI**: new `docs` job runs `sphinx-build -W --keep-going` and uploads HTML artifact.

**Acceptance:** `make docs` serves locally; `make docs-build` passes with `-W`; RTD builds green on a staging branch; the curated `llms.txt` is reachable from the RTD URL.

---

## Batch 2 — PyPI release infrastructure + uv.lock

**Goal:** make `v*` tags cut a PyPI release without human intervention.

**Size:** ~0.5 day, ~8 files. Minor bump (`0.3.0 → 0.4.0`). **Do not release yet** — bake for one week on `main` first.

**Deliverables**

1. **PyPI trusted publisher (OIDC)** — one-time manual config on PyPI project page (not automated). Document in `docs/development/releasing.md`.
2. **`.github/workflows/release.yml`**:
   - Trigger: `push` tags matching `v*`.
   - Jobs: `build` (`uv build` → sdist + wheel) → `publish` (`pypa/gh-action-pypi-publish` via OIDC) → `github-release` (attach artifacts + pull release notes from CHANGELOG section via `scripts/extract_release_notes.py`).
3. **`uv.lock`** — checked in for the first time; CI switches from `uv pip install -e .[...]` to `uv sync --frozen`.
4. **`scripts/extract_release_notes.py`** — pull the `[vX.Y.Z]` section from `CHANGELOG.md`, print to stdout. Used by `release.yml`.
5. **CHANGELOG footer** — comparison-link table (`[unreleased]: ...compare/vX.Y.Z...HEAD`), keep-a-changelog style.
6. **`docs/development/releasing.md`** — expand with: first-release (v1.0.0) checklist, subsequent-release checklist, how to hotfix, how to yank.
7. **`CITATION.cff`** — Zenodo-style citation file at repo root. Citations for SDID + Mediation engines link to the canonical papers.

**Acceptance:** a dry-run `act -j build` succeeds locally; the real trigger is deferred until Batch 3 bakes a week on main.

---

## Batch 3 — Cross-platform CI + v1.0.0 release

**Goal:** broaden the CI matrix, fix anything mac/windows-specific, then cut the first PyPI release.

**Size:** ~1 day + 1 week of baking. Bump to `1.0.0` (major, per §0.3 — first stable release once all three contracts are frozen).

**Deliverables**

1. **CI matrix** — add `macos-latest` and `windows-latest` runners for the `test` job. Add `python-3.14` if released by the date of this batch (as of 2026-04-19 it should be; if not, drop).
2. **Windows shim work** — expect `pathlib` / `line-ending` issues with the jellycell scaffold CLI and the parquet round-trip. Fix or skip with `pytest.mark.skipif(sys.platform == 'win32', reason=...)` + issue filed.
3. **Mac ARM shim work** — `pyarrow`, `shapely`, `geopandas` wheels are usually fine on ARM64 now; a CI-only reveal.
4. **Contract snapshot freeze** — run the `autodoc2`-backed JSON-schema extractor, commit the snapshots to `docs/reference/contracts.md` with `SNAPSHOT_VERSION = "1.0.0"`.
5. **CHANGELOG** — write the v1.0.0 entry summarizing everything through Batch 3; credit SDID/Mediation gaps closed; link Arkhangelsky 2021 + VanderWeele 2014 DOIs.
6. **Tag + release** — `git tag v1.0.0 && git push --tags`. `release.yml` fires, PyPI gets the first release, GitHub Release is auto-populated.

**Acceptance:** `pip install factor-factory[all]` works on a fresh venv on all three OSes. RTD shows "v1.0.0" and "latest" versions.

---

## Batch 4 — Framework polish pass

**Goal:** graduate the Priority-3 "tighten the edges" items into public API before any more engines land.

**Size:** ~1 day, ~10 files. Minor bump (`1.0.0 → 1.1.0`). No contract breaks — every change is additive.

**Deliverables**

1. **`Panel.attach_treatment_columns()`** — promote `_attach_treatment_columns` from module-private to a public `Panel` instance method. Keep the underscore alias as a deprecation shim for one minor-release cycle.
2. **`Panel.validate(strict: bool = True)`** — add `strict=False` fast-path that skips O(n) integrity checks and runs only the O(1) shape checks. `Panel.from_records(..., validate=False)` is equivalent.
3. **`record_view_columns` schema validation** — in `from_records`, raise a crisp `ValueError` listing the missing columns instead of silently returning `None`s.
4. **`Panel.summary()`** — returns a dict: `{n_units, n_periods, freq, period_kind, n_treatment_events, treated_unit_share, n_outcomes, n_records, provenance}`. Used by tearsheet renderers and notebooks.
5. **`summary_table()` parity** — add to `SurvivalResults`, `EventStudyResults`, `SdidResults`, `MediationResults`. Each returns a pandas DataFrame with a stable column schema (add to the Tearsheet-JSON contract snapshot).
6. **Cross-engine tearsheet templates** — expand `findings.md.j2` with per-family blocks: DiD / Survival / Event Study / SDID / Mediation. The dispatch keys off a `family` field in each `*_results.json`.
7. **Tests** — every item above gets a focused unit test.

**Acceptance:** tearsheet renders a full-engine-zoo showcase with per-family blocks populated end-to-end.

---

## Batch 5 — SDID and Mediation completeness

**Goal:** finish the two gap-closers at production quality.

**Size:** ~2 days, ~12 files. Minor bump (`1.1.0 → 1.2.0`).

**Deliverables**

1. **SDID placebo inference** — for the single-treated-unit case, replace the current first-differences `sigma` fallback with proper placebo-test inference (permute the treatment assignment across controls, refit, build the null distribution of the ATT estimator). Matches the R `synthdid` placebo-test option.
2. **SDID placebo-test option for multi-treated panels** — add `estimate(..., inference="jackknife" | "placebo")`. Jackknife stays default for `n_treated ≥ 2`.
3. **SDID AER Prop-99 validation** — add a `tests/test_sdid_prop99.py` that reproduces Arkhangelsky 2021 Table 2, California-Prop-99-cigarettes, and asserts ATT + SE within published tolerance. Fixture data: either a pinned download from the `synthdid` R package's vendored CSV or a checked-in copy under `factor_factory/tests/_fixtures/prop99.csv` (small enough to commit).
4. **Logistic-outcome / logistic-mediator mediation** — port VanderWeele 2014 §3. Monte-Carlo integration over the mediator distribution; `n_draws = 1000` default with seeded RNG. Adds `FourWayMediationEngine(outcome_family="linear" | "logistic", mediator_family="linear" | "logistic")`.
5. **Mediation sensitivity analysis (rho-test)** — port the sensitivity-to-unobserved-confounding check from R `CMAverse`. `MediationResult.sensitivity(rho=np.linspace(-0.5, 0.5, 21))` returns a DataFrame with the component estimates as a function of the unmeasured-confounding correlation.
6. **Docs**: expand `docs/cookbook/sdid.md` with the Prop-99 example; expand `docs/cookbook/mediation-four-way.md` with logistic + sensitivity.

**Acceptance:** Prop-99 test passes within tolerance quoted in AER Table 2; logistic-logistic fixture recovers the four components within 1.5 SE.

---

## Batch 6 — DiD completeness + Cox stratification + FF event study

**Goal:** close the remaining Priority-2 items on already-shipping engine families.

**Size:** ~2 days, ~14 files. Minor bump (`1.2.0 → 1.3.0`).

**Deliverables**

1. **Sun-Abraham adapter** (`engines.did.sun_abraham`) — wrap `differences` if it already implements it; else port from the Sun-Abraham 2021 JoE paper. Conformance fixture against a known-staggered-ATT panel.
2. **Borusyak-Jaravel-Spiess adapter** (`engines.did.borusyak_jaravel_spiess`) — same pattern.
3. **`estimate(..., methods=("twfe", "cs", "sa", "bjs"))`** — all four DiD adapters composable in one call.
4. **Stratified Cox PH** — surface `lifelines`' `strata=` kwarg in `CoxPHEngine`. Conformance test: a two-stratum fixture where strata misuse would bias HR.
5. **Fama-French market-model event study** (`engines.event_study.fama_french`) — FF3 / FF5 / Carhart-4 residuals; Patell-z + BMP tests. Uses `pandas-datareader` to pull Ken French's data library; cache aggressively (`~/.cache/factor_factory/ff_factors.parquet`) because the upstream endpoint is flaky. Fallback: ship a pinned snapshot of the factor data under `factor_factory/_data/` and use it if the download fails.
6. **Event-study `estimate(..., method="market_adjusted" | "fama_french")`** dispatcher.

**Acceptance:** staggered-ATT fixture recovers the true ATT more accurately with SA/BJS than with TWFE (as expected under heterogeneity); FF event study reproduces a known CAR from a published earnings-announcement study within a few bps.

---

## Batch 7 — Engine family: RDD (`engines.rdd`)

**Goal:** first net-new engine family post-v0.1.

**Size:** ~1 day, ~8 files. Minor bump (`1.3.0 → 1.4.0`).

**Deliverables**

1. **`engines/rdd/_base.py`** — `RddResult` + `RddEngine` Protocol. Result captures: `estimate`, `std_error`, `bandwidth_used`, `bias_correction`, `kernel`, `n_effective`, `first_stage_f` (if fuzzy RDD), `covariate_balance_pvalues`.
2. **`engines/rdd/rd_robust.py`** — `RdRobustEngine` wrapping `rdrobust`. Expose `c` (cutoff), `p` (poly order), `kernel`, `bwselect` (mserd / msetwo / msesum / msecomb1 / msecomb2), `covs`, `fuzzy`, `cluster`. Conformance fixture: sharp RDD with known jump; fuzzy RDD with known LATE.
3. **`engines/rdd/plots.py`** — standard RDD plot (binned scatter + local-polynomial fit on each side of the cutoff) via matplotlib.
4. **`_fixtures/cross_domain.py`** — add `rdd_education_cutoff_panel()` (test-score cutoff determines scholarship → earnings outcome) and `rdd_geographic_discontinuity_panel()` (policy changes at a geographic boundary).
5. **`supported-domains.md`** — add RDD column + rows to applicable domains (education, policy evaluation, clinical dosing thresholds).
6. **`docs/cookbook/rdd.md`** — two worked examples (one sharp, one fuzzy).
7. **Conformance test** against the fixtures + a snapshot of `rdrobust`'s canonical senate-election example.

**Acceptance:** sharp-RDD fixture recovers the known jump within 1 SE; fuzzy-RDD recovers the known LATE within 1.5 SE.

---

## Batch 8 — Engine family: SCM (`engines.scm`)

**Goal:** classic Abadie synthetic-control + the Ben-Michael augmented SCM frontier.

**Size:** ~1.5 days, ~10 files. Minor bump (`1.4.0 → 1.5.0`).

**Deliverables**

1. **`engines/scm/_base.py`** — `ScmResult` + `ScmEngine` Protocol. Result captures: `att`, `std_error`, `donor_weights`, `predictor_weights`, `pre_period_rmspe`, `post_period_rmspe`, `placebo_pvalue`.
2. **`engines/scm/pysyncon_adapter.py`** — `PysynconEngine` wrapping `pysyncon`. Supports V-matrix optimization options (`optim_method`, `optim_initial`). Permutation inference for p-value.
3. **`engines/scm/augmented.py`** — `AugmentedScmEngine`. If `pysyncon` supports augmented-SCM (check at implementation time), wrap it; else port from Ben-Michael-Feller-Rothstein 2021 (ridge-regression outcome model bias correction on top of the classic SCM fit). Keep this deliberate-wrap-first per §0.4.
4. **Fixture**: `scm_single_treated_state_panel()` — one treated state, many donor states, known treatment effect. Mirror of the canonical California-Prop-99 shape (but synthetic to avoid reusing the SDID Prop-99 fixture).
5. **Conformance test**: recover known ATT within 1 SE; placebo p-value < 0.1 under the alternative.
6. **`docs/cookbook/scm.md`** — worked examples, comparison to SDID.

**Acceptance:** on the SDID Prop-99 fixture, classic SCM recovers a similar ATT to what Abadie-Gardeazabal-Hainmueller 2003 got; the augmented SCM dampens the pre-period fit mismatch visible in the trajectory plot.

---

## Batch 9 — Causal-ML families: `engines.het_te` + `engines.dml`

**Goal:** modern heterogeneous-effects + double-ML.

**Size:** ~2 days, ~14 files. Minor bump (`1.5.0 → 1.6.0`).

**Deliverables**

1. **`engines/het_te/_base.py`** — `HetTeResult` + `HetTeEngine`. Result captures: `ate`, `ate_std_error`, `cate_predictions` (np array), `cate_std_errors`, `treatment_effect_heterogeneity_pvalue`, `feature_importances`, `nuisance_learner_scores`.
2. **`engines/het_te/causal_forest.py`** — `CausalForestEngine` wrapping `econml.dml.CausalForestDML`. Options: `discrete_treatment`, `n_estimators`, `min_samples_leaf`, `model_y`, `model_t` (sklearn-compatible).
3. **`engines/het_te/x_learner.py`** + **`engines/het_te/r_learner.py`** — thin wrappers over `econml.metalearners.XLearner` and `econml.dr.DRLearner` for apples-to-apples comparison.
4. **`engines/dml/_base.py`** — `DmlResult` + `DmlEngine`.
5. **`engines/dml/plr.py`** — partially-linear-regression DML via the `DoubleML` package. Options for score function (`IV-type` / `partialling-out`), nuisance learners (`model_l`, `model_m`).
6. **`engines/dml/irm.py`** — interactive-regression-model DML (binary treatment + continuous outcome).
7. **Fixtures**: `het_te_pricing_experiment_panel()` (binary treatment × continuous covariate that modulates effect); `dml_confounded_observational_panel()` (strong confounding where OLS fails but DML recovers).
8. **Docs**: `docs/cookbook/het-te-causal-forest.md`, `docs/cookbook/dml.md` with clear when-to-use guidance (RCT vs observational vs heterogeneous effects).
9. **CI note**: `econml` install is ~200 MB — split into its own CI job matrix entry to keep the mainline test job fast.

**Acceptance:** causal forest CATE variance is meaningfully higher on the heterogeneous fixture than on the homogeneous one; DML recovers ATE within 1 SE on the confounded fixture where OLS is biased by > 3 SE.

---

## Batch 10 — Time-series families: `engines.changepoint` + `engines.stl` + `engines.panel_reg`

**Goal:** offline+online changepoint detection, seasonal decomposition + forecasting, high-dimensional fixed-effects regression.

**Size:** ~2 days, ~18 files. Minor bump (`1.6.0 → 1.7.0`).

**Deliverables**

1. **`engines/changepoint/_base.py`** — `ChangepointResult` + `ChangepointEngine`. Captures: `changepoints` (list of period indices), `regime_means`, `confidence` (posterior probability or BIC-style score), `model`.
2. **`engines/changepoint/ruptures_adapter.py`** — Pelt / BinSeg / Window / Dynp via `ruptures`. `model="l1" | "l2" | "rbf"`, `pen` tuning.
3. **`engines/changepoint/bayesloop_adapter.py`** — online Bayesian changepoint detection via `bayesloop`.
4. **`engines/stl/_base.py`** — `StlResult` + `StlEngine`. Captures: `trend`, `seasonal`, `residual`, `forecast`, `forecast_interval`.
5. **`engines/stl/sktime_stl.py`** — `sktime`'s `STLForecaster`.
6. **`engines/stl/prophet_adapter.py`** — `prophet`, with holidays + regressors.
7. **`engines/panel_reg/_base.py`** — `PanelRegResult` + `PanelRegEngine`.
8. **`engines/panel_reg/pyfixest_adapter.py`** — `pyfixest`'s `feols` for arbitrary fixed-effects + IV + clustered SEs. Reghdfe-equivalent.
9. **Fixtures**: `changepoint_structural_break_panel()`, `stl_seasonal_demand_panel()`, `panel_reg_hdfe_earnings_panel()`.
10. **Docs**: one cookbook page per family.

**Acceptance:** changepoint fixture recovers the known break within 2 periods; STL fixture recovers the seasonal amplitude within 5%; panel_reg fixture recovers a coefficient within 1 SE of the DGP truth across 3+ fixed-effect dimensions.

---

## Batch 11 — Spatial + inequality + reporting-bias

**Goal:** three small-surface families that share an ops pattern.

**Size:** ~1.5 days, ~14 files. Minor bump (`1.7.0 → 1.8.0`).

**Deliverables**

1. **`engines/spatial/_base.py`** + three adapters:
   - `spatial/morans_i.py` — `esda.Moran` global + local autocorrelation.
   - `spatial/spreg_ols.py` — spatial lag / spatial error models via `spreg`.
   - `spatial/libpysal_weights.py` — weights builders (queen, rook, KNN, distance-band).
2. **`engines/inequality/_base.py`** + `theil.py` — Theil T, Theil L, Atkinson, Gini via the `inequality` package. Between/within decompositions for grouped panels.
3. **`engines/reporting_bias/_base.py`** + `latent_em.py` — two-class latent-EM estimator for under-reporting rates (a staple in civic-data work: "what's the true rate if agencies under-report?"). Homegrown; no mature Python package.
4. **Fixtures**: `spatial_crime_panel()`, `inequality_wages_panel()`, `reporting_bias_311_panel()`.
5. **Docs**: three cookbook pages.

**Acceptance:** Moran's I on a known-clustered fixture recovers a significant positive value; Theil decomposition sums to the known total inequality; latent-EM recovers the known under-reporting rate within 5%.

---

## Batch 12 — Hawkes + climate + diffusion

**Goal:** three "exotic" families with lightly-used-in-practice but Python-available libraries.

**Size:** ~1.5 days, ~14 files. Minor bump (`1.8.0 → 1.9.0`).

**Deliverables**

1. **`engines/hawkes/_base.py`** + `tick_adapter.py` — multivariate Hawkes processes via `tick`. For network cascades, trading microstructure, crime hotspotting. Captures: `baseline_intensities`, `excitation_matrix`, `branching_ratio`, `log_likelihood`.
2. **`engines/climate/_base.py`** + `xclim_adapter.py` + `mann_kendall.py` — `xclim` climate indices (growing-degree-days, heatwave-frequency, precipitation-anomaly, etc.); `pymannkendall` trend tests (classic, Hamed-Rao, Yue-Wang).
3. **`engines/diffusion/_base.py`** + `ndlib_adapter.py` — SI / SIR / SEIR / Threshold / Independent-Cascade models via `ndlib`. For adoption cascades on explicit graphs.
4. **Fixtures**: already have `network_diffusion_panel`; add `climate_anomaly_panel` extension + `hawkes_contagion_panel`.
5. **Docs**: three cookbook pages.

**Acceptance:** Hawkes fixture recovers the known branching ratio within 10%; xclim recovers the known GDD aggregate; ndlib simulates to the known equilibrium prevalence.

---

## Batch 13 — Framework deep-cuts: streaming, async, multi-geography

**Goal:** three Priority-5 "nice-to-have" framework changes that unblock large-data and multi-scale work.

**Size:** ~2 days, ~12 files. Minor bump (`1.9.0 → 1.10.0`).

**Deliverables**

1. **Streaming `Panel.from_records`** — chunked-builder pattern. New `PanelBuilder` class that accepts iterables of record chunks, accumulates treatment events, and emits a single `Panel` at `.build()`. Memory-bounded by a configurable buffer; spills to parquet scratch when exceeded. Target: 10M records on a 16 GB machine.
2. **Async Socrata bulk fetch** — `tidy.socrata.bulk_fetch_async(...)` using `httpx.AsyncClient`. Concurrency cap, retry-with-jitter, progress bar via `rich`. Synchronous wrapper stays default; async is opt-in.
3. **Multi-geography panels** — drop the single-`dimension` assumption. `Panel.from_records(..., dimensions=("community_district", "station_id"))` builds a hierarchical panel (outer dimension dominates; inner dimension is the fine-grained unit). `RecordView` and treatment-column attachment handle both levels. Diagnostics know which level they operate on.
4. **Contract impact** — this touches the Panel contract (§0.2 invariant #1). Bump `MINOR_VERSION` in `docs/reference/contracts.md`. Changes are **additive** — existing single-dimension panels still validate.
5. **Docs**: `docs/cookbook/streaming-large-panels.md`, `docs/cookbook/async-fetch.md`, `docs/cookbook/multi-geography.md`.

**Acceptance:** 10M-record streaming test fits in < 4 GB peak RSS; async fetch over 100 chunks is ≥ 5× faster than sync on the same endpoint; a two-level panel fits a TWFE DiD at the station level with community-district fixed effects cleanly.

---

## Batch 14 — Testing + benchmarks + migration guide

**Goal:** Priority-4 in full.

**Size:** ~1.5 days, ~20 files. Patch bumps as the individual PRs land (no new public API).

**Deliverables**

1. **`hypothesis`-based property tests** — `factor_factory/tests/properties/test_panel_properties.py`:
   - Random well-formed panels always validate.
   - Random malformed panels always raise.
   - `Panel.summary()` is invariant under record shuffling.
   - Treatment-column attachment is idempotent.
   - `Panel.attach_treatment_columns()` followed by a round-trip via parquet preserves every invariant.
2. **Snapshot tests for tearsheets** — `pytest-regressions` (jellycell uses this). Render the demo showcase's 5 tearsheet files; commit snapshots; fail on drift. One snapshot set per engine family.
3. **`pytest-benchmark`** — benchmark `Panel.from_records` on a 100k-record fixture and engine fits on a 10k-record fixture. CI job flags > 2× regressions.
4. **Per-engine cookbook expansion** — fill in each `docs/cookbook/*.md` to ~10 worked examples (one per headline domain per family).
5. **Migration guide for nyc311 / subway-access** — `docs/migration/v0-to-v1.md` with concrete before/after PR snippets. Identify the two import paths and public-API names that changed (only `Panel.attach_treatment_columns` and `Panel.validate(strict=...)` in Batch 4).
6. **AER Prop-99 SDID validation** — already landed in Batch 5; re-verify here as a regression gate.

**Acceptance:** `pytest -m property` runs 100+ hypothesis examples per test; snapshot tests catch an intentional-drift change and pass after update; benchmark CI job posts run-over-run comparisons to PR comments.

---

## Batch 15 — Research-frontier extras: BCF, matrix-completion SCM, Quarto generator

**Goal:** Priority-5 tail — high-optionality, low-required-urgency items.

**Size:** ~2 days, ~18 files. Minor bump (`1.10.0 → 1.11.0`).

**Deliverables**

1. **Bayesian Causal Forests (`engines.het_te.bcf`)** — Hahn-Murray-Carvalho 2020. If a maintained `bcf-py` package exists, wrap it; else port the linear-Gaussian case from the paper. Conformance fixture mirrors the causal-forest fixture for comparability.
2. **Matrix-completion SCM (`engines.scm.matrix_completion`)** — Athey-Bayati-Doudchenko-Imbens-Khosravi 2021. `pysyncon` may already provide this; check first.
3. **Quarto / RMarkdown report generator** — `factor_factory.reporting.quarto`. New `.qmd` template that consumes the same tearsheet JSON the jellycell renderers use. Gives consumers who don't want jellycell an alternative. Shipped as an opt-in extra `factor-factory[quarto]` (no runtime deps beyond `jinja2` — quarto itself is a system dep).
4. **Docs**: cookbook pages for each.

**Acceptance:** BCF fixture recovers the known heterogeneous effect within 1 SE; matrix-completion SCM matches the published ATT on the canonical example; the Quarto template renders to a standalone HTML/PDF report from the same inputs as the jellycell tearsheet.

---

## Batch 16 — Final polish + 1.12 release

**Goal:** capstone. Everything left over from Priorities 1–5 that hasn't landed.

**Size:** ~1 day, ~10 files. Minor bump (`1.11.0 → 1.12.0`). Announce "roadmap complete" in the CHANGELOG + a short blog post (or README notice).

**Deliverables**

1. **CS-adapter cluster fix** — stop silently dropping `cluster=`; accept it and pass it correctly.
2. **CS-adapter period-kind expansion** — if the upstream `differences` package has added support for float / ordinal periods since we last checked, enable them.
3. **`dev` + `all` extras sanity** — `factor-factory[all,dev]` install on a clean Py 3.13 venv passes every test.
4. **Sphinx site review pass** — rewrite any cookbook pages that still read like stubs; add a "FAQ" page; add a "comparison to R ecosystem" page (for each engine, link the R package we piggyback/port from and compare feature parity).
5. **Contribution-experience review** — run through the "add an engine" flow cold (as a fake outside contributor); tighten any rough edges in `/add-engine`, `docs/development/adding-an-engine.md`.

**Acceptance:** a fresh-clone developer can open `/add-engine` → answer 5 questions → land a boilerplate PR that passes CI, against a newly-added engine family, in under an hour.

---

## Appendix A — Per-batch checklist (copy this into every PR description)

```
- [ ] Batch ref: `docs/og_context/06_post_v0.1_roadmap.md#batch-N`
- [ ] New engine family? → `_base.py` (frozen Result + Protocol), registry entry, conformance fixture, citation in docstring
- [ ] New piggyback dependency? → row added in `docs/reference/piggyback-map.md`
- [ ] Contract touch (Panel / Engine Protocol / Tearsheet JSON)? → `MINOR_VERSION` bumped in `docs/reference/contracts.md`; snapshot regenerated; CHANGELOG §Contracts note
- [ ] CHANGELOG `[Unreleased]` entry under the right header (Added / Changed / Fixed / Contracts / Deprecated)
- [ ] `make lint && make test && make docs-build` green locally
- [ ] `/contract-check` clean
- [ ] New optional-dependency extra? → folded into the `all` aggregator
- [ ] New engine family? → row added to `docs/supported-domains.md`; cookbook stub under `docs/cookbook/`
- [ ] New engine family? → `/engine-status` now lists it as shipping
- [ ] `_version.py` bumped (patch / minor / major per §0.3)
```

## Appendix B — When NOT to follow this plan

- **If a downstream adopter hits a blocker**, that jumps the queue. File the RFC; cut a hotfix patch; resume the batch afterwards.
- **If a piggyback library breaks** (upstream API change, license flip, maintainer disappears), `docs/reference/piggyback-map.md` gets an anti-piggyback row and we port inline. Don't try to "fix upstream" as part of a batch.
- **If a contract would need to break non-additively**, stop, write an RFC using `docs/og_context/05_rfc_template.md`, and put it up for review before any code changes. Major bumps are expensive; be sure.

## Appendix C — Deliberately out of scope (still)

- **GWAS / biobank-scale genetics** — already documented in `docs/supported-domains.md`. Scale + file formats + inference shape all mismatch. Users go to `hail` / `pysnptools` / `PLINK 2.0`.
- **Deep-learning causal estimators** — research frontier where stability is insufficient to wrap at production quality. Revisit post-v2.0.
- **Streaming engine fits** (not to be confused with streaming `Panel.from_records`, which IS in Batch 13) — estimators all assume the Panel fits in memory. Out of scope.
- **Non-Python render pipelines beyond jellycell + Quarto** — LaTeX-only or Jupyter-Book generators are not on the roadmap.

---

*Last updated: 2026-04-19. Next review: after Batch 3 ships (1.0.0).*
