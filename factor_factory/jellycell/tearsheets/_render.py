"""Shared template-rendering plumbing for the five tearsheet renderers."""

from __future__ import annotations

import json
import re
import tomllib
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from ..._version import __version__

_TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "_templates"
_ENV = Environment(
    loader=FileSystemLoader(str(_TEMPLATE_DIR)),
    undefined=StrictUndefined,
    keep_trailing_newline=True,
    autoescape=False,
)

_FREEZE_MARKER = re.compile(r"<!--\s*tearsheet:freeze\s*-->", re.IGNORECASE)


def render_template(
    template_name: str,
    project: str,
    *,
    output_path: Path | None = None,
    overwrite: bool = False,
    template_overrides: dict[str, Any] | None = None,
    extra_context: dict[str, Any] | None = None,
) -> Path:
    """Render ``template_name`` for ``project`` and write to disk.

    The template's ``<!-- tearsheet:freeze -->`` marker delineates a
    "regenerated" section (above) from a "preserved" section (below).
    On overwrite, only the regenerated section is rewritten; everything
    after the freeze marker is kept verbatim.
    """
    if output_path is not None:
        out_path = output_path
        # Derive project_dir from the explicit output_path so the renderer
        # reads context from the right place (output is .../manuscripts/<X>.md
        # so project_dir is two levels up).
        project_dir = output_path.parent.parent
    else:
        project_dir = _resolve_project_dir(project)
        out_path = _default_output_path(template_name, project_dir)

    context = _build_default_context(project, project_dir)
    if extra_context:
        context.update(extra_context)
    if template_overrides:
        context.update(template_overrides)

    template = _ENV.get_template(template_name)
    rendered = template.render(**context)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.exists():
        if not overwrite:
            raise FileExistsError(
                f"{out_path} already exists. Pass overwrite=True to regenerate "
                "(the section below `<!-- tearsheet:freeze -->` is preserved)."
            )
        rendered = _splice_in_preserved_tail(out_path.read_text(), rendered)
    out_path.write_text(rendered)
    return out_path


def _resolve_project_dir(project: str) -> Path:
    """Resolve a project name or path into the project root directory."""
    candidate = Path(project)
    if candidate.is_absolute() and candidate.exists():
        return candidate
    cwd = Path.cwd()
    if (cwd / "jellycell.toml").exists() and cwd.name == project:
        return cwd
    sub = cwd / project
    if sub.exists():
        return sub
    # Allow rendering even when the directory doesn't exist yet — caller
    # may be writing manuscripts to a fresh location.
    return sub


def _default_output_path(template_name: str, project_dir: Path) -> Path:
    mapping = {
        "methodology.md.j2": "METHODOLOGY.md",
        "diagnostics_checklist.md.j2": "DIAGNOSTICS_CHECKLIST.md",
        "findings.md.j2": "FINDINGS.md",
        "manuscript.md.j2": "MANUSCRIPT.md",
        "audit.md.j2": "AUDIT.md",
    }
    return project_dir / "manuscripts" / mapping[template_name]


def _build_default_context(project: str, project_dir: Path) -> dict[str, Any]:
    """Default Jinja context — pulled from the project's filesystem state."""
    context: dict[str, Any] = {
        "project": project,
        "version": __version__,
        "generated_at": datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC"),
        "data_files": _list_files(project_dir / "data"),
        "figures": _list_files(project_dir / "artifacts" / "figures"),
        "headline_artifacts": _load_headline_artifacts(project_dir / "artifacts"),
        "did_results": _load_did_results(project_dir / "artifacts"),
        "panel_metadata": _load_panel_metadata(project_dir / "data"),
        "record_count": None,
        "smd_table": None,
        "residual_diagnostics_summary": _load_residual_diagnostics(project_dir / "artifacts"),
        "engines": _infer_engines_from_results(project_dir / "artifacts"),
        "status_or_pending": _status_or_pending_factory(project_dir / "artifacts"),
    }
    if context["panel_metadata"] is not None:
        context["record_count"] = context["panel_metadata"].get("record_count")
    return context


def _list_files(directory: Path) -> list[str]:
    if not directory.exists():
        return []
    return sorted(p.name for p in directory.iterdir() if p.is_file())


def _load_headline_artifacts(artifacts_dir: Path) -> list[dict[str, Any]]:
    if not artifacts_dir.exists():
        return []
    out: list[dict[str, Any]] = []
    for path in sorted(artifacts_dir.glob("*.json")):
        if path.name.startswith("did_results"):
            continue
        if path.name.startswith("residual_diagnostics"):
            continue
        try:
            payload = json.loads(path.read_text())
        except json.JSONDecodeError:
            continue
        out.append(
            {
                "name": path.stem,
                "caption": "",
                "preview": json.dumps(payload, indent=2, default=str)[:1500],
            }
        )
    return out


def _load_did_results(artifacts_dir: Path) -> list[dict[str, Any]] | None:
    path = artifacts_dir / "did_results.json"
    if not path.exists():
        return None
    payload = json.loads(path.read_text())
    if isinstance(payload, dict) and "results" in payload:
        payload = payload["results"]
    if not isinstance(payload, list):
        return None
    return payload


def _load_panel_metadata(data_dir: Path) -> dict[str, Any] | None:
    if not data_dir.exists():
        return None
    for meta in sorted(data_dir.glob("*.parquet.meta.json")):
        try:
            return json.loads(meta.read_text())  # type: ignore[no-any-return]
        except json.JSONDecodeError:
            continue
    return None


def _load_residual_diagnostics(artifacts_dir: Path) -> dict[str, Any] | None:
    path = artifacts_dir / "residual_diagnostics.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())  # type: ignore[no-any-return]
    except json.JSONDecodeError:
        return None


def _infer_engines_from_results(artifacts_dir: Path) -> list[dict[str, str]]:
    results = _load_did_results(artifacts_dir) or []
    return [{"method": r["method"], "family": "did"} for r in results]


def _status_or_pending_factory(artifacts_dir: Path):  # type: ignore[no-untyped-def]
    """Return a callable used inside the Jinja template to mark check status."""
    artifact_present = {
        "smd": (artifacts_dir / "smd.json").exists() or (artifacts_dir / "smd.parquet").exists(),
        "parallel_trends": (artifacts_dir / "figures" / "parallel_trends.png").exists(),
        "residual_diagnostics": (artifacts_dir / "residual_diagnostics.json").exists(),
    }

    def status(check: str) -> str:
        if check == "multi_index_assertions":
            return "✓ enforced at panel construction"
        return "✓ saved" if artifact_present.get(check, False) else "_pending_"

    return status


def _splice_in_preserved_tail(existing_text: str, regenerated_text: str) -> str:
    """Replace everything ABOVE the freeze marker; preserve everything below.

    If the existing file lacks a freeze marker, fully overwrite. If the
    regenerated text has no marker (shouldn't happen with shipped
    templates), also fully overwrite.
    """
    existing_match = _FREEZE_MARKER.search(existing_text)
    regenerated_match = _FREEZE_MARKER.search(regenerated_text)
    if existing_match is None or regenerated_match is None:
        return regenerated_text
    new_head = regenerated_text[: regenerated_match.start()]
    preserved_tail = existing_text[existing_match.start() :]
    return new_head + preserved_tail


def load_jellycell_toml(project_dir: Path) -> dict[str, Any]:
    """Load a project's jellycell.toml; returns {} if absent."""
    path = project_dir / "jellycell.toml"
    if not path.exists():
        return {}
    return tomllib.loads(path.read_text())
