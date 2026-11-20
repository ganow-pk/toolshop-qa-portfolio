# Releasing

Flow: `feature/*` --PR--> `develop` --> `release/vX.Y` --PR--> `main` --> tag `vX.Y` + release notes --> merge `main` back into `develop`.
`hotfix/*` may PR straight into `main`. The live report on GitHub Pages is published from `main` only.

**Local full runs:** `python scripts/publish_local_run.py` (add `--allure` for the Allure report, about 13 MB) saves the report and the local run history to `reports/`. Merged into develop, they go live only when the next release (or a hotfix) reaches main.

**Dashboard history:** each CI run on main downloads `history/ci.json` from the live site, adds its own run, and deploys it again. If that download fails (anything but a 404), the run fails and nothing is deployed, so the history is never wiped. A spare copy is kept as the `run-history` artifact of each main run (90 days).

## Checklist
1. `develop` is green in CI and has everything that goes into this release.
2. Cut the branch: `git switch develop && git pull && git switch -c release/vX.Y`, then push it.
3. Open a PR `release/vX.Y` -> `main`. Checks `test` and `release-source` must pass.
4. Merge with **Create a merge commit** (not squash, not rebase). A squash gives main a commit develop doesn't have, and the branches drift apart.
5. Tag the merge commit on main: `git switch main && git pull && git tag -a vX.Y -m "vX.Y" && git push origin vX.Y`.
6. Create the GitHub Release from the tag, using the template below.
7. Merge main back into develop with a PR from `main` into `develop` (develop is protected, so no direct push). Merge it with **Create a merge commit**.
8. Check the live dashboard updated (a new bar in the CI chart): https://ganow-pk.github.io/toolshop-qa-portfolio/
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
