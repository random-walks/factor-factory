# RFC template

Copy-paste this template whenever starting a new engine-family RFC
(Phase 2 of the implementation plan).

Each engine family release (DiD, RDD, SCM, etc.) starts with an RFC
to pin the API surface BEFORE writing engine adapters. The RFC
typically lives at `docs/rfcs/00N-<family>-engines.md` in this repo.

---

```markdown
# RFC NNN: <family> engines

**Status:** draft | in-review | accepted | implemented
**Author:** <name>
**Created:** YYYY-MM-DD
**Targets:** factor-factory v0.X.0

## Summary

One-paragraph description of what this RFC covers.

## Motivation

Why this engine family? Which canonical tools exist? What gap does
factor-factory fill?

## Proposed result dataclass

```python
@dataclass(frozen=True)
class <Family>Result:
    method: str                      # required
    # ... other required fields ...

    # ... optional fields ...
    diagnostics: dict | None = None
    meta: dict | None = None
```

Justification for each field. Note any deviations from the engine
Protocol pattern.

## Proposed engine Protocol

```python
class <Family>Engine(Protocol):
    name: str

    def fit(self, panel, *, ...) -> <Family>Result: ...
```

Justification for the `fit` signature. Which arguments are required vs.
optional? Which defaults are safe?

## Engine adapters in scope for this release

- **`<engine_name_1>`** — adapts `<external_package_name>`. Citation:
  `<Author Year>, <Journal>`. Acceptance criteria: passes
  conformance tests + recovers known ATT on `small_treatment_effect_panel`
  within tolerance.
- **`<engine_name_2>`** — ...

## Engine adapters explicitly NOT in scope (future work)

- ... and why they're deferred

## Optional dependency strategy

Which packages does this engine family pull in? What's the size impact?

```toml
[project.optional-dependencies]
<family> = ["external_pkg_1>=A.B", "external_pkg_2>=C.D"]
```

## Conformance tests

What tests every engine in this family must pass:

1. ...
2. ...
3. ...

(Beyond the standard contract tests in `test_<family>_conformance.py`.)

## Backwards compatibility

If this engine family already has a deprecated implementation in
nyc311 / subway-access:

- Field-mapping table: old field → new field
- Deprecation warning text
- Removal target version

## Open questions

- ...

## Implementation plan

1. Land the result dataclass + Protocol in `_base.py`
2. Land the registry in `__init__.py` with one engine adapter
3. Land conformance test scaffolding
4. Land each adapter as its own PR (one per release point)
5. Update `docs/getting-started.md` if user-facing concepts change
```

---

## Notes for RFC authors

- **Keep RFCs short.** A complete RFC for one engine family is
  usually 2-3 pages. The point is to pin the API + get reviewer
  agreement before code lands, not to write a paper.
- **Cite the canonical reference for each method.** Future
  contributors need the citation to understand what the adapter is
  approximating.
- **Always include the conformance test plan.** Not a TODO — actual
  test code or close to it.
- **Open questions go in the open-questions section.** Don't bury
  them. Reviewers look there first.
- **One PR per RFC.** Multiple-engine-family RFCs are too big to
  review productively.
