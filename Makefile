.PHONY: help dev test test-engines test-cross-domain test-property lint format docs docs-build docs-clean release-check clean

help:
	@echo "factor-factory — developer Makefile"
	@echo ""
	@echo "  make dev               uv sync --all-extras --dev (first-time setup)"
	@echo "  make test              pytest the whole suite"
	@echo "  make test-engines      pytest factor_factory/tests/test_engines/ only"
	@echo "  make test-cross-domain pytest the cross-domain conformance loop only"
	@echo "  make test-property     pytest hypothesis property tests (Batch 14+)"
	@echo "  make lint              ruff check + ruff format --check + mypy --strict"
	@echo "  make format            ruff format + ruff check --fix"
	@echo "  make docs              sphinx-autobuild, live preview at :5190"
	@echo "  make docs-build        sphinx-build -W --keep-going (CI mode)"
	@echo "  make docs-clean        remove docs/_build"
	@echo "  make release-check     preflight for a release tag push"
	@echo "  make clean             remove build/dist/cache"

dev:
	uv sync --all-extras --dev

test:
	uv run pytest factor_factory/tests -q

test-engines:
	uv run pytest factor_factory/tests/test_engines -q

test-cross-domain:
	uv run pytest factor_factory/tests/test_cross_domain.py -q

test-property:
	uv run pytest factor_factory/tests -q -m property

lint:
	uv run ruff check factor_factory
	uv run ruff format --check factor_factory
	uv run mypy factor_factory

format:
	uv run ruff format factor_factory
	uv run ruff check --fix factor_factory

docs:
	@if [ ! -f docs/conf.py ]; then \
		echo "docs/conf.py not found — Sphinx scaffold is a Batch-1 deliverable."; \
		echo "Read docs/og_context/06_post_v0.1_roadmap.md#batch-1 for details."; \
		exit 1; \
	fi
	uv run sphinx-autobuild docs docs/_build/html --port 5190 --watch factor_factory --watch docs

docs-build:
	@if [ ! -f docs/conf.py ]; then \
		echo "docs/conf.py not found — Sphinx scaffold is a Batch-1 deliverable."; \
		exit 0; \
	fi
	uv run sphinx-build -W --keep-going -b html docs docs/_build/html

docs-clean:
	rm -rf docs/_build docs/apidocs/_build

release-check:
	@$(MAKE) lint
	@$(MAKE) test
	@$(MAKE) docs-build
	uv run hatch build || uv build
	@echo ""
	@echo "Version:"
	@uv run python -c "from factor_factory._version import __version__; print(__version__)"
	@echo ""
	@echo "Recent commits:"
	@git log --oneline -10

clean:
	rm -rf build dist *.egg-info
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	rm -rf docs/_build docs/apidocs/_build
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
