<!-- factor-factory PR template — short, non-bureaucratic. Delete sections that don't apply. -->

## Summary

<!-- 1–3 bullets. What does this PR do and why? -->

## Batch ref (if applicable)

<!-- docs/og_context/06_post_v0.1_roadmap.md#batch-N -->

## Contract touches

<!-- Tick any that apply. If any are ticked, confirm the ceremony was performed per docs/og_context/06_post_v0.1_roadmap.md#02. -->

- [ ] Panel contract (`factor_factory/tidy/panel.py`, `contracts.py`, `record_view.py`)
- [ ] Engine Protocol contract (`engines/<family>/_base.py`)
- [ ] Tearsheet JSON contract (`Result.to_dict()` changes or `_templates/*.j2` changes)
- [ ] None of the above

If any ticked:

- [ ] `docs/reference/contracts.md` snapshot regenerated + `SNAPSHOT_VERSION` bumped
- [ ] CHANGELOG `### Contracts` note
- [ ] RFC filed (for breaking changes only) — link: _______________

## Checklist

- [ ] `make lint && make test && make docs-build` green locally
- [ ] `/contract-check` clean
- [ ] CHANGELOG `[Unreleased]` entry under the right header (Added / Changed / Fixed / Deprecated / Contracts / Security)
- [ ] New optional-dependency extra? → folded into `all` extras
- [ ] New engine family? → `/engine-status` shows it as shipping; piggyback-map row added; supported-domains row added; cookbook stub exists
- [ ] Citations (DOI + reference R package URL) present in adapter docstring

## Citations (for new engine adapters)

<!-- Paper + reference implementation URL -->

## Test plan

<!-- What did you run to convince yourself this works? -->
