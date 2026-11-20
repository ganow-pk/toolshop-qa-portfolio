#!/usr/bin/env bash
# Run the tooling tests: checks for our own scripts (run history, dashboard,
# the CI site build, the "full run" rule), not for the Toolshop app.
# Fast (a few seconds), no browser, no internet. Writes only to temp folders:
# no report/, allure-results/, history/ or public/. CI runs this on every event.
# Usage, from anywhere in the project:
#   scripts/check_tooling.sh            # all tooling tests
#   scripts/check_tooling.sh -k fetch   # extra pytest options are passed on
set -euo pipefail
cd "$(dirname "$0")/.."

PYTHON=".venv/bin/python"
[ -x "$PYTHON" ] || PYTHON="python3"

# No __pycache__ folders written next to the scripts or tests.
export PYTHONDONTWRITEBYTECODE=1
exec "$PYTHON" -m pytest -c tooling_tests/pytest.ini tooling_tests "$@"
