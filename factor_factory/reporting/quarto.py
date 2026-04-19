"""Quarto (.qmd) report generator.

Consumes the same ``*_results.json`` tearsheet JSON as the jellycell
renderers, emits a ``.qmd`` file suitable for ``quarto render`` (HTML
or PDF output). No dependency on jellycell — lets consumers who don't
want jellycell still get a templated report from factor-factory outputs.

The Quarto system itself is a system dependency (not a pip package):
users need ``quarto`` on PATH to render the emitted ``.qmd``. We only
generate the markdown; we don't invoke ``quarto render`` ourselves.

Usage
-----

    from factor_factory.reporting.quarto import render_report
    from factor_factory.engines.did import estimate

    results = estimate(panel, methods=("twfe", "cs"))
    render_report(
        results=[r.to_dict() for r in results],
        panel_summary=panel.summary(),
        out_path="report.qmd",
        title="DiD Findings",
    )
    # Then: `quarto render report.qmd --to html` on the shell.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_TEMPLATE = """\
---
title: "{title}"
author: "{author}"
date: "{date}"
format:
  html:
    toc: true
    code-fold: true
  pdf:
    toc: true
---

## Panel summary

{panel_summary_block}

## Results

{results_block}

## Provenance

{provenance_block}

## Appendix — raw JSON

```{{{{=json}}}}
{raw_json}
```
"""


def render_report(
    *,
    results: list[dict[str, Any]],
    panel_summary: dict[str, Any] | None = None,
    out_path: str | Path,
    title: str = "factor-factory Report",
    author: str = "factor-factory",
    date: str = "",
) -> Path:
    """Generate a ``.qmd`` file from a list of Result.to_dict() outputs.

    Parameters
    ----------
    results:
        List of dicts, one per engine fit. Each is the output of
        ``<Family>Result.to_dict()``.
    panel_summary:
        Optional dict from ``Panel.summary()``. Rendered as a block at
        the top of the report.
    out_path:
        Where to write the ``.qmd`` file.
    title, author, date:
        Front-matter for the Quarto render.

    Returns
    -------
    Path to the written file.
    """
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    if panel_summary:
        panel_block = "\n".join(
            f"- **{k}**: {v}" for k, v in panel_summary.items() if k != "provenance"
        )
        prov = panel_summary.get("provenance", {}) or {}
    else:
        panel_block = "_Panel summary not provided._"
        prov = {}

    if prov:
        prov_block = "\n".join(f"- **{k}**: {v}" for k, v in prov.items() if v is not None)
    else:
        prov_block = "_No provenance metadata attached._"

    results_blocks: list[str] = []
    for i, r in enumerate(results, start=1):
        method = r.get("method", f"result_{i}")
        results_blocks.append(f"### {method}\n")
        for k, v in r.items():
            if k in ("method", "meta", "diagnostics"):
                continue
            if isinstance(v, (int, float, str)):
                results_blocks.append(f"- **{k}**: {v}")
            elif isinstance(v, dict) and len(v) < 20:
                results_blocks.append(f"- **{k}**:")
                for k2, v2 in v.items():
                    results_blocks.append(f"  - `{k2}`: {v2}")
        results_blocks.append("")

    rendered = _TEMPLATE.format(
        title=title,
        author=author,
        date=date,
        panel_summary_block=panel_block,
        results_block="\n".join(results_blocks),
        provenance_block=prov_block,
        raw_json=json.dumps({"results": results, "panel": panel_summary}, indent=2, default=str),
    )
    out.write_text(rendered)
    return out


__all__ = ["render_report"]
