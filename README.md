# Toolshop QA Portfolio

[![Tests](https://github.com/ganow-pk/toolshop-qa-portfolio/actions/workflows/tests.yml/badge.svg)](https://github.com/ganow-pk/toolshop-qa-portfolio/actions/workflows/tests.yml)

**[View the test reports](https://ganow-pk.github.io/toolshop-qa-portfolio/)**: the daily CI run (API) and the latest full run (UI + API)

UI and API test automation for [Practice Software Testing](https://practicesoftwaretesting.com) (the "Toolshop" demo store), built with **Playwright, Python, and pytest** using the **Page Object Model**.

This repo shows how I work as a QA engineer, not just how I write test code:

| What | Where |
|------|-------|
| Every test is tagged with its **ISTQB test-design technique**, and the suite refuses to run an untagged test | [docs/TEST_DESIGN.md](docs/TEST_DESIGN.md) |
| **Healing rules**: how flaky tests get fixed without hiding real bugs, with a heal log | [docs/HEALING_RULES.md](docs/HEALING_RULES.md), [docs/heal_log.md](docs/heal_log.md) |
| **AI guardrails**: how I use an AI coding assistant safely | [docs/AI_GUARDRAILS.md](docs/AI_GUARDRAILS.md) |
| **Exploratory testing**: session charters and reports (SBTM) | [docs/exploratory/](docs/exploratory/) |
| **Bug reports** for defects found | [docs/BUGS.md](docs/BUGS.md), [Issues](../../issues) |
| A daily **CI run** that publishes the HTML reports to GitHub Pages | [.github/workflows/tests.yml](.github/workflows/tests.yml) |

## Project layout
```
config/settings.py      All URLs and credentials in one place (environment variables override them)
pages/                  Page objects. The only place locators live (data-test attributes)
api/toolshop_api.py     REST API client. The only place endpoint paths live
tests/ui/               Browser tests
tests/api/              API tests
conftest.py             Fixtures and the suite-wide rules (technique tags, report columns, Allure labels)
allurerc.mjs            Allure 3 settings (report name, output folder, failure categories)
docs/                   Test design, healing rules, heal log, AI guardrails, bugs
```

## Run it locally
```bash
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install chromium

pytest                    # everything, headless
pytest -m smoke           # just the smoke set
pytest -m api             # just the API tests
pytest --headed -m ui     # watch the browser
```
The report is written to `report/index.html`. Screenshots and traces of failures go to `test-results/`. Open a trace with `playwright show-trace <file>.zip`.

**Point the suite at another environment** without touching code (profiles live in `config/settings.py`):
```bash
TOOLSHOP_ENV=with-bugs pytest     # the site's intentionally buggy build
```

## Allure report (local)
Every run also writes Allure results to `allure-results/` (emptied at the start of each run). The HTML report above stays the main one; Allure adds filtering by tag, failure categories, and a trace viewer.

Needs Node.js. The first run downloads the Allure 3 CLI through `npx` (no global install).
```bash
pytest                       # or: TOOLSHOP_ENV=with-bugs pytest
scripts/allure_report.sh     # builds allure-report/ and opens it in the browser (Ctrl+C to stop)
```
What you'll see on each test:
- **Labels and tags:** ISTQB technique, `smoke` / `ui` / `api`, and `healed H-00X` with a link to the [heal log](docs/heal_log.md). Tests are grouped under **UI tests** and **API tests**.
- **Issue links:** tests that fail because of a known product bug link to the GitHub issue (`@allure.issue("8")`).
- **Evidence:** the screenshot, the step log, and, for a failed UI test, the Playwright trace.
- **Categories:** each failure is sorted into **Product defect** (assertion failed), **Test or locator problem** (timeout, strict mode), or **Environment** (Cloudflare, 423 Locked, network). The rules live in `config/allure_categories.json`; the first match wins. A category is a starting point for triage, not a verdict: a missing element can still be a product bug.

## Why UI tests don't run in CI
On the first CI run, all 7 API tests passed and all 10 UI tests failed. The failure screenshots
embedded in the report showed why: the site's **Cloudflare "verify you are human" check** blocks
browsers running on GitHub's cloud runners. From a normal machine, all 17 tests pass.

The cause is the environment, not the tests or the product, and getting past a bot check would
defeat its purpose. So the pipeline is built around it:
- **CI** runs the API tests live every day.
- **The full suite** runs locally with `python scripts/publish_local_run.py`, which saves the dated report to
  `reports/local-full-run.html`. CI publishes it next to the API report.

## Design choices
- **Locators use `data-test` attributes** through `get_by_test_id()`. They don't break when styling changes.
- **Tests wait for the app, not the clock.** No `sleep()`. Playwright's `expect()` retries until the condition holds or times out.
- **Negative login tests use an unregistered email**, so they never lock the shared demo account.
- **Config-driven.** Changing environments or accounts is a settings change, not a code change.
