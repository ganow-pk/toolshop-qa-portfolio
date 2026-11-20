"""Run history for the dashboard: one small JSON entry per test run.

An entry looks like this:
    {"timestamp": "2026-11-20T15:51:02Z", "source": "local", "env": "main",
     "branch": "develop", "commit": "7fc1a07",
     "passed": 30, "failed": 1, "broken": 0, "skipped": 0, "retried": 0,
     "total": 31, "duration_s": 212.4}
CI entries also carry "run_url" (the GitHub Actions run).

Counts come from allure-results/*-result.json. A test that was retried
(conftest.py, rule 5) has one result file per attempt; only its last attempt
counts, and "retried" says how many tests needed more than one attempt.

Used by:
    conftest.py                 adds a "local" entry after a full pytest run
    .github/workflows/tests.yml downloads the live CI history and adds a "ci" entry
    scripts/build_dashboard.py  draws the history

Command line (from the project folder):
    python scripts/run_history.py summarize allure-results
    python scripts/run_history.py record --results allure-results --history h.json --source ci
    python scripts/run_history.py fetch --url https://.../history/ci.json --out h.json
"""
import argparse
import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CAP = 60
STATUSES = ("passed", "failed", "broken", "skipped")


# ---------- Counting ----------

def summarize(allure_results_dir, source="local", env=None, branch=None,
              commit=None, run_url=None) -> dict:
    """Count one run's results. Values not given are read from the run or git."""
    results_dir = Path(allure_results_dir)
    results = [json.loads(path.read_text(encoding="utf-8"))
               for path in sorted(results_dir.glob("*-result.json"))]
    if not results:
        raise ValueError(f"No *-result.json files in {results_dir}: nothing to record.")

    attempts: dict = {}
    for result in results:
        attempts.setdefault(_test_key(result), []).append(result)

    entry = {
        "timestamp": _utc_iso(min(r.get("start", 0) for r in results)),
        "source": source,
        "env": env or _env_from_results(results_dir) or "main",
        "branch": branch or _git("rev-parse", "--abbrev-ref", "HEAD"),
        "commit": (commit or _git("rev-parse", "HEAD"))[:7],
        **{status: 0 for status in STATUSES},
        "retried": 0,
        "total": len(attempts),
        "duration_s": round((max(r.get("stop", 0) for r in results)
                             - min(r.get("start", 0) for r in results)) / 1000, 1),
    }
    for tries in attempts.values():
        final = max(tries, key=lambda r: (r.get("stop", 0), r.get("start", 0)))
        status = final.get("status")
        # Allure's "unknown" means the result is unusable: show it as broken, never as passed.
        entry[status if status in STATUSES else "broken"] += 1
        if len(tries) > 1:
            entry["retried"] += 1
    if run_url:
        entry["run_url"] = run_url
    return entry


def _test_key(result: dict) -> str:
    """Attempts of the same test share a historyId (name + parameters)."""
    return result.get("historyId") or result.get("fullName") or result.get("uuid", "")


def _utc_iso(epoch_ms) -> str:
    moment = datetime.fromtimestamp(epoch_ms / 1000, tz=timezone.utc) if epoch_ms else datetime.now(timezone.utc)
    return moment.strftime("%Y-%m-%dT%H:%M:%SZ")


def _env_from_results(results_dir: Path):
    """conftest.py writes "Environment=<name>" into environment.properties."""
    props = results_dir / "environment.properties"
    if props.is_file():
        for line in props.read_text(encoding="utf-8").splitlines():
            if line.startswith("Environment="):
                return line.split("=", 1)[1].strip()
    return None


def _git(*args) -> str:
    try:
        return subprocess.run(["git", *args], capture_output=True, text=True,
                              check=True, cwd=ROOT).stdout.strip() or "unknown"
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


# ---------- History file ----------

def load(history_path) -> list:
    """A missing file is an empty history. A broken file stops everything."""
    path = Path(history_path)
    if not path.exists():
        return []
    history = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(history, list):
        raise ValueError(f"{path} is not a JSON list: refusing to overwrite it.")
    return history


def append(history_path, entry: dict, cap: int = DEFAULT_CAP) -> list:
    """Add one entry, keep the newest `cap` entries, write the file back."""
    history = (load(history_path) + [entry])[-cap:]
    _write_json(Path(history_path), history)
    return history


def _write_json(path: Path, data) -> None:
    """Write to a temp file first, so a crash never leaves half a history."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp")
    temp.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")
    temp.replace(path)


# ---------- Download the live history (CI) ----------

def fetch(url: str, timeout: float = 20) -> list:
    """Download a history list from the live site.

    404 means "no history yet" and gives []. Anything else that goes wrong
    (no network, 5xx, not JSON, not a list) raises, so the caller fails
    instead of replacing the live history with an empty one.
    """
    separator = "&" if "?" in url else "?"
    fresh_url = f"{url}{separator}nocache={int(time.time())}"   # skip the Pages CDN cache
    request = urllib.request.Request(fresh_url, headers={"Cache-Control": "no-cache"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        if error.code == 404:
            return []
        raise RuntimeError(f"Could not download history from {url}: HTTP {error.code}") from error
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        raise RuntimeError(f"Could not download history from {url}: {error}") from error
    try:
        history = json.loads(body)
    except json.JSONDecodeError as error:
        raise RuntimeError(f"History at {url} is not valid JSON: {error}") from error
    if not isinstance(history, list):
        raise RuntimeError(f"History at {url} is not a JSON list.")
    return history


# ---------- Command line ----------

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Run history for the test dashboard.")
    commands = parser.add_subparsers(dest="command", required=True)

    show = commands.add_parser("summarize", help="print the entry for one run")
    show.add_argument("results", help="allure-results folder")

    record = commands.add_parser("record", help="add this run to a history file")
    record.add_argument("--results", default="allure-results")
    record.add_argument("--history", required=True)
    record.add_argument("--source", choices=["ci", "local"], required=True)
    record.add_argument("--cap", type=int, default=DEFAULT_CAP)
    record.add_argument("--branch")
    record.add_argument("--commit")
    record.add_argument("--run-url")

    download = commands.add_parser("fetch", help="download the live history (404 = empty)")
    download.add_argument("--url", required=True)
    download.add_argument("--out", required=True)

    args = parser.parse_args(argv)
    try:
        if args.command == "summarize":
            print(json.dumps(summarize(args.results), indent=1))
        elif args.command == "record":
            entry = summarize(args.results, source=args.source, branch=args.branch,
                              commit=args.commit, run_url=args.run_url)
            history = append(args.history, entry, cap=args.cap)
            print(f"Recorded run {len(history)} in {args.history}: {_one_line(entry)}")
        elif args.command == "fetch":
            history = fetch(args.url)
            _write_json(Path(args.out), history)
            print(f"Downloaded {len(history)} past runs from {args.url}")
    except (OSError, ValueError, RuntimeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


def _one_line(entry: dict) -> str:
    return (f"{entry['passed']} passed, {entry['failed']} failed, {entry['broken']} broken, "
            f"{entry['skipped']} skipped ({entry['retried']} retried)")


if __name__ == "__main__":
    sys.exit(main())
