"""Run the full suite on this machine and publish its report to the portfolio site.

Why: the practice site's Cloudflare bot check blocks browsers running on
GitHub's cloud runners, so UI tests can only run from a normal machine.

Usage (from the project folder, in PyCharm's terminal):
    python scripts/publish_local_run.py            # HTML report + run history
    python scripts/publish_local_run.py --allure   # also the Allure report (needs Node.js, ~13 MB file)
Then commit and push. The live dashboard updates when the change reaches main
(docs/RELEASING.md).

What it writes (all committed):
    reports/local-full-run.html          the HTML report of this run
    reports/history-local.json           every recorded local run, for the dashboard chart
    reports/local-full-run-allure.html   the Allure report as one file (only with --allure)
"""
import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from config import settings  # noqa: E402  (needs ROOT on the path first)

REPORT = ROOT / "report" / "index.html"
PUBLISHED = ROOT / "reports" / "local-full-run.html"
HISTORY = ROOT / settings.RUN_HISTORY_FILE
PUBLISHED_HISTORY = ROOT / "reports" / "history-local.json"
PUBLISHED_ALLURE = ROOT / "reports" / "local-full-run-allure.html"
ALLURE = ["npx", "--yes", "allure@3.33.0"]   # same pinned version as scripts/allure_report.sh


def count_results(report_html: str) -> dict:
    blob = re.search(r'data-jsonblob="([^"]*)"', report_html).group(1)
    tests = json.loads(html.unescape(blob))["tests"]
    counts: dict = {}
    for runs in tests.values():
        for run in runs:
            counts[run["result"]] = counts.get(run["result"], 0) + 1
    return counts


def publish_allure() -> None:
    """Build the Allure report as a single file (it opens without a server)."""
    with tempfile.TemporaryDirectory() as out:
        env = {**os.environ, "ALLURE_SINGLE_FILE": "1"}
        subprocess.run([*ALLURE, "generate", "allure-results", "--output", out],
                       cwd=ROOT, env=env, check=True, stdout=subprocess.DEVNULL)
        shutil.copyfile(Path(out) / "index.html", PUBLISHED_ALLURE)
    print(f"Published: {PUBLISHED_ALLURE.relative_to(ROOT)}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--allure", action="store_true",
                        help="also publish the Allure report (one ~13 MB file)")
    args = parser.parse_args()

    print("Running the full suite (UI + API)...")
    # The published "full run" is always the main environment. A plain full
    # pytest run also adds itself to the run history (conftest.py, rule 6).
    env = {**os.environ, "TOOLSHOP_ENV": "main"}
    exit_code = subprocess.call([sys.executable, "-m", "pytest"], cwd=ROOT, env=env)

    report_html = REPORT.read_text(encoding="utf-8")
    counts = count_results(report_html)
    summary = ", ".join(f"{n} {result.lower()}" for result, n in sorted(counts.items()))
    stamp = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")

    PUBLISHED.parent.mkdir(exist_ok=True)
    shutil.copyfile(REPORT, PUBLISHED)
    print(f"\nPublished: {PUBLISHED.relative_to(ROOT)}  [{stamp}: {summary}]")

    if HISTORY.exists():
        shutil.copyfile(HISTORY, PUBLISHED_HISTORY)
        print(f"Published: {PUBLISHED_HISTORY.relative_to(ROOT)} (run history for the dashboard)")
    else:
        print(f"No run history at {HISTORY} yet: the dashboard chart stays empty.")

    if args.allure:
        publish_allure()

    print("Next: commit and push (Cmd+K in PyCharm, then Commit and Push).")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
