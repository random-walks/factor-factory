---
description: Bump factor_factory/_version.py and roll CHANGELOG [Unreleased] → new version section. Arg = patch | minor | major (default patch).
---

Run these steps in order:

1. Parse `$ARGUMENTS`. Valid values: `patch` (default if omitted), `minor`, `major`.
2. Read current version from `factor_factory/_version.py`. Parse `__version__ = "X.Y.Z"`.
3. Compute new version per the policy in `docs/og_context/06_post_v0.1_roadmap.md#03-versioning-policy-minimum-bump-jellycell-inspired`:
   - patch → `X.Y.(Z+1)`
   - minor → `X.(Y+1).0`
   - major → `(X+1).0.0`
4. Write the new version back to `factor_factory/_version.py`.
5. In `CHANGELOG.md`:
   - Find the `## [Unreleased]` section.
   - Rename it to `## [<new-version>] — <today's date in YYYY-MM-DD>`.
   - Insert a fresh empty `## [Unreleased]` block above it with the standard subheadings: `### Added / ### Changed / ### Fixed / ### Deprecated / ### Contracts / ### Security`.
   - Update the comparison-link footer table: `[unreleased]: https://github.com/random-walks/factor-factory/compare/v<new>...HEAD` plus `[<new>]: ...compare/v<prev>...v<new>`.
6. Stage both files with `git add factor_factory/_version.py CHANGELOG.md`.
7. Print a summary: old version, new version, number of `[Unreleased]` entries being carried over, next-step suggestion (`git commit -m "release: v<new>"` followed by `git tag v<new>`).

Do NOT commit or tag — leave that to the human.

If `$ARGUMENTS` is invalid, print the usage and exit without writing anything.
