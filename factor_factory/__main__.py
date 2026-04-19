"""``python -m factor_factory <subcommand>`` entry point.

Currently the only subcommand is ``scaffold``. More may be added later
(e.g., ``render-tearsheets``, ``validate-panel``).
"""

from __future__ import annotations

import argparse
import sys

from .jellycell.notebooks._scaffold import main as scaffold_main


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m factor_factory",
        description="factor-factory CLI",
    )
    sub = parser.add_subparsers(dest="command")
    sub.add_parser(
        "scaffold",
        help="Generate a jellycell + factor-factory showcase skeleton",
        add_help=False,
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        build_argument_parser().print_help()
        return 0
    cmd, *rest = argv
    if cmd == "scaffold":
        return scaffold_main(rest)
    if cmd in ("-h", "--help", "help"):
        build_argument_parser().print_help()
        return 0
    print(f"Unknown command: {cmd}", file=sys.stderr)
    build_argument_parser().print_help()
    return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
