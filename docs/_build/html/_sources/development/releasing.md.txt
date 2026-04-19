# Releasing

## Versioning policy (minimum-bump)

Factor-factory follows jellycell's pattern: patch bumps are cheap, hoard nothing, release frequently.

| Change | Bump |
|---|---|
| Bug fix, docs, refactor, non-breaking dep bump, new fixture | patch |
| New adapter, new engine family, new public API (additive) | minor |
| Break any contract (Panel / Engine Protocol / Tearsheet JSON) | **major** (post-1.0) / minor (pre-1.0) |

See `.claude/skills/release-bump.md` for the full decision tree.

## Cutting a release

One-time setup (complete before v1.0.0):

1. On PyPI, configure the project as a **trusted publisher** pointing at `random-walks/factor-factory` repo + `release.yml` workflow + `pypi` environment. No stored tokens.
2. Create the `pypi` GitHub Environment on the repo with protected-branches rule `main` only.

Routine release:

1. Confirm `main` is green (CI + docs + release-check).
2. Run `/bump patch|minor|major` — it bumps `factor_factory/_version.py` and rolls `CHANGELOG.md`.
3. Commit: `git commit -am "release: v<new-version>"`.
4. Tag: `git tag v<new-version>`.
5. Push: `git push && git push --tags`.
6. `release.yml` fires on the tag:
   - builds sdist + wheel via `uv build`
   - publishes to PyPI via OIDC trusted publisher
   - creates a GitHub Release with CHANGELOG-extracted notes + the built artifacts

## Pre-release checklist

```bash
make lint
make test
make docs-build
make release-check
```

`make release-check` prints the version + recent commits + confirms no `[Unreleased]` block remains above the new version heading.

## Hotfix flow

For urgent bug fixes on a released version:

1. Branch off the last tag: `git checkout -b hotfix/v<X.Y.Z+1> v<X.Y.Z>`.
2. Apply the fix + test.
3. `/bump patch`.
4. Commit + tag + push. `release.yml` fires.
5. Merge the hotfix back into `main` (usually a trivial fast-forward).

## Yanking a broken release

PyPI's "yank" is a metadata flag: yanked releases are still installable by exact version pin but skipped by dependency resolvers. Yank via the PyPI web UI. Add a CHANGELOG note explaining why.

## First release (v1.0.0)

See [`../og_context/06_post_v0.1_roadmap.md`](../og_context/06_post_v0.1_roadmap.md#batch-3) — cut at the end of Batch 3 after:

- Sphinx + RTD live
- `uv.lock` committed
- Cross-platform CI green (ubuntu + macos + windows, py3.12 + py3.13)
- Contract snapshots frozen at `SNAPSHOT_VERSION = "1.0.0"`
- First downstream adopter (nyc311 or subway-access) migrated end-to-end
