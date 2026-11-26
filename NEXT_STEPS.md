# Where we left off (2026-11-24)

**Now:** 40 product tests (UI + API, ISTQB-tagged) and 57 tooling tests. Live: v1.5 (catalog regression tests, published local full run). 14 open bugs (#1–#12, #15, #16).
Latest local runs: main (2026-11-24) 39 passed / 1 failed (#15); with-bugs (2026-11-21, before the catalog tests) 20 passed / 8 failed (all filed) / 3 skipped.


## Done (round 1, 2026-11-17)
- [x] Framework built: Playwright + Python + pytest, POM, config-driven (`config/settings.py`)
- [x] 17 tests (10 UI, 7 API), each tagged with an ISTQB technique (untagged tests block the run)
- [x] First run: 14/17 passed. Healed H-001 (locked demo account, switched to `customer2@`) and H-002 (search read the old list, now waits on the search response). Re-run: **17/17 passed**
- [x] Report: ISTQB technique + Healed columns
- [x] Report: screenshot embedded for each UI test (`REPORT_SCREENSHOTS` = all / failures / off)
- [x] Report: step-by-step log for each test (passwords never logged)

## Next
1. [x] Report shows screenshot + step log for each test (confirmed 2026-11-18). Healed H-003 (page-load timeout); confirmed 17/17 on re-run
2. [x] Locked-account "no error message": not reproduced on 2026-11-18 (account unlocked). Recorded in `docs/BUGS.md` under "Investigated, not reproduced"
3. [x] Pushed to https://github.com/ganow-pk/toolshop-qa-portfolio
4. [x] Pages on (Source: GitHub Actions). First CI run: API 7/7 passed, UI 10/10 blocked by the site's Cloudflare bot check
4b. [x] Live 2026-11-18 (run #4 green). CI runs API tests only; full run is published from the Mac with `python scripts/publish_local_run.py`, then commit + push
5. [x] README badge + report link filled in (commit and push this change)
6. [x] Portfolio link added to both resumes (2026-11-18)

## Round 2: show the work (started 2026-11-18)
1. [x] (2026-11-18: 9 failures triaged; H-004 healed; 2 product-bug candidates) Run the suite against the buggy build: `TOOLSHOP_ENV=with-bugs pytest`, then triage every failure (locator difference vs. real bug)
2. [ ] Exploratory session 01 (60 min) using `docs/exploratory/session-01-browse-search-filter.md`
3. [x] Issues #1–#7 filed (2026-11-19), #8–#12 (2026-11-20); add screenshots to #2–#7. File each real bug as a GitHub issue (bug template), list it in `docs/BUGS.md`
4. [x] Written 2026-11-19: `tests/ui/test_registration.py` (11 cases), `tests/ui/test_checkout.py` (3). First run on main 2026-11-20: 4/14; first-run fixes (Register click, Continue as Guest tab) -> 13/14. Red on purpose: `test_password_length_message_matches_the_rule` (#15). with-bugs: 9 passed, 2 red on #16 (10-character rule), 3 checkout tests skipped (no guest checkout on that build). Fixes listed in the PR description (not heals)
5. [ ] Accessibility checks (axe-core, WCAG)
6. [x] Allure report added 2026-11-20: labels, issue links, screenshots, traces, failure categories. Built in CI and published on Pages since v1.1
7. [x] API tests retry once on network timeouts only (PR #13 CI flake; `conftest.py` rule 5, `docs/TEST_DESIGN.md`). Allure "Environment" category now catches API request timeouts. Merged 2026-11-20 (PR #14)
8. [x] Git flow (2026-11-20, PR #18, released v1.0): feature/* -> develop -> release/vX.Y -> main, hotfix/* -> main. CI deploys Pages from main only; `release-source` is a required check on main. See `docs/RELEASING.md`
9. [x] Dashboard (PR #22, released v1.1): stacked pass/fail chart per run, CI history on the live site (main only), local history from plain `pytest` runs (`conftest.py` rule 6), `scripts/dashboard.sh`. Live history started 2026-11-20; first daily refresh passed 2026-11-21; first local runs 2026-11-21
10. [x] Tooling tests (PR #24, released v1.1): `tooling_tests/` (52 checks, ~3 s) for the dashboard and history scripts, run by `scripts/check_tooling.sh` and first in CI. Not part of the product suite, not ISTQB-tagged
11. [x] `--collect-only` no longer overwrites `report/index.html` (PR #27, released v1.2)
12. [x] Catalog regression tests (PR #29, released v1.5 2026-11-24): sorting #6, price slider #2, category names #3; 9 tests. main 9/9; with-bugs 8 failed on #6/#2, category test passes ("Undefined" not seen on with-bugs 2026-11-21). Included in the published local full run of 2026-11-24 (40 tests: 39 passed, 1 failed on #15)

## Ideas for later
- Follow-up exploratory charters: checkout and invoices, security basics, accessibility (see Session 02)
- Use `docs/TEST_DESIGN.md` as ISTQB exam study notes

## Commands
    pytest                         # all tests, headless (main site; recorded for the dashboard)
    TOOLSHOP_ENV=with-bugs pytest  # same suite against the buggy build
    pytest --headed --slowmo 500   # watch the browser
    pytest -m smoke                # smoke set only
    open report/index.html         # open the report (Mac)
    scripts/allure_report.sh       # build + open the Allure report from the last run
    scripts/dashboard.sh           # build + open the local dashboard (run history + report links)
    scripts/check_tooling.sh       # tests for our own scripts (dashboard, history), not the app
