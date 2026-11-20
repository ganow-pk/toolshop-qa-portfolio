# Releasing

Flow: `feature/*` --PR--> `develop` --> `release/vX.Y` --PR--> `main` --> tag `vX.Y` + release notes --> merge `main` back into `develop`.
`hotfix/*` may PR straight into `main`. The live report on GitHub Pages is published from `main` only.

**Local full runs:** a report saved with `scripts/publish_local_run.py` and merged into develop goes live only when the next release (or a hotfix) reaches main.

## Checklist
1. `develop` is green in CI and has everything that goes into this release.
2. Cut the branch: `git switch develop && git pull && git switch -c release/vX.Y`, then push it.
3. Open a PR `release/vX.Y` -> `main`. Checks `test` and `release-source` must pass.
4. Merge with **Create a merge commit** (not squash, not rebase). A squash gives main a commit develop doesn't have, and the branches drift apart.
5. Tag the merge commit on main: `git switch main && git pull && git tag -a vX.Y -m "vX.Y" && git push origin vX.Y`.
6. Create the GitHub Release from the tag, using the template below.
7. Merge main back into develop with a PR from `main` into `develop` (develop is protected, so no direct push). Merge it with **Create a merge commit**.
8. Check the live report updated: https://ganow-pk.github.io/toolshop-qa-portfolio/
9. Delete the `release/vX.Y` branch.

Hotfix: branch `hotfix/<name>` from main, PR into main (merge commit), tag a patch version (`vX.Y.Z`), then step 7.

## Release-notes template
```markdown
## vX.Y (YYYY-MM-DD)

### Tests added
- `tests/...`: what it covers (ISTQB technique)

### Bugs found
- #NN: one-line summary

### Changes to the suite/CI
- ...

### Known failing tests (expected)
- `test_name`: red on purpose, product bug #NN
```
