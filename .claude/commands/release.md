---
description: Full release flow — preflight, bump version + CHANGELOG, commit, annotated tag, open release PR against main. Arg = patch | minor | major (default patch). Add --direct to push main + tag instead of opening a PR (requires permission rule; default is safe PR mode).
---

Run a full patch / minor / major release end-to-end. The default flow is
**safe**: every check runs before any file is modified, and the release
lands via a PR against `main` (not a direct push), so branch protection +
CI + human review all fire before the tag is public. Add `--direct` only
when the repo policy allows direct-to-main pushes and you have the
permission rule configured in `.claude/settings.json`.

## Usage

```
/release                     # patch, PR flow (default)
/release patch               # same
/release minor
/release major
/release patch --direct      # push main + tag directly (needs permission)
```

Parse `$ARGUMENTS`. First positional token is the bump kind (`patch` /
`minor` / `major`, default `patch`). Second positional token may be
`--direct`. Anything else → print usage and exit without touching the
tree.

## Preflight — run BEFORE any edits

Stop on the first failure and print a one-line `NOT READY — <reason>`
diagnostic. Do not edit any files yet.

1. **Clean working tree.** `git status --porcelain` must be empty. If
   not, bail out and tell the human what's dirty.
2. **On `main`, up-to-date with origin.** `git branch --show-current` →
   `main`. `git fetch origin main` then `git rev-parse HEAD` must equal
   `git rev-parse origin/main`. If behind, bail out and tell them to
   `git pull --ff-only`.
3. **Unreleased entries exist.** Parse `CHANGELOG.md`. The `## [Unreleased]`
   block must contain at least one non-empty bullet across its
   subsections. Refuse to cut an empty release.
4. **Lint.** `uv run ruff check factor_factory` must pass.
5. **Format.** `uv run ruff format --check factor_factory` must pass.
6. **Types.** `uv run mypy factor_factory` must pass.
7. **Tests.** `uv run pytest factor_factory/tests` must pass (0 failed).
8. **Strict docs build.** `uv run sphinx-build -W --keep-going -b html docs docs/_build/html`
   must succeed. Skip only if `docs/conf.py` does not exist yet
   (pre-Batch-1 historical escape hatch — log that it was skipped).
9. **Build wheel.** `uv run hatch build` (or `uv build`) must succeed and
   produce both an sdist and a wheel. Log the filenames.
10. **No tag collision.** The target tag `v<new-version>` must not
    already exist locally or on `origin`. Check with
    `git rev-parse -q --verify "refs/tags/v<new>"` and
    `git ls-remote --tags origin "v<new>"`.

If every preflight passes, print `PREFLIGHT OK — ready to roll v<new>`
and proceed.

## Bump

Invoke the same logic as `/bump $1` (in `.claude/commands/bump.md`):

1. Read current version from `factor_factory/_version.py`.
2. Compute new version per the patch / minor / major rule.
3. Write the new version back to `factor_factory/_version.py`.
4. In `CHANGELOG.md`:
   - Rename `## [Unreleased]` → `## [<new>] — <today YYYY-MM-DD>`.
   - Insert a fresh empty `## [Unreleased]` block above it with the
     standard subheadings: `### Added / ### Changed / ### Fixed / ### Deprecated / ### Contracts / ### Security`.
   - Update the footer comparison-link table:
     `[unreleased]: .../compare/v<new>...HEAD`
     `[<new>]: .../compare/v<prev>...v<new>`

## Post-bump sanity

After the edits, before committing:

1. **Version matches CHANGELOG.** The first non-Unreleased `## [X.Y.Z] — DATE`
   header in `CHANGELOG.md` must equal the new version in
   `factor_factory/_version.py`.
2. **Footer links sane.** The new `[unreleased]` row must reference
   `v<new>...HEAD` and there must be a `[<new>]: ...v<prev>...v<new>` row.
3. **Re-run lint + tests** (cheap, catches any autoformat artefacts the
   edits might have introduced — rare, but worth the 10s). Use
   `uv run ruff check factor_factory` and `uv run pytest factor_factory/tests`.

If any of these fail, do not commit. Restore the two edited files with
`git checkout -- factor_factory/_version.py CHANGELOG.md` and print
`POST-BUMP SANITY FAILED — <reason>`.

## Commit + tag

1. `git add factor_factory/_version.py CHANGELOG.md`.
2. Build a commit message: title `release: v<new>`, body containing a
   short rollup of what's in the release (pull the bullet subject lines
   from the just-promoted `## [<new>]` block; truncate at ~500 chars).
   Include the standard `Co-Authored-By` footer.
3. `git commit -m "<message>"`.
4. Create an annotated tag: `git tag -a v<new> -m "v<new>"`.

## Publish — PR mode (default)

1. `git checkout -b release/v<new>`.
2. `git push -u origin release/v<new>`.
3. `gh pr create --base main --head release/v<new> --title "release: v<new>" --body "<body>"` where the body contains:
   - A summary listing the PRs rolled up since the previous tag
     (pull from `git log --oneline v<prev>..HEAD`).
   - The preflight checklist (all ticked, since we just ran it).
   - A post-merge reminder: after merge, push the tag (`git push origin v<new>`).
4. Print the PR URL wrapped in `<pr-created>...</pr-created>` so the
   UI renders the status card. Example:

   ```
   <pr-created>https://github.com/random-walks/factor-factory/pull/42</pr-created>
   ```

5. **Do not push the tag yet.** The tag currently points at the commit
   on the release branch, not `main`. After the PR merges (squash or
   merge commit), either re-tag the merge commit or push the existing
   tag only if the merge was fast-forward. Tell the human both options.

## Publish — direct mode (`--direct`)

Only if the second argument is `--direct`:

1. `git push origin main`.
2. `git push origin v<new>`.
3. Print the URLs of the commit and the tag on GitHub.

If the push is denied by a harness permission rule, fall back to PR
mode automatically and tell the human why.

## Final output

Print a summary block:

- Old version → new version.
- PRs / commits rolled up since the previous tag.
- Mode chosen (`PR` or `direct`) and the resulting URL(s).
- Next-step suggestion:
  - PR mode: watch the CI on the release PR, merge, then push the tag
    (or re-cut against the merge commit if the project squash-merges).
  - Direct mode: watch the tag-triggered `release.yml` workflow, confirm
    PyPI artifact upload, and verify the GitHub Release was created.

## Invariants

- **Every preflight check runs before any file is modified.** If any
  fails, the tree is untouched and nothing is staged.
- **The commit and tag are created locally before any push.** If the
  push fails for any reason (network, permissions), the human can
  inspect `git log -1` and `git tag --list` and retry the push manually.
- **The default path does not push `main`.** Direct-to-main push is
  opt-in via `--direct` and requires a permission rule.
- **The human still owns the merge.** The skill opens the release PR
  and stops — it does not auto-merge or auto-push the tag post-merge.
