---
name: tearsheet-json-contract
description: Reminder that `*_results.json` shapes produced by Result.to_dict() are a public contract consumed by jellycell tearsheet templates and downstream adopters. Triggers when editing to_dict() methods or tearsheet *.j2 templates.
---

# Tearsheet JSON contract

The JSON files produced by each engine family's `Result.to_dict()` method are read by:

1. The jellycell tearsheet Jinja templates under `factor_factory/jellycell/_templates/*.j2`.
2. Any downstream showcase that archives results to disk and re-reads them later.
3. Human reviewers doing eyeball checks via `jq` / `cat`.

This makes the JSON shape a contract. The ceremony for changes:

## Additive changes (safe)

- **Adding a new optional key** to `to_dict()` → safe. Patch or minor bump. CHANGELOG `### Added` note.
- **Adding a new engine family** → safe; introduces a new `<family>_results.json` shape. Document the shape in `docs/reference/contracts.md` and add a per-family block in the tearsheet template.

## Breaking changes (costly)

- **Renaming a key** → breaking. Major bump on ≥1.0. Must land with:
  - RFC under `docs/og_context/rfcs/`
  - Migration note in `docs/migration/`
  - Template update in lockstep (both old + new key support during a deprecation window)
- **Removing a key** → breaking. Same ceremony.
- **Changing the type of a value** (e.g. `float → dict`) → breaking. Same ceremony.

## Snapshot gate

`docs/reference/contracts.md` holds a pinned JSON-schema snapshot per family. Any touch to a `to_dict()` method that changes the schema must regenerate the snapshot and bump `SNAPSHOT_VERSION` for that family. The contract-auditor agent checks this.

## Template-side view

The `.j2` templates under `factor_factory/jellycell/_templates/` are how the tearsheet actually reads the JSON. When you add a key to `to_dict()`, the template that consumes it also gets a patch — otherwise the new key is invisible. When you rename or remove a key, the template must be updated in lockstep OR tolerate both forms.

## Example safe additive change

```python
# engines/did/_base.py
@dataclass(frozen=True)
class DidResult:
    estimate: float
    std_error: float
    method: str
    # NEW in v1.1.0:
    effective_sample_size: int | None = None   # additive, optional, default None

    def to_dict(self) -> dict[str, Any]:
        return {
            "estimate": self.estimate,
            "std_error": self.std_error,
            "method": self.method,
            "effective_sample_size": self.effective_sample_size,  # NEW
        }
```

Template:

```jinja
{% if r.effective_sample_size is not none %}
  <p>Effective sample size: {{ r.effective_sample_size }}</p>
{% endif %}
```

Safe, additive, tearsheet renders fine for both old and new JSON.
