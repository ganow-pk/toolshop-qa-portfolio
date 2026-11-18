"""Run the full suite on this machine and publish its report to the portfolio site.

Why: the practice site's Cloudflare bot check blocks browsers running on
GitHub's cloud runners, so UI tests can only run from a normal machine.

Usage (from the project folder, in PyCharm's terminal):
    python scripts/publish_local_run.py
Then commit and push. GitHub Pages shows the new report a few minutes later.
"""
import html
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / "report" / "index.html"
PUBLISHED = ROOT / "reports" / "local-full-run.html"
LANDING = ROOT / "site" / "index.html"


def count_results(report_html: str) -> dict:
    blob = re.search(r'data-jsonblob="([^"]*)"', report_html).group(1)
    tests = json.loads(html.unescape(blob))["tests"]
    counts: dict = {}
    for runs in tests.values():
        for run in runs:
            counts[run["result"]] = counts.get(run["result"], 0) + 1
    return counts


def main() -> int:
    print("Running the full suite (UI + API)...")
    # The published "full run" is always the main environment.
    env = {**os.environ, "TOOLSHOP_ENV": "main"}
    exit_code = subprocess.call([sys.executable, "-m", "pytest"], cwd=ROOT, env=env)

    report_html = REPORT.read_text(encoding="utf-8")
    counts = count_results(report_html)
    summary = ", ".join(f"{n} {result.lower()}" for result, n in sorted(counts.items()))
    stamp = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")

    PUBLISHED.parent.mkdir(exist_ok=True)
    shutil.copyfile(REPORT, PUBLISHED)

    landing = LANDING.read_text(encoding="utf-8")
    landing = re.sub(r"<!--LOCAL_RUN-->.*?<!--/LOCAL_RUN-->",
                     f"<!--LOCAL_RUN-->{stamp} ({summary})<!--/LOCAL_RUN-->", landing)
    LANDING.write_text(landing, encoding="utf-8")

    print(f"\nPublished: {PUBLISHED.relative_to(ROOT)}  [{stamp}: {summary}]")
    print("Next: commit and push (Cmd+K in PyCharm, then Commit and Push).")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
