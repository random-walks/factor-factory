---
description: Scaffold a new engine family. Arg = family name (snake_case, singular, matches dir name under factor_factory/engines/).
---

Scaffold a new engine family in `factor_factory/engines/$ARGUMENTS/`. Refuse if `$ARGUMENTS` is empty, contains non-snake_case characters, or the directory already exists.

Steps:

1. **Pick a reference to copy.** Prefer `factor_factory/engines/sdid/` as the template (homegrown, with bootstrap/jackknife inference) or `factor_factory/engines/survival/` (wrapper around an upstream package). Ask the human which pattern (wrapper vs homegrown) unless `$ARGUMENTS` already has a known piggyback (check `docs/reference/piggyback-map.md`).
2. **Create the directory structure:**
   - `factor_factory/engines/$ARGUMENTS/__init__.py` — exports `estimate`, `<Family>Result`, `<Family>Results`, `registry`; lazy-imports adapters inside a try/except that skips if the optional extra is missing.
   - `factor_factory/engines/$ARGUMENTS/_base.py` — frozen `<Family>Result` dataclass with `to_dict()`, `<Family>Engine` Protocol, module-level `registry: EngineRegistry[<Family>Engine]`.
   - `factor_factory/engines/$ARGUMENTS/<adapter>.py` — one adapter class implementing the Protocol. Stub with `raise NotImplementedError` if the math isn't done yet.
3. **Add a fixture.** Append a `<family>_fixture_panel()` function to `factor_factory/tests/_fixtures/cross_domain.py` that returns a Panel with a known-truth ground truth encoded in its provenance.
4. **Add a test.** Create `factor_factory/tests/test_engines/test_<family>_<adapter>.py` that:
   - instantiates the fixture
   - fits the adapter
   - asserts the recovered estimate matches the ground truth within tolerance
   - uses `pytest.importorskip("<upstream_package>")` at the top if the adapter wraps an external package
5. **Add the extras group** to `pyproject.toml` — new `[<family>]` extras entry plus fold into `all`.
6. **Add a piggyback-map row** to `docs/reference/piggyback-map.md`.
7. **Add a supported-domains row** to `docs/supported-domains.md`.
8. **Create a cookbook stub** at `docs/cookbook/<family>-<adapter>.md` with TODO markers.
9. **Add a CHANGELOG entry** under `[Unreleased]` → `### Added`.
10. **Print a next-steps checklist** for the human: fill in the math, write the citation docstring, verify the fixture ground truth, run `make lint test`.

Do NOT run `make lint` or `make test` yourself — the human drives that after filling in the math.
