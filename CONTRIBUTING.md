# Contributing to factor-factory

Thanks for your interest. This is a small project with tight contracts — the quickest path to a merge is to know what those contracts are and what ceremony they need.

## Getting set up

```bash
git clone https://github.com/random-walks/factor-factory.git
cd factor-factory
make dev     # uv sync --all-extras --dev (or use pip install -e .[all,dev])
make test    # 112+ tests; should take ~30 s
make lint    # ruff + mypy strict
make docs    # sphinx-autobuild live preview at :5190 (post-Batch-1)
```

Editor setup: `ruff` + `mypy` via your IDE's LSP. No other config needed.

## The three contracts

Factor-factory commits to three invariants. Touching any of them triggers a ceremony. Full detail in [`docs/og_context/06_post_v0.1_roadmap.md`](docs/og_context/06_post_v0.1_roadmap.md#02-contract-invariants-lock-these-before-we-scale) §0.2.

1. **Panel contract** — Panel shape, `period_kind` variants, treatment-column naming, provenance.
2. **Engine Protocol contract** — frozen `<Family>Result` + `<Family>Engine` Protocol per family.
3. **Tearsheet JSON contract** — `<family>_results.json` schema that jellycell templates consume.

Breaking any of these = major bump. Additive changes = minor bump. Everything else = patch bump. See `.claude/skills/release-bump.md`.

## The piggyback-first rule

Before writing engine math from scratch, consult [`docs/reference/piggyback-map.md`](docs/reference/piggyback-map.md). We wrap mature packages; we don't reimplement. Two existing exceptions (SDID, Four-way Mediation) document why.

## Adding a new engine family

Use the `/add-engine <family>` Claude slash-command — it scaffolds every artifact the `engine-reviewer` agent will check for. Or by hand, copy `factor_factory/engines/sdid/` (homegrown) or `factor_factory/engines/survival/` (wrapper) and rename. Either way, ship:

- `_base.py` — frozen `<Family>Result` + `<Family>Engine` Protocol + `registry`
- `__init__.py` — lazy-import adapters behind a try/except gate on the extras
- `<adapter>.py` — actual implementation
- `tests/_fixtures/cross_domain.py` — synthetic fixture with ground truth in `provenance.annotations`
- `tests/test_engines/test_<family>_<adapter>.py` — conformance test that recovers the truth within tolerance
- `docs/supported-domains.md` — row for the new adapter
- `docs/cookbook/<family>-<adapter>.md` — ≥1 worked example
- `docs/reference/piggyback-map.md` — row (piggyback or anti-piggyback)
- `pyproject.toml` — `[<family>]` extras group + fold into `all`
- `CHANGELOG.md` — entry under `[Unreleased]` → `### Added` with citation

## Pre-merge checklist

Paste this into your PR description:

```
- [ ] Batch ref (if applicable): docs/og_context/06_post_v0.1_roadmap.md#batch-N
- [ ] `make lint && make test && make docs-build` green locally
- [ ] `/contract-check` clean
- [ ] New engine? → `/engine-status` now lists it as shipping
- [ ] New optional-dependency extra? → folded into `all`
- [ ] New adapter? → piggyback-map row + supported-domains row + cookbook page
- [ ] Contract touch? → snapshot regenerated + CHANGELOG ### Contracts entry
- [ ] CHANGELOG `[Unreleased]` entry under the right header
- [ ] `_version.py` bump (or defer to /bump at release time)
```

## RFCs (for new engine families or contract changes)

Copy `docs/og_context/05_rfc_template.md` to `docs/og_context/rfcs/<short-slug>.md` and open a PR. Discuss shape before implementation. Most new adapters don't need an RFC — just follow the scaffolding pattern. New **families** benefit from a 1-page RFC that lists the canonical paper, the piggyback choice, and the `Result` dataclass fields.

## Coding conventions

- `ruff` config is the source of truth — 100-char lines, py312 target.
- `mypy --strict` is the floor; no `type: ignore` without a comment explaining why.
- Follow existing import order (stdlib → third-party → factor_factory internals).
- Tests colocate under `factor_factory/tests/` by module (e.g. `test_engines/`, `test_tidy/`).
- Docstring style: short one-line summary, blank line, `Parameters`/`Returns` blocks when non-obvious.
- `@dataclass(frozen=True)` for every `Result`. No exceptions.

## Commit + PR hygiene

- Conventional-commit subject line: `feat(engines.rdd): ...`, `fix(panel): ...`, `docs: ...`, `ci: ...`.
- One engine family per PR in v1.x. Bundling 2+ families makes review painful.
- Link the canonical paper DOI + reference R-package URL in the adapter docstring, not just in the PR description.

## Discussion

Issues and PRs on GitHub. No Slack, no Discord, no IRC. Keep it async and searchable.
