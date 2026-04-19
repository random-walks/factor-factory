---
description: Preflight check before pushing a release tag. Runs lint, tests, strict docs build, hatch build, and version sanity.
---

Execute these in order. Stop on first failure and report the offending step.

1. `uv run ruff format --check factor_factory docs 2>/dev/null || uv run ruff format --check factor_factory`
2. `uv run ruff check factor_factory`
3. `uv run mypy factor_factory`
4. `uv run pytest factor_factory/tests -q`
5. `uv run sphinx-build -W --keep-going -b html docs docs/_build/html` (skip if `docs/conf.py` does not yet exist — pre-Batch-1)
6. `uv run hatch build` (or `uv build`)
7. Print the version from `factor_factory/_version.py` and confirm it has no `[Unreleased]` block remaining above it in `CHANGELOG.md`.
8. Print the output of `git log --oneline -20` and the diff stat `git diff --stat main...HEAD` so the human can eyeball what's about to go out.

Return a final one-line verdict: `READY to tag v<version>` or `NOT READY — <reason>`.
