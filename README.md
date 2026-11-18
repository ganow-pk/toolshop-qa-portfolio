# Toolshop QA Portfolio

[![Tests](https://github.com/ganow-pk/toolshop-qa-portfolio/actions/workflows/tests.yml/badge.svg)](https://github.com/ganow-pk/toolshop-qa-portfolio/actions/workflows/tests.yml)

**[View the latest test report](https://ganow-pk.github.io/toolshop-qa-portfolio/)**

UI and API test automation for [Practice Software Testing](https://practicesoftwaretesting.com) (the "Toolshop" demo store), built with **Playwright, Python, and pytest** using the **Page Object Model**.

This repo shows how I work as a QA engineer, not just how I write test code:

| What | Where |
|------|-------|
| Every test is tagged with its **ISTQB test-design technique**, and the suite refuses to run an untagged test | [docs/TEST_DESIGN.md](docs/TEST_DESIGN.md) |
| **Healing rules**: how flaky tests get fixed without hiding real bugs, with a heal log | [docs/HEALING_RULES.md](docs/HEALING_RULES.md), [docs/heal_log.md](docs/heal_log.md) |
| **AI guardrails**: how I use an AI coding assistant safely | [docs/AI_GUARDRAILS.md](docs/AI_GUARDRAILS.md) |
| **Bug reports** for defects found | [docs/BUGS.md](docs/BUGS.md), [Issues](../../issues) |
| A daily **CI run** that publishes the HTML report to GitHub Pages | [.github/workflows/tests.yml](.github/workflows/tests.yml) |

## Project layout
```
config/settings.py      All URLs and credentials in one place (environment variables override them)
pages/                  Page objects. The only place locators live (data-test attributes)
api/toolshop_api.py     REST API client. The only place endpoint paths live
tests/ui/               Browser tests
tests/api/              API tests
conftest.py             Fixtures and the suite-wide rules (technique tags, report columns)
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

**Point the suite at another environment** without touching code:
```bash
TOOLSHOP_BASE_URL=https://with-bugs.practicesoftwaretesting.com pytest
```

## Design choices
- **Locators use `data-test` attributes** through `get_by_test_id()`. They don't break when styling changes.
- **Tests wait for the app, not the clock.** No `sleep()`. Playwright's `expect()` retries until the condition holds or times out.
- **Negative login tests use an unregistered email**, so they never lock the shared demo account.
- **Config-driven.** Changing environments or accounts is a settings change, not a code change.
