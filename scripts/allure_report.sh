#!/usr/bin/env bash
# Build the Allure report from the last pytest run and open it in the browser.
# Needs Node.js. npx fetches the Allure 3 CLI the first time (no global install).
# Usage, from the project folder, after running pytest:
#   scripts/allure_report.sh
set -euo pipefail
cd "$(dirname "$0")/.."

ALLURE="npx --yes allure@3.33.0"          # pinned so every run looks the same

$ALLURE generate allure-results --clean   # -> allure-report/ (settings: allurerc.mjs)
$ALLURE open                               # serves allure-report/; Ctrl+C to stop
