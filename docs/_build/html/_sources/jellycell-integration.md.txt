# Jellycell integration

`factor_factory.jellycell.*` is the load-bearing **first-class
jellycell integration** that makes factor-factory more than just a
stats-engine framework. It owns the cell-level workarounds, the five
manuscript renderers, and the `scaffold` command.

## Why it exists

Three loadbearing reasons:

1. **Workaround for jellycell #J1** (`jc.setup` cells get cached,
   their imports vanish on re-execute). `cells.setup()` returns the
   imports as a dict the cell unpacks locally — sidesteps the cache
   scope bug entirely.
2. **Workaround for jellycell #J2** (`jc.figure(path)` requires
   `fig=plt.gcf()`). `figure.from_path()` is the path-only entry
   point that registers the artifact and emits the IPython display.
3. **Manuscript scaffolding**. Five canonical templates
   (METHODOLOGY, DIAGNOSTICS_CHECKLIST, FINDINGS, MANUSCRIPT, AUDIT)
   that every showcase has previously hand-authored. `tearsheets.*`
   regenerates them from a project's filesystem state.

Plus the `scaffold` command, which spins up a complete project in
one shot.

## Conventions

Showcase notebooks built against factor-factory follow these rules.
Each is enforced by the scaffolded `notebooks/01_load.py` stub.

### 1. Always start cells with `setup()`

Never rely on `# %% tags=["jc.setup"]` cells (jellycell #J1 makes them
unreliable). Inline the imports per cell:

```python
# %% tags=["jc.load", "name=panel"]
from factor_factory.jellycell.cells import setup
ns = setup(also=("matplotlib.pyplot as plt",))
jc, pd, np, plt, Image = ns["jc"], ns["pd"], ns["np"], ns["plt"], ns["Image"]
```

`setup()` returns a dict with `jc`, `pd`, `np`, `Image` always
present, plus any `also=` aliases parsed as `<module> [as <alias>]`
strings. Verbose, yes — but it's the only pattern that survives the
upstream cache-scope bug.

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

`jc.table` writes parquet by default and requires `pyarrow` —
factor-factory ships pyarrow in default deps so this works out of
the box (workaround for jellycell #J4).

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
```

The `deps=panel` declaration means jellycell re-runs this cell when
the upstream `name=panel` cell changes. Lint-friendly via
`pnpm showcase:lint`.

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

## Coordinated upstream items

The factor-factory workarounds are intentional design choices — they
should NOT be ripped out when jellycell ships the upstream fixes
(`random-walks/jellycell` #10–#15). The reasons, per the spec:

- **`cells.setup()` and `figure.from_path()` are stable surface
  area** for downstream consumers. Insulating callers from jellycell
  version churn is the point.
- **The five tearsheet renderers** outlive any single jellycell
  release; the manuscript-template scaffolding is a factor-factory
  capability regardless of jellycell internals.
- **The scaffold command** is a factor-factory feature; jellycell's
  own `init` doesn't and shouldn't know about factor-factory specifics
  (panel construction, DiD engine wiring, `pyarrow` default dep).

When upstream lands, the only change here is that
`figure.from_path` can call `jc.figure(path)` directly instead of
the current best-effort `register_figure` shim.

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
