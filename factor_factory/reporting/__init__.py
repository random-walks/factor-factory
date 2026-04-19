"""Alternative reporting backends (non-jellycell).

The default reporting pipeline is ``factor_factory.jellycell.tearsheets.*``
— scaffold a showcase, render to jellycell manuscripts, view in the
jellycell viewer.

For consumers who want a different rendering pipeline, this module
provides alternatives:

- ``factor_factory.reporting.quarto`` — generates ``.qmd`` files that
  consume the same ``*_results.json`` tearsheet contract, then calls
  the system ``quarto render`` to emit HTML or PDF reports.

All reporting backends consume the Tearsheet JSON contract documented
in ``docs/reference/contracts.md`` — any engine family's
``Result.to_dict()`` output can be rendered by any backend.
"""

from __future__ import annotations

from . import quarto

__all__ = ["quarto"]
