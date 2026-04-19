"""Sphinx configuration for factor-factory docs.

Mirrors jellycell's setup (furo + myst-parser + autodoc2 + sphinx-llms-txt)
so the experience is uniform across the random-walks Python projects.
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

# Make the package importable for autodoc2 without a full install.
sys.path.insert(0, str(Path(__file__).parent.parent))

from factor_factory._version import __version__  # noqa: E402

# -- Project metadata ---------------------------------------------------------

project = "factor-factory"
author = "random-walks"
copyright = f"{datetime.now().year}, {author}"  # noqa: A001
version = __version__
release = __version__

# -- General config -----------------------------------------------------------

extensions = [
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "myst_parser",
    "autodoc2",
    "sphinx_design",
    "sphinx_copybutton",
    "sphinx_llms_txt",
]

# Allow both .md (MyST) and .rst sources.
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

master_doc = "index"

exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "og_context/**",  # design docs — internal, not user-facing
]

# -- MyST configuration -------------------------------------------------------

myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "fieldlist",
    "tasklist",
    "linkify",
    "substitution",
    "attrs_inline",
    "attrs_block",
]

myst_heading_anchors = 3
myst_linkify_fuzzy_links = False

# -- autodoc2 -----------------------------------------------------------------

autodoc2_packages = [
    {
        "path": "../factor_factory",
        "auto_mode": True,
        "exclude_dirs": ["tests"],
    },
]
autodoc2_output_dir = "apidocs"
autodoc2_render_plugin = "myst"
autodoc2_hidden_objects = ["dunder", "private", "inherited"]
autodoc2_skip_module_regexes = [
    r".*__main__",
    r".*\._templates.*",
    r".*notebooks\._templates.*",
    r".*notebooks\._scaffold_templates.*",
]

# Silence warnings about autodoc2 duplicate items from the scaffolded
# notebook templates — they're not meant to be part of the API docs.
suppress_warnings = [
    "autodoc2.dup_item",
    "myst.xref_missing",  # og_context/* refs are internal design docs, not Sphinx-built.
]

# -- HTML output --------------------------------------------------------------

html_theme = "furo"
html_title = f"factor-factory {__version__}"
html_static_path: list[str] = []
html_show_sourcelink = False
html_theme_options = {
    "source_repository": "https://github.com/random-walks/factor-factory/",
    "source_branch": "main",
    "source_directory": "docs/",
    "sidebar_hide_name": False,
    "navigation_with_keys": True,
    "footer_icons": [
        {
            "name": "GitHub",
            "url": "https://github.com/random-walks/factor-factory",
            "html": "",
            "class": "fa-brands fa-github",
        },
    ],
}

# -- Intersphinx --------------------------------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "pandas": ("https://pandas.pydata.org/docs/", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "scipy": ("https://docs.scipy.org/doc/scipy/", None),
    "matplotlib": ("https://matplotlib.org/stable/", None),
    "jellycell": ("https://jellycell.readthedocs.io/en/latest/", None),
}

# -- sphinx-copybutton --------------------------------------------------------

copybutton_prompt_text = r">>> |\.\.\. |\$ |In \[\d*\]: | {2,5}\.\.\.: | {5,8}: "
copybutton_prompt_is_regexp = True

# -- sphinx-llms-txt ----------------------------------------------------------

# Curated agent-facing index. `llms.txt` is human-authored-looking,
# `llms-full.txt` is the full concat (including apidocs).
llms_txt_full_max_size = None
llms_txt_exclude = [
    "apidocs/**",
    "genindex",
    "py-modindex",
    "search",
]
