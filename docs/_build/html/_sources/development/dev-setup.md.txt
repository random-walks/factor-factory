# Dev setup

## First-time

```bash
git clone https://github.com/random-walks/factor-factory.git
cd factor-factory
make dev     # uv sync --all-extras --dev
```

Prefer `pip`? `pip install -e ".[all,dev]"` works too, but the `uv.lock` is the source of truth for reproducible builds (committed from Batch 2).

## Editor integration

- **VS Code / Cursor**: Python extension picks up `.venv/`. Enable ruff + mypy LSPs.
- **Vim / Neovim**: `ruff-lsp` + `pylsp-mypy` or `mypy` via `nvim-lspconfig`.
- **PyCharm**: Mark `factor_factory/` as a Sources Root; set interpreter to `.venv/bin/python`.

## Run one thing

```bash
uv run pytest factor_factory/tests/test_engines/test_sdid.py -v
```

## Build the docs locally

```bash
make docs           # live-reload at http://localhost:5190
make docs-build     # CI-style strict build into docs/_build/html
```

## Common knobs

| Task | Command |
|---|---|
| Lint only (no fix) | `make lint` |
| Auto-fix + format | `make format` |
| Mypy strict | `uv run mypy factor_factory` |
| Just the engines tests | `make test-engines` |
| Just cross-domain conformance | `make test-cross-domain` |
| Property-based (hypothesis) | `make test-property` *(Batch 14+)* |
| Full preflight | `make release-check` |

## Updating the lock

After adding a dep to `pyproject.toml`:

```bash
uv lock             # regenerate uv.lock
git diff uv.lock    # review the churn
```

Large `uv.lock` diffs during engine-family additions are normal and expected. Review the top-level additions; ignore transitive noise.
