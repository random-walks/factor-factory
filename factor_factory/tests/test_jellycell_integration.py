"""Tests for the jellycell integration MVP."""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

from factor_factory.jellycell import tearsheets
from factor_factory.jellycell.cells import setup
from factor_factory.jellycell.figure import from_path
from factor_factory.jellycell.notebooks._scaffold import scaffold

_TEMPLATES_DIR = Path(__file__).parent.parent / "jellycell" / "notebooks" / "_templates"
_TAGS_LINE_RE = re.compile(r"^#\s*%%\s*tags\s*=\s*(\[.*\])\s*$", re.MULTILINE)


def _notebook_template_paths() -> list[Path]:
    """Scaffold .py templates that are percent-format notebooks (have `# %%` cells)."""
    return sorted(
        p for p in _TEMPLATES_DIR.glob("*.py") if re.search(r"^#\s*%%", p.read_text(), re.MULTILINE)
    )


def test_setup_returns_required_keys() -> None:
    ns = setup()
    for key in ("jc", "pd", "np", "Image"):
        assert key in ns


def test_setup_with_also() -> None:
    ns = setup(also=("matplotlib.pyplot as plt", "json"))
    assert "plt" in ns
    assert "json" in ns


def test_setup_rejects_bad_also_entry() -> None:
    with pytest.raises(ValueError, match="Cannot parse"):
        setup(also=("not a valid import",))


def test_figure_from_path_requires_existing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        from_path(tmp_path / "nope.png")


def test_figure_from_path_with_real_file(tmp_path: Path) -> None:
    # Create a tiny 1x1 PNG using matplotlib.
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])
    target = tmp_path / "fig.png"
    fig.savefig(target)
    plt.close(fig)

    out = from_path(target, caption="x", name="fig", notes="n")
    # Returned object is the IPython.display.Image (or None in headless ci).
    assert out is None or out.filename == str(target)


def test_scaffold_creates_directory(tmp_path: Path) -> None:
    project_dir = scaffold("demo-project", into=tmp_path)
    assert project_dir.exists()
    assert (project_dir / "jellycell.toml").exists()
    assert (project_dir / "notebooks" / "01_load.py").exists()
    assert (project_dir / "data" / "README.md").exists()
    assert (project_dir / "manuscripts" / "METHODOLOGY.md").exists()
    assert (project_dir / "manuscripts" / "DIAGNOSTICS_CHECKLIST.md").exists()
    assert (project_dir / "manuscripts" / "FINDINGS.md").exists()
    assert (project_dir / "manuscripts" / "MANUSCRIPT.md").exists()
    assert (project_dir / "manuscripts" / "AUDIT.md").exists()
    body = (project_dir / "jellycell.toml").read_text()
    assert "demo-project" in body


def test_scaffold_rejects_invalid_name(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Invalid project name"):
        scaffold("Bad Name", into=tmp_path)


def test_scaffold_refuses_existing_directory(tmp_path: Path) -> None:
    target = tmp_path / "existing"
    target.mkdir()
    with pytest.raises(FileExistsError):
        scaffold("existing", into=tmp_path)


@pytest.mark.parametrize(
    "renderer",
    [
        tearsheets.methodology,
        tearsheets.diagnostics,
        tearsheets.findings,
        tearsheets.manuscript,
        tearsheets.audit,
    ],
)
def test_tearsheet_renders_non_empty(tmp_path: Path, renderer) -> None:  # type: ignore[no-untyped-def]
    project_dir = tmp_path / "demo"
    project_dir.mkdir()
    out = renderer(
        "demo",
        output_path=project_dir / "manuscripts" / "OUT.md",
        overwrite=True,
    )
    assert out.exists()
    content = out.read_text()
    assert len(content) > 100
    assert "demo" in content


def test_tearsheet_freeze_marker_preserves_tail(tmp_path: Path) -> None:
    project_dir = tmp_path / "demo"
    project_dir.mkdir()
    out_path = project_dir / "manuscripts" / "FINDINGS.md"

    tearsheets.findings("demo", output_path=out_path, overwrite=True)
    original = out_path.read_text()
    assert "<!-- tearsheet:freeze -->" in original

    # Append unique custom content under the freeze marker
    edited = original + "\n\nMY CUSTOM TAIL CONTENT\n"
    out_path.write_text(edited)

    tearsheets.findings("demo", output_path=out_path, overwrite=True)
    new_text = out_path.read_text()
    assert "MY CUSTOM TAIL CONTENT" in new_text


@pytest.mark.parametrize(
    "template_path",
    _notebook_template_paths(),
    ids=lambda p: p.name,
)
def test_scaffold_template_tags_have_no_commas(template_path: Path) -> None:
    """Regression: nbformat rejects tags containing commas.

    The tag schema enforces ``^[^,]+$`` per tag, so
    ``tags=["deps=a,b"]`` raises ``NotebookValidationError`` on first
    ``jellycell run``. The correct form is one ``deps=`` tag per dep:
    ``tags=["deps=a", "deps=b"]``. Upstream jellycell 1.4.0 added a
    ``deps-no-comma`` lint rule that catches this, but our scaffold
    templates need to ship clean from the start.
    """
    source = template_path.read_text()
    matches = _TAGS_LINE_RE.findall(source)
    assert matches, f"no `# %% tags=[...]` lines found in {template_path.name}"
    for raw in matches:
        tags = ast.literal_eval(raw)
        for tag in tags:
            assert "," not in tag, (
                f"tag {tag!r} in {template_path.name} contains a comma; "
                "split into one tag per value (nbformat rejects commas)."
            )


def test_tearsheet_freeze_marker_only_matches_line_anchored(tmp_path: Path) -> None:
    """Regression: doc text quoting the marker must NOT be treated as the marker itself.

    Earlier the regex matched any occurrence of ``<!-- tearsheet:freeze -->``,
    including a quoted reference inside doc prose at the top of the file.
    That caused the splice logic to preserve everything from the doc-comment
    onward, freezing the auto-generated content forever. The marker is now
    line-anchored.
    """
    project_dir = tmp_path / "demo"
    project_dir.mkdir()
    (project_dir / "manuscripts").mkdir()
    out_path = project_dir / "manuscripts" / "M.md"

    initial = (
        "# top\n"
        "> a quote referencing the marker `<!-- tearsheet:freeze -->` inline\n"
        "## section\n"
        "OLD CONTENT\n"
        "<!-- tearsheet:freeze -->\n"
        "preserved\n"
    )
    out_path.write_text(initial)
    tearsheets.findings("demo", output_path=out_path, overwrite=True)
    final = out_path.read_text()
    # The OLD CONTENT must not survive (the inline-quoted marker should not
    # have been treated as the splice point).
    assert "OLD CONTENT" not in final
    # The legitimate tail must survive.
    assert "preserved" in final
