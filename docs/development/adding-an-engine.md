# Adding an engine family

A step-by-step walkthrough. The `/add-engine <family>` Claude slash-command automates most of this.

## 1. Check the piggyback map

Open [`../reference/piggyback-map.md`](../reference/piggyback-map.md). If your method is listed, you'll wrap the named package. If it's not listed and no mature Python or R port exists, you'll port from scratch (anti-piggyback) — see the SDID and Mediation families for the pattern.

## 2. Decide on the Result shape

The frozen `<Family>Result` dataclass is part of the Engine Protocol contract. It should contain:

- **Estimate + uncertainty** (always): `estimate: float`, `std_error: float`, or equivalents
- **Method identifier**: `method: str`
- **Inference parameters** (when relevant): `inference: str`, cluster-variable name, bootstrap seed, etc.
- **Diagnostic outputs** (family-dependent): unit weights, hazard ratios, changepoints, etc.
- **`extra: dict[str, Any]`** for family-specific passthrough data

Every field should be JSON-serializable in `to_dict()`.

## 3. Copy a template family

Either:

- **Wrapper pattern** — copy `factor_factory/engines/survival/` and rename. Replace `lifelines` with your upstream package.
- **Homegrown pattern** — copy `factor_factory/engines/sdid/` and rename. Your math lives inline.

## 4. Scaffold the artifacts

Every new family needs:

1. `factor_factory/engines/<family>/_base.py` — Result + Protocol + registry
2. `factor_factory/engines/<family>/__init__.py` — lazy adapter imports, exports
3. `factor_factory/engines/<family>/<adapter>.py` — implementation
4. `factor_factory/tests/_fixtures/cross_domain.py` — add a truth-tracking fixture
5. `factor_factory/tests/test_engines/test_<family>_<adapter>.py` — conformance test
6. `pyproject.toml` — `[<family>]` extras + fold into `all`
7. `docs/reference/piggyback-map.md` — add a row
8. `docs/supported-domains.md` — add a row
9. `docs/cookbook/<family>-<adapter>.md` — worked example
10. `CHANGELOG.md` — `[Unreleased]` → `### Added` entry with DOI

## 5. Citations in docstrings

The adapter class docstring MUST contain:

```python
class MyEngine:
    """Short one-line summary.

    Wraps :mod:`<upstream_package>` — see the reference implementation at
    https://<upstream-package-url>.

    References
    ----------
    Author, A., & Author, B. (Year). Paper title. Journal, Vol(Issue),
    Pages. https://doi.org/10.xxxx/...
    """
```

The `engine-reviewer` Claude agent will flag a missing citation.

## 6. Test the truth

Your conformance test must recover the ground truth within a documented tolerance. See [`../fixture-parity`](/.claude/skills/fixture-parity.md) (skill loaded into Claude sessions automatically).

```python
def test_my_engine_recovers_truth():
    panel = my_family_fixture_panel()
    result = estimate(panel, method="my_adapter")
    truth = panel.provenance.annotations["ground_truth_att"]
    assert abs(result.estimate - truth) < 2 * result.std_error
```

## 7. Ship

`/contract-check` → `make lint test docs-build` → open PR with the template. The `engine-reviewer` agent reviews against the 13-point checklist.
