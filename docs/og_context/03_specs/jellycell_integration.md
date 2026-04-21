# Spec: Jellycell integration

`factor_factory.jellycell.*` is the load-bearing **first-class
jellycell integration** that makes factor-factory more than just a
stats-engine framework. It owns:

1. Workarounds for known jellycell upstream bugs (so factor-factory
   consumers don't hit them)
2. The five canonical manuscript template renderers (so every
   showcase doesn't hand-author the same scaffolding)
3. The `scaffold` command that generates a working showcase skeleton
   in one shot

## Module layout

```
factor_factory/jellycell/
├── __init__.py
├── cells.py                     # setup() helper — workaround for jellycell #J1
├── figure.py                    # from_path() helper — workaround for jellycell #J2
├── tearsheets/
│   ├── __init__.py
│   ├── methodology.py
│   ├── diagnostics.py
│   ├── findings.py
│   ├── manuscript.py
│   └── audit.py
├── notebooks/
│   ├── _scaffold.py             # implementation of `python -m factor_factory scaffold`
│   └── _templates/              # notebook stubs the scaffolder copies
└── _templates/                  # Jinja2 templates for tearsheets
```

## `cells.py` — the setup helper

The most important deliverable in this module. Works around the
jellycell #J1 bug (`jc.setup` cells get cached, breaking imports).

```python
def setup(
    *,
    also: tuple[str, ...] = (),
    jellycell_module: str = "jellycell.api",
) -> dict:
    """Return a dict of imports for unpacking at the top of every cell.

    Workaround for the jellycell upstream bug where `# %% tags=["jc.setup"]`
    cells get cached + their imports DO NOT survive into subsequent
    re-executed cells. Calling `setup()` from any cell guarantees
    the imports are in scope regardless of cache state.

    Parameters
    ----------
    also : tuple of str, optional
        Additional import statements to evaluate, e.g.
        ("matplotlib.pyplot as plt", "scipy.stats as sps").
        Each entry is parsed as `<module> [as <alias>]`.
    jellycell_module : str, default "jellycell.api"
        Which jellycell module to import as `jc`. Override only for
        testing or compatibility shims.

    Returns
    -------
    dict
        Keys: at minimum `jc`, `pd`, `np`, `Image`. Plus any aliases
        from `also`. Unpack at the top of the cell:

        >>> ns = setup(also=("matplotlib.pyplot as plt",))
        >>> jc, pd, np, plt, Image = ns["jc"], ns["pd"], ns["np"], ns["plt"], ns["Image"]
    """
```

Usage in a notebook:

```python
# %% tags=["jc.load", "name=panel"]
from factor_factory.jellycell.cells import setup
ns = setup(also=("matplotlib.pyplot as plt",))
jc, pd, np, plt, Image = ns["jc"], ns["pd"], ns["np"], ns["plt"], ns["Image"]

# now use them as usual
panel = pd.read_parquet("data/panel.parquet")
jc.save({"n_obs": len(panel)}, "artifacts/summary.json")
```

This pattern is verbose but reliable. Once jellycell ships the
upstream fix for #J1, factor-factory can offer a thinner alternative
that uses `# %% tags=["jc.setup"]` directly.

## `figure.py` — path-only figure helper

Workaround for jellycell #J2 (`jc.figure(path)` requires `fig=` arg).

```python
def from_path(
    path: str | Path,
    *,
    caption: str = "",
    name: str | None = None,
    notes: str = "",
    tags: tuple[str, ...] = (),
) -> None:
    """Register an existing PNG as a jellycell figure artifact.

    For verbatim-mirror cases where you have a pre-rendered image
    on disk and don't want to recompute it via matplotlib.

    Parameters
    ----------
    path : str or Path
        Path to the image file (relative to project root, or absolute).
    caption : str, default ""
        Caption to associate with the figure in tearsheets.
    name : str, optional
        Artifact name. Defaults to the file's stem.
    notes : str, default ""
        Optional notes (rendered as italic subcaption in tearsheets).
    tags : tuple of str, default ()
        Optional tags for filtering in the live viewer.

    Returns
    -------
    None
        Side-effect-only: registers the artifact in the jellycell
        manifest and emits the IPython display so the cell renders
        the image.
    """
```

Usage:

```python
# %% tags=["jc.figure", "name=fig1"]
from factor_factory.jellycell.figure import from_path
from_path("artifacts/figures/figure-1.png", caption="System-wide ADA coverage")
```

Cleaner than the current pattern (`Image("artifacts/figures/figure-1.png")`).

## Tearsheets module

Five render functions, one per canonical manuscript:

```python
# factor_factory/jellycell/tearsheets/__init__.py
from .methodology import render as methodology
from .diagnostics import render as diagnostics
from .findings import render as findings
from .manuscript import render as manuscript
from .audit import render as audit
```

Each `render()` follows the same signature:

```python
def render(
    project: str,
    *,
    output_path: Path | None = None,
    overwrite: bool = False,
    template_overrides: dict | None = None,
) -> Path:
    """Render the [METHODOLOGY|DIAGNOSTICS_CHECKLIST|FINDINGS|...].md
    for `project` using the canonical template.

    Parameters
    ----------
    project : str
        Name of the jellycell project (the directory name under
        which jellycell.toml lives).
    output_path : Path, optional
        Where to write. Defaults to
        `<project>/manuscripts/<UPPERCASE_NAME>.md`.
    overwrite : bool, default False
        If False and output exists, raises FileExistsError. If True,
        replaces.
    template_overrides : dict, optional
        Keys override default template variables (e.g., add custom
        sections). See `_templates/` for available variables.

    Returns
    -------
    Path
        The path written.
    """
```

The templates live in `factor_factory/jellycell/_templates/` as
Jinja2 templates. They auto-pull data from:

- `<project>/jellycell.toml` for project metadata
- `<project>/artifacts/*.json` for headline numbers
- `<project>/artifacts/*.parquet` for tables
- The `EngineRegistry` for cited methods + their canonical refs

## `scaffold` command

The CLI entry point that generates a complete showcase skeleton:

```bash
python -m factor_factory scaffold <name> [--into <directory>]
```

What it does:

1. Creates `<directory>/<name>/` (default `<directory>` is current cwd)
2. Inside: `jellycell.toml` (project name = `<name>`), `notebooks/`,
   `data/`, `artifacts/`, `manuscripts/`, `site/` — matching what
   `jellycell init` produces
3. Drops a working `notebooks/01_load.py` stub that:
   - Uses `factor_factory.jellycell.cells.setup()` correctly
   - Builds an example panel using `factor_factory.tidy.Panel.from_records`
     against synthetic data (so the showcase runs out of the box)
   - Saves a `panel_summary.json` artifact
4. Drops a `_helpers.py` with the panel-loading boilerplate (kept
   thin; users edit it)
5. Drops a `data/README.md` explaining the data plan + escape
   hatches (live-fetch, etc.)
6. Drops scaffolded manuscripts in `manuscripts/`:
   - `METHODOLOGY.md` — minimal, edit-me stub
   - `FINDINGS.md` — minimal, regenerable via `jellycell.tearsheets.findings`
   - `AUDIT.md` — explicit "what's strong / what's gappy" template
7. Detects a parent `AGENTS.md` and prints
   `✓ agent guide detected at <path> — Cursor / Codex / Copilot / Claude Code already covered.`

Implementation lives in `notebooks/_scaffold.py`. The notebook stubs
live under `notebooks/_templates/` and are copied verbatim into the
scaffolded project (with `<name>` substitutions).

## Conventions for showcase notebooks built against factor-factory

These are documented in `docs/jellycell-integration.md` (shipped
with v0.1) and enforced by the scaffolded notebooks:

1. **Every cell that uses external imports starts with**
   `setup()` — never rely on `# %% tags=["jc.setup"]` cells.
2. **Headline numbers** go to `artifacts/<name>.json` via `jc.save`.
3. **Tables** go via `jc.table` (which requires pyarrow — already a
   default factor-factory dep, working around jellycell #J4).
4. **Pre-rendered figures** go via `factor_factory.jellycell.figure.from_path`.
5. **Generated figures** go via `jc.figure(path, fig=plt.gcf(), ...)`
   following the standard jellycell API.
6. **Cell deps** declared via `tags=["jc.step", "name=foo", "deps=bar", "deps=baz"]`
   (one `deps=` tag per upstream dep — nbformat rejects commas inside tags,
   enforced by jellycell's `deps-no-comma` lint rule as of 1.4.0).
7. **Manuscripts** auto-generated via the tearsheet renderers
   wherever possible; only `MANUSCRIPT.md` (the long-form
   working-paper) stays hand-authored.

## What's NOT in scope

- **Replacing jellycell** — we use it. We don't reimplement it.
- **A custom IDE / live viewer** — jellycell ships its own.
- **A documentation hosting platform** — out of scope.

## Tests

`tests/test_jellycell_integration.py` covers:

- `setup()` returns the expected keys regardless of `also=` content
- `from_path()` registers an artifact (mock the jellycell.api side)
- Each tearsheet renderer produces non-empty output against a
  fixture project
- The scaffold command produces a directory that passes `jellycell run`
  + `jellycell render` + `jellycell lint` end-to-end

## Open questions

- **Once jellycell ships the upstream fixes (#J1, #J2)**: do we
  deprecate `cells.setup()` and `figure.from_path()`? Or keep them
  as the canonical entry points to insulate consumers from
  jellycell version churn? **Resolved (2026-04-20):** keep them.
  jellycell 1.3.2 shipped both fixes (#J1/#10, #J2/#11) and 1.3.5
  closed the rest of #J3–#J6. Our shims stay as stable public API;
  consumers don't have to track jellycell minor-version churn. See
  `docs/jellycell-integration.md` → "Coordinated upstream items".
- **Tearsheet template customization**: how flexible should the
  templates be? Should they support per-project overrides via
  `<project>/manuscripts/_templates/*.md.j2`? Defer until we've
  shipped the v0.1 templates and seen what consumers actually
  override. **Partial answer (2026-04-20):** jellycell 1.4.0
  shipped a generic `jellycell.tearsheets.*` API for ad-hoc
  in-notebook tearsheets with a `template_overrides=` header-pin
  knob; that covers the per-result customization story. The
  factor-factory renderers stay fixed-schema for the five canonical
  showcase manuscripts, with a `<!-- tearsheet:freeze -->` splice
  marker for hand-edited sections.
- **R-style report generation**: should we offer Quarto / RMarkdown-
  style reports as well as jellycell? Defer indefinitely; that's a
  different rendering pipeline.
