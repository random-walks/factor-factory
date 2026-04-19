# AGENTS.md — factor-factory

Canonical agent guide for this repo. Native readers: Cursor, Codex,
GitHub Copilot, Aider, Zed, Warp, Windsurf, Gemini CLI. Claude Code
reads `CLAUDE.md`, which delegates here.

## What this repo is

`factor-factory` is the shared analysis-pipeline framework for the
`random-walks` NYC OSS ecosystem. See [`README.md`](README.md) for the
elevator pitch.

## Where to start

**For new agents implementing the framework:** start at
[`docs/og_context/README.md`](docs/og_context/README.md). That folder
contains the complete design rationale, API specs, implementation
plan, and downstream-change roadmap. Reading order is documented
inside.

**For agents extending an existing engine family:** see
[`docs/og_context/03_specs/engine_protocol.md`](docs/og_context/03_specs/engine_protocol.md)
for the Protocol pattern + result dataclass conventions, then look at
the existing engine implementations under `factor_factory/engines/`.

**For agents adding a new factor / diagnostic / tidy primitive:** see
the corresponding spec under
[`docs/og_context/03_specs/`](docs/og_context/03_specs/).

## Hard rules

- **Every new engine adapter follows the Protocol contract** in
  `engine_protocol.md`. Result dataclasses are frozen + comparable.
  Conformance test required.
- **Every notebook in this repo follows the cell conventions** in
  `jellycell_integration.md` — including the `cells.setup()` pattern
  that works around the upstream jellycell cache-skip bug.
- **No domain-specific code lives here.** `factor-factory` is
  domain-agnostic. NYC-specific schemas, fixtures, and case studies
  belong in `nyc311` / `subway-access` (or a future
  `nyc-mesh` / `nyc-permits`).
- **Optional engine deps**: each engine family is an extra
  (`factor-factory[did]`, `[rdd]`, `[scm]`, ..., `[all]`). Default
  install = tidy + diagnostics + jellycell only. Minimal blast
  radius for downstream consumers.
- **MIT license, Python ≥ 3.12** to match siblings.

## Conventions

- **Imports**: `import factor_factory as ff` is encouraged in
  notebooks. In library code, use absolute imports
  (`from factor_factory.tidy import Panel`) for clarity.
- **Type hints**: pydantic models for runtime contracts (Panel,
  TreatmentEvent), `dataclass(frozen=True)` for engine result
  objects, vanilla type hints elsewhere.
- **Tests**: `pytest`-based, `factor_factory/tests/` mirrors source
  layout. Synthetic-panel fixtures in
  `factor_factory/tests/_fixtures/`.
- **Docs**: descriptive markdown under `docs/`. No Sphinx until
  v1.0 — keep iteration fast during the engine fan-out phase.
