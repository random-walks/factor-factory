# Jellycell integration

`factor_factory.jellycell.*` is the load-bearing **first-class
jellycell integration** that makes factor-factory more than just a
stats-engine framework. It owns the cell-level workarounds, the five
manuscript renderers, and the `scaffold` command.

## Why it exists

Three loadbearing reasons:

1. **Stable per-cell import helper** (`cells.setup()`). Returns the
   imports as a dict the cell unpacks locally so every cell has a
   self-contained, reproducible namespace regardless of jellycell
   cache state. Originally a workaround for a jellycell cache-scope
   bug (`random-walks/jellycell` #10); that bug shipped upstream in
   jellycell 1.3.2, but we keep the helper as the canonical pattern
   because it's stable surface area downstream can lean on.
2. **Path-only figure registration** (`figure.from_path()`).
   Convenience wrapper for registering a pre-rendered PNG without
   having to pass `fig=plt.gcf()`. Originally a workaround for
   `random-walks/jellycell` #11 (shipped 1.3.2); retained as stable
   public API.
3. **Manuscript scaffolding**. Five canonical templates
   (METHODOLOGY, DIAGNOSTICS_CHECKLIST, FINDINGS, MANUSCRIPT, AUDIT)
   that every showcase has previously hand-authored. `tearsheets.*`
   regenerates them from a project's filesystem state.

Plus the `scaffold` command, which spins up a complete project in
one shot.

> **Upstream status:** all six jellycell issues (#10–#15) that
> motivated the `cells` / `figure` shims and `pyarrow` default dep
> are **closed** as of jellycell 1.3.5. Our pin floor
> (`jellycell[server]>=1.4.0,<2`) guarantees every fix is present
> and unlocks the generic `jellycell.tearsheets.*` in-notebook API
> (shipped in jellycell 1.4.0).
> The shims stay — they're stable surface area; upstream churn is
> insulated from downstream consumers.

## Conventions

Showcase notebooks built against factor-factory follow these rules.
Each is enforced by the scaffolded `notebooks/01_load.py` stub.

### 1. Always start cells with `setup()`

Inline the imports per cell via `setup()`:

```python
# %% tags=["jc.load", "name=panel"]
from factor_factory.jellycell.cells import setup
ns = setup(also=("matplotlib.pyplot as plt",))
jc, pd, np, plt, Image = ns["jc"], ns["pd"], ns["np"], ns["plt"], ns["Image"]
```

`setup()` returns a dict with `jc`, `pd`, `np`, `Image` always
present, plus any `also=` aliases parsed as `<module> [as <alias>]`
strings. Verbose, but every cell is self-contained and reproducible
— no dependence on what an earlier cell happens to have imported or
whether jellycell's cache chose to re-run it.

### 2. Headline numbers via `jc.save`

```python
jc.save(payload, "artifacts/<name>.json", caption="...")
```

Tearsheet renderers pick up `artifacts/*.json` automatically.
Convention: one JSON per "headline" (the model output, the headline
counts, etc.). Don't over-fragment.

### 3. Tables via `jc.table`

```python
jc.table(df, name="balance", caption="Pre-treatment SMDs")
```

`jc.table` writes parquet by default and requires `pyarrow`.
factor-factory ships `pyarrow` in default deps so this works out of
the box. (Upstream jellycell 1.3.4 also started shipping `pyarrow`
as a default dep — we keep ours regardless; it's a genuine
factor-factory requirement for `Panel` parquet round-trips.)

### 4. Pre-rendered figures via `from_path`

```python
# %% tags=["jc.figure", "name=fig1"]
from factor_factory.jellycell.figure import from_path
from_path("artifacts/figures/figure-1.png", caption="System-wide ADA coverage")
```

Cleaner than `IPython.display.Image(...)`. Registers the artifact
with jellycell when the API supports it; falls back to display-only
otherwise.

### 5. Generated figures via `jc.figure(..., fig=plt.gcf())`

For figures generated inside a cell, use jellycell's standard API:

```python
fig, ax = plt.subplots()
ax.plot(x, y)
jc.figure("artifacts/figures/scatter.png", fig=fig, caption="...")
```

### 6. Cell deps via `tags`

```python
# %% tags=["jc.step", "name=did", "deps=panel"]
# multiple upstream deps: one deps= tag per dep
# %% tags=["jc.step", "name=tearsheets", "deps=did", "deps=trends"]
```

The `deps=panel` declaration means jellycell re-runs this cell when
the upstream `name=panel` cell changes. **Do not** comma-separate
values inside a single tag — nbformat's tag schema rejects commas
(`^[^,]+$` per tag). Upstream jellycell 1.4.0 catches this
automatically via the `deps-no-comma` auto-fixable lint rule.

### 7. Manuscripts via `tearsheets.*`

```python
from factor_factory.jellycell import tearsheets
for name in ("methodology", "diagnostics", "findings", "manuscript", "audit"):
    getattr(tearsheets, name)(project_name, overwrite=True)
```

Sections above the `<!-- tearsheet:freeze -->` marker get
regenerated. Sections below it are preserved across runs — edit
interpretation, references, etc., without losing them. Only
`MANUSCRIPT.md` typically has substantial below-the-marker content
(the long-form working-paper writeup); the others stay mostly
auto-generated.

## The five renderers

Each `factor_factory.jellycell.tearsheets.*` function takes the
same signature:

```python
def render(
    project: str,
    *,
    output_path: Path | None = None,
    overwrite: bool = False,
    template_overrides: dict | None = None,
) -> Path: ...
```

| Renderer | Output | What it pulls from disk |
|---|---|---|
| `methodology` | `manuscripts/METHODOLOGY.md` | `data/*.parquet.meta.json` (panel metadata), `did_results.json` |
| `diagnostics` | `manuscripts/DIAGNOSTICS_CHECKLIST.md` | `artifacts/residual_diagnostics.json`, `artifacts/figures/parallel_trends.png` |
| `findings` | `manuscripts/FINDINGS.md` | `artifacts/*.json`, `artifacts/did_results.json`, `artifacts/figures/*` |
| `manuscript` | `manuscripts/MANUSCRIPT.md` | `data/*.parquet.meta.json` |
| `audit` | `manuscripts/AUDIT.md` | `artifacts/did_results.json` (for engine list) |

The renderers' default project-dir resolution looks for
`<cwd>/<project>/jellycell.toml`; pass `output_path=` explicitly if
you want to write somewhere else.

## When to use upstream `jellycell.tearsheets` instead

Jellycell 1.4.0 added a **generic in-notebook tearsheet API** —
`jellycell.tearsheets.findings(results_dict, …)`,
`jellycell.tearsheets.methodology(sections_dict, …)`, and
`jellycell.tearsheets.audit(notebook_path, …)`. It's orthogonal to
the five factor-factory renderers above, and both coexist:

| Use… | When |
|---|---|
| `factor_factory.jellycell.tearsheets.*` | You're building a **showcase project** scaffolded by `factor-factory scaffold` (or matching its layout). You want the five canonical manuscripts auto-populated from `artifacts/*.json` + `data/*.parquet.meta.json` via fixed Jinja2 templates, with a `<!-- tearsheet:freeze -->` marker that preserves your hand-written interpretation across re-renders. |
| `jellycell.tearsheets.*` | You have a **specific dict of results** you want to publish as a manuscript (inside a `jc.step` cell, so the rendered markdown participates in the jellycell cache graph). Works in any project layout; no `jellycell.toml` required. Callable with an arbitrary in-memory `results` dict — no filesystem-walking. |

Rule of thumb: if you scaffolded with `factor-factory scaffold`, use
the factor-factory renderers for the five canonical manuscripts; use
`jellycell.tearsheets.*` for *additional* ad-hoc tearsheets (e.g.,
per-subgroup findings, per-sensitivity-check audit pages) that live
outside the fixed five.

Scaffolded notebooks ship **both patterns, in two separate cells**,
so every new showcase has a working reference for each:

```python
# %% tags=["jc.step", "name=tearsheets", "deps=did", "deps=trends"]
# Canonical five — fixed-schema manuscripts driven from on-disk artifacts.
from factor_factory.jellycell import tearsheets
for name in ("methodology", "diagnostics", "findings", "manuscript", "audit"):
    getattr(tearsheets, name)("<project>", overwrite=True)


# %% tags=["jc.step", "name=adhoc_tearsheets", "deps=did"]
# Ad-hoc / in-memory — upstream jellycell.tearsheets.* (1.4.0+).
import json
from pathlib import Path
import jellycell.tearsheets as jt

did_records = json.loads(Path("artifacts/did_results.json").read_text())
did_by_method = {r.get("method", "est"): {k: v for k, v in r.items() if k != "method"}
                 for r in did_records}

jt.findings(
    results=did_by_method,
    out_path="manuscripts/_adhoc/findings_inline.md",
    project="<project>",
    template_overrides={"author": "<project>"},
)
```

`jt.findings(results, *, out_path, project, template_overrides)` writes
a byte-stable manuscript when the `template_overrides` header is
pinned. `jt.methodology(spec, …)` takes an ordered
`{section_title: markdown_body}` mapping. `jt.audit(notebook, *,
out_path)` renders a per-notebook cell-by-cell tearsheet (different
shape from our `audit.py` which renders AUDIT.md from project state —
both are useful in different contexts).

An end-to-end example of the **in-memory** pattern lives in the
[nyc-geo-toolkit boundary-explorer
showcase](https://github.com/random-walks/nyc-geo-toolkit/tree/main/examples/boundary-explorer-tearsheet)
(as of its v0.4.1 alignment with jellycell 1.4.0).

## The `scaffold` command

```bash
python -m factor_factory scaffold <name> [--into <dir>]
# or, if installed via pip:
factor-factory scaffold <name>
```

Drops:

```
<name>/
├── jellycell.toml             # project config, viewer port, lint rules
├── notebooks/
│   ├── 01_load.py             # working starter notebook
│   └── _helpers.py            # thin domain-specific scratch space
├── data/
│   └── README.md              # data plan + escape hatches
├── artifacts/
│   └── figures/
├── manuscripts/
│   ├── METHODOLOGY.md         # initial render — edit freely
│   ├── DIAGNOSTICS_CHECKLIST.md
│   ├── FINDINGS.md
│   ├── MANUSCRIPT.md
│   └── AUDIT.md
└── site/                      # jellycell render output (gitignored)
```

Detects a parent `AGENTS.md` and prints a confirmation when found.
Project-name validation: lowercase letters / digits / hyphens, must
start with a letter, ≤ 50 chars.

## Coordinated upstream items (historical)

All six original upstream issues landed:

| Upstream issue | Status | Shipped in |
|---|---|---|
| [jellycell#10](https://github.com/random-walks/jellycell/issues/10) — `jc.setup` cache-skip | closed | jellycell 1.3.2 |
| [jellycell#11](https://github.com/random-walks/jellycell/issues/11) — path-only `jc.figure` | closed | jellycell 1.3.2 |
| [jellycell#12](https://github.com/random-walks/jellycell/issues/12) — tearsheet path resolution | closed | jellycell 1.3.3 |
| [jellycell#13](https://github.com/random-walks/jellycell/issues/13) — `jc.table` needs `pyarrow` | closed | jellycell 1.3.4 |
| [jellycell#14](https://github.com/random-walks/jellycell/issues/14) — `jc.table` mixed-type inference | closed | jellycell 1.3.4 |
| [jellycell#15](https://github.com/random-walks/jellycell/issues/15) — tearsheet artifact filtering | closed | jellycell 1.3.5 |

Our pin floor (`jellycell[server]>=1.4.0,<2`) guarantees every fix
is present. The `cells.setup()` and `figure.from_path()` shims are
**retained deliberately** as stable public API — they insulate
downstream consumers from any future jellycell cache/API churn.
Ripping them out would be a breaking change for every showcase
that imports them, for a one-line behavioral improvement that
callers wouldn't notice.

## Tests

`factor_factory/tests/test_jellycell_integration.py` covers:

- `setup()` returns the expected keys; `also=` parsing rejects
  malformed entries.
- `from_path()` raises on missing files; works on real PNGs.
- `scaffold()` creates the expected directory layout, refuses
  invalid names, refuses to overwrite existing dirs.
- Each tearsheet renderer produces non-empty output against a
  fixture project.
- The freeze marker preserves below-the-marker content across
  re-renders.

End-to-end smoke test: `python -m factor_factory scaffold demo &&
cd demo && python notebooks/01_load.py` produces a parquet panel,
five JSON/PNG artifacts, and five regenerated manuscripts.
