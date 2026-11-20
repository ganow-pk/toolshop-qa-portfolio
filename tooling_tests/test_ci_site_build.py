"""The CI site build: the two steps in .github/workflows/tests.yml that keep
the dashboard history and build the page.

The test reads the steps' shell scripts straight from tests.yml (so it can't
drift from the real workflow) and runs them in a temp copy of the project,
the way GitHub runs them (bash -e). A local web server stands in for the live
GitHub Pages site. What this does NOT cover: the steps' `if:` conditions and
the deploy itself; those only run on GitHub.

The safety rule being checked: on main, if the live history can't be read
(anything but a 404), the history step fails, so nothing is built or deployed
and the live history is never replaced by an empty one.
"""
import json
import os
import shutil
import subprocess
import sys
import textwrap

import pytest

from paths import SCRIPTS, WORKFLOW

HISTORY_STEP = "Add this run to the run history"
SITE_STEP = "Build the dashboard"


def workflow_step_script(step_name):
    """The `run: |` script of one step in tests.yml."""
    lines = WORKFLOW.read_text(encoding="utf-8").splitlines()
    start = next((i for i, line in enumerate(lines) if line.strip() == f"- name: {step_name}"), None)
    assert start is not None, f'No step "{step_name}" in {WORKFLOW.name}: update this test'
    for i in range(start + 1, len(lines)):
        if lines[i].strip().startswith("- "):     # reached the next step
            break
        if lines[i].strip() == "run: |":
            run_indent = len(lines[i]) - len(lines[i].lstrip())
            body = []
            for line in lines[i + 1:]:
                if line.strip() and len(line) - len(line.lstrip()) <= run_indent:
                    break
                body.append(line)
            return textwrap.dedent("\n".join(body))
    raise AssertionError(f'Step "{step_name}" has no "run: |" script: update this test')


@pytest.fixture
def checkout(tmp_path):
    """A temp copy of what the two steps need: scripts/, an API run's results, its report."""
    project = tmp_path / "checkout"
    shutil.copytree(SCRIPTS, project / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
    (project / "reports").mkdir()
    results = project / "allure-results"
    results.mkdir()
    for number, status in enumerate(["passed", "passed", "failed"]):
        (results / f"r{number}-result.json").write_text(json.dumps(
            {"historyId": f"T{number}", "status": status, "start": 1000, "stop": 2000}))
    (project / "public" / "ci-api").mkdir(parents=True)
    (project / "public" / "ci-api" / "index.html").write_text("<p>API report</p>")
    return project


@pytest.fixture
def run_step(checkout):
    """Run one workflow step in the temp checkout. publish=True is a run on main."""
    def run(step_name, site_url, publish=True):
        env = {**os.environ,
               "PATH": f"{os.path.dirname(sys.executable)}{os.pathsep}{os.environ['PATH']}",
               "PYTHONDONTWRITEBYTECODE": "1",
               "PUBLISH": "true" if publish else "false",
               "SITE_URL": site_url,
               "GITHUB_REF_NAME": "main" if publish else "feature/x",
               "GITHUB_SHA": "abcdef1234567890",
               "RUN_URL": "https://github.com/ganow-pk/toolshop-qa-portfolio/actions/runs/1"}
        # GitHub runs `run:` scripts with: bash --noprofile --norc -eo pipefail
        return subprocess.run(["bash", "--noprofile", "--norc", "-eo", "pipefail", "-c",
                               workflow_step_script(step_name)],
                              cwd=checkout, env=env, capture_output=True, text=True, timeout=60)
    return run


def saved_history(checkout):
    return json.loads((checkout / "public" / "history" / "ci.json").read_text())


# ---------- History step on main ----------

def test_first_run_on_main_starts_a_new_history(fake_site, run_step, checkout):
    step = run_step(HISTORY_STEP, fake_site.url)   # live history: 404

    assert step.returncode == 0, step.stderr
    [entry] = saved_history(checkout)
    assert (entry["source"], entry["branch"], entry["commit"]) == ("ci", "main", "abcdef1")
    assert (entry["passed"], entry["failed"], entry["total"]) == (2, 1, 3)
    assert entry["run_url"].startswith("https://github.com/")


def test_next_run_on_main_adds_to_the_live_history(fake_site, run_step, checkout):
    fake_site.pages["/history/ci.json"] = (200, json.dumps([{"timestamp": "2026-11-19T13:20:00Z"}]))

    step = run_step(HISTORY_STEP, fake_site.url)

    assert step.returncode == 0, step.stderr
    history = saved_history(checkout)
    assert len(history) == 2
    assert history[0]["timestamp"] == "2026-11-19T13:20:00Z"   # the old run stays first


@pytest.mark.parametrize("status, body", [
    (503, "Service Unavailable"),
    (200, "<html>oops"),
], ids=["live site error 503", "live history not JSON"])
def test_unreadable_live_history_fails_the_step(fake_site, run_step, checkout, status, body):
    fake_site.pages["/history/ci.json"] = (status, body)

    step = run_step(HISTORY_STEP, fake_site.url)

    assert step.returncode != 0
    assert not (checkout / "public" / "history" / "ci.json").exists()


def test_unreachable_live_site_fails_the_step(run_step, checkout, closed_port):
    step = run_step(HISTORY_STEP, f"http://127.0.0.1:{closed_port}")

    assert step.returncode != 0
    assert not (checkout / "public" / "history" / "ci.json").exists()


# ---------- History step on PRs and develop ----------

def test_pr_run_never_reads_the_live_history(fake_site, run_step, checkout):
    fake_site.pages["/history/ci.json"] = (200, json.dumps([{"timestamp": "old"}] * 5))

    step = run_step(HISTORY_STEP, fake_site.url, publish=False)

    assert step.returncode == 0, step.stderr
    assert fake_site.requests == []
    [entry] = saved_history(checkout)            # a one-run preview only
    assert entry["branch"] == "feature/x"


# ---------- Site step ----------

def test_site_is_built_with_placeholders_when_nothing_was_published(fake_site, run_step, checkout):
    assert run_step(HISTORY_STEP, fake_site.url).returncode == 0

    step = run_step(SITE_STEP, fake_site.url)

    assert step.returncode == 0, step.stderr
    page = (checkout / "public" / "index.html").read_text()
    assert "Daily CI run (API): HTML report" in page
    assert "Allure report" not in page   # no Allure reports in this checkout
    assert "No local full run published yet" in (checkout / "public" / "full-run" / "index.html").read_text()
    assert json.loads((checkout / "public" / "history" / "local.json").read_text()) == []


def test_site_includes_published_local_run_and_allure_reports(fake_site, run_step, checkout):
    (checkout / "reports" / "local-full-run.html").write_text("<p>full run</p>")
    (checkout / "reports" / "local-full-run-allure.html").write_text("<p>full run allure</p>")
    (checkout / "reports" / "history-local.json").write_text(json.dumps(
        [{"timestamp": "2026-11-20T15:50:00Z", "source": "local", "passed": 30, "failed": 1}]))
    (checkout / "public" / "ci-api" / "allure").mkdir()
    (checkout / "public" / "ci-api" / "allure" / "index.html").write_text("<p>api allure</p>")
    assert run_step(HISTORY_STEP, fake_site.url).returncode == 0

    step = run_step(SITE_STEP, fake_site.url)

    assert step.returncode == 0, step.stderr
    page = (checkout / "public" / "index.html").read_text()
    for link in ('href="full-run/"', 'href="full-run/allure/"', 'href="ci-api/"', 'href="ci-api/allure/"'):
        assert link in page
    assert (checkout / "public" / "full-run" / "index.html").read_text() == "<p>full run</p>"
    assert (checkout / "public" / "full-run" / "allure" / "index.html").exists()
    assert len(json.loads((checkout / "public" / "history" / "local.json").read_text())) == 1
