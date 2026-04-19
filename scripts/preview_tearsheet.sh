#!/usr/bin/env bash
# Preview a scaffolded factor-factory tearsheet end-to-end.
#
# Used by .claude/launch.json's tearsheet-preview entry.
#
# Workflow:
#   1. Scaffold a throwaway showcase under /tmp/ff-preview-<timestamp>
#   2. Run its 01_load.py to build a Panel + fit an engine + render tearsheets
#   3. Launch the jellycell viewer against the showcase
set -euo pipefail

TS=$(date +%Y%m%d-%H%M%S)
PREVIEW_DIR="/tmp/ff-preview-${TS}"

echo "Scaffolding preview showcase at ${PREVIEW_DIR}..."
uv run python -m factor_factory scaffold "${PREVIEW_DIR}"

echo "Running 01_load.py..."
cd "${PREVIEW_DIR}"
uv run python notebooks/01_load.py

echo "Launching jellycell viewer (ctrl-c to stop)..."
uv run jellycell view "${PREVIEW_DIR}"
