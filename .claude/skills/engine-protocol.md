---
name: engine-protocol
description: Pre-edit ceremony checklist when touching any factor_factory/engines/*/_base.py or the Engine Protocol contract. Triggers on reads/edits of _base.py, _registry.py, or Result dataclasses.
---

# Engine Protocol ceremony

**You are about to touch the Engine Protocol contract** — one of the three factor-factory §0.2 invariants. Before you write, confirm you know which change type this is:

| Change type | Example | Bump | Ceremony |
|---|---|---|---|
| Additive (new optional field on `Result`) | Adding `jackknife_replicates: int \| None = None` | patch / minor | CHANGELOG `### Added` entry, snapshot regen |
| New adapter in existing family | `engines.did.sun_abraham` | minor | Standard engine-scaffold flow |
| New family | `engines.rdd` | minor | Use `/add-engine` |
| Renaming a `Result` field | `estimate` → `att` | **BREAKING** | RFC + **major** bump |
| Removing a `Result` field | Any removal | **BREAKING** | RFC + **major** bump |
| Changing the `Engine` Protocol signature | Adding a required kwarg to `estimate()` | **BREAKING** | RFC + **major** bump |

## The files you're about to touch

- `_base.py` — Protocol + frozen Result. **Frozen means frozen**: do not add `@dataclass.__post_init__` logic that mutates fields. Do not widen `Result` into a non-frozen class.
- `_registry.py` or the shared `engines/_registry.py` — `EngineRegistry` generic. Changing the registry shape affects every family simultaneously; prefer family-local workarounds.
- `<adapter>.py` files — adapters are free to refactor internally, but they must continue to satisfy the Protocol.

## Ceremony steps

1. If additive, proceed. CHANGELOG entry + snapshot regen + cookbook update if user-facing.
2. If breaking, **stop**. Write an RFC in `docs/og_context/rfcs/<slug>.md` (use `docs/og_context/05_rfc_template.md`). Get human sign-off.
3. Update `docs/reference/contracts.md` snapshot section with the new shape. Bump `SNAPSHOT_VERSION`.
4. Update `docs/og_context/03_specs/engine_protocol.md` if the prose is now stale.
5. Make sure `<Family>Result.to_dict()` still round-trips through the tearsheet templates under `factor_factory/jellycell/_templates/`.

## Golden rule

If downstream adopters (nyc311, subway-access) would have to change a line of code to upgrade past this PR, it's breaking. Major bump or don't ship.
