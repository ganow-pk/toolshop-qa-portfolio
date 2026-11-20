#!/usr/bin/env bash
# Build the local test dashboard and open it in the browser.
# Shows every full run recorded on this Mac (history/local-runs.json, filled in
# by plain `pytest`, see conftest.py rule 6) plus links to the last run's reports.
# Usage, from the project folder, after running pytest:
#   scripts/dashboard.sh
# Writes report/dashboard.html (and report/allure/index.html if Node.js is installed).
set -euo pipefail
cd "$(dirname "$0")/.."

HISTORY="${TOOLSHOP_RUN_HISTORY:-history/local-runs.json}"   # same override as config/settings.py
PYTHON=".venv/bin/python"
[ -x "$PYTHON" ] || PYTHON="python3"
LINKS=(--link "Last run: HTML report=index.html")

# The Allure report as ONE file, so it opens from disk without a server.
if ls allure-results/*-result.json >/dev/null 2>&1 && command -v npx >/dev/null; then
  ALLURE_SINGLE_FILE=1 npx --yes allure@3.33.0 generate allure-results \
    --output report/allure --clean >/dev/null
  LINKS+=(--link "Last run: Allure report=allure/index.html")
else
  echo "Skipping the Allure report (no allure-results/ yet, or Node.js not installed)."
fi

"$PYTHON" scripts/build_dashboard.py --local-history "$HISTORY" \
  --out report/dashboard.html "${LINKS[@]}"
open report/dashboard.html
