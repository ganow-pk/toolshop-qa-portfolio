"""scripts/run_history.py fetch: downloading the live CI history.

The rule: 404 means "no history yet" and gives an empty list. Anything else
that goes wrong raises, so CI fails instead of replacing the live history
with an empty one. A local web server (127.0.0.1) stands in for the live site.
"""
import json
import subprocess
import sys

import pytest

from paths import SCRIPTS
import run_history  # noqa: E402  (found through paths.py)


def test_200_returns_the_list(fake_site):
    fake_site.pages["/history/ci.json"] = (200, '[{"timestamp": "t1"}]')

    assert run_history.fetch(fake_site.url + "/history/ci.json", timeout=3) == [{"timestamp": "t1"}]


def test_request_skips_the_cache(fake_site):
    fake_site.pages["/history/ci.json"] = (200, "[]")

    run_history.fetch(fake_site.url + "/history/ci.json", timeout=3)

    assert "nocache=" in fake_site.requests[-1]


def test_404_means_no_history_yet(fake_site):
    assert run_history.fetch(fake_site.url + "/history/ci.json", timeout=3) == []


@pytest.mark.parametrize("status, body", [
    (503, "Service Unavailable"),
    (200, "<html>not json"),
    (200, '{"runs": []}'),
], ids=["server error 503", "invalid JSON", "JSON object, not a list"])
def test_anything_else_raises(fake_site, status, body):
    fake_site.pages["/history/ci.json"] = (status, body)

    with pytest.raises(RuntimeError):
        run_history.fetch(fake_site.url + "/history/ci.json", timeout=3)


def test_connection_refused_raises(closed_port):
    with pytest.raises(RuntimeError, match="Could not download"):
        run_history.fetch(f"http://127.0.0.1:{closed_port}/history/ci.json", timeout=3)


# ---------- The command CI calls ----------

def fetch_command(url, out):
    return subprocess.run(
        [sys.executable, str(SCRIPTS / "run_history.py"), "fetch", "--url", url, "--out", str(out)],
        capture_output=True, text=True, timeout=30)


def test_fetch_command_on_404_writes_an_empty_list(fake_site, tmp_path):
    out = tmp_path / "public" / "history" / "ci.json"

    run = fetch_command(fake_site.url + "/history/ci.json", out)

    assert run.returncode == 0, run.stderr
    assert json.loads(out.read_text()) == []


def test_fetch_command_on_error_exits_1_and_writes_nothing(fake_site, tmp_path):
    fake_site.pages["/history/ci.json"] = (503, "down")
    out = tmp_path / "public" / "history" / "ci.json"

    run = fetch_command(fake_site.url + "/history/ci.json", out)

    assert run.returncode == 1
    assert "ERROR" in run.stderr
    assert not out.exists()
