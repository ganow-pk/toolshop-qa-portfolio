"""scripts/run_history.py: counting one run, and keeping the history file safe."""
import json
import os
import subprocess
import sys
import textwrap

import pytest

from paths import SCRIPTS
import run_history  # noqa: E402  (found through paths.py)


def counts(entry):
    names = ("passed", "failed", "broken", "skipped", "total", "retried")
    return {name: entry[name] for name in names}


# ---------- Counting one run ----------

def test_only_the_last_attempt_of_a_retried_test_counts(write_result, results_dir):
    # Files are named so that sorting by name puts the attempts in the wrong order.
    write_result("a", "T1", "passed", start=300, stop=400)   # T1 retry: passed
    write_result("b", "T1", "broken", start=100, stop=200)   # T1 first try: timed out
    write_result("c", "T2", "failed", start=100, stop=200)   # T2 first try: failed
    write_result("d", "T2", "failed", start=300, stop=500)   # T2 retry: failed again
    write_result("e", "T3", "passed", start=100, stop=150)   # T3: passed first time

    entry = run_history.summarize(results_dir, branch="b", commit="c")

    assert counts(entry) == {"passed": 2, "failed": 1, "broken": 0, "skipped": 0,
                             "total": 3, "retried": 2}


def test_unknown_status_counts_as_broken_never_as_passed(write_result, results_dir):
    write_result("a", "T1", "unknown", start=100, stop=200)
    write_result("b", "T2", "something-new", start=100, stop=200)

    entry = run_history.summarize(results_dir, branch="b", commit="c")

    assert (entry["passed"], entry["broken"], entry["total"]) == (0, 2, 2)


def test_entry_has_utc_time_duration_short_commit_and_given_values(write_result, results_dir):
    write_result("a", "T1", "passed", start=1_000, stop=1_400)

    entry = run_history.summarize(results_dir, source="ci", env="with-bugs", branch="main",
                                  commit="1234567890abcdef", run_url="https://example.test/run/1")

    assert entry["timestamp"] == "1970-01-01T00:00:01Z"
    assert entry["duration_s"] == 0.4
    assert entry["commit"] == "1234567"
    assert (entry["source"], entry["env"], entry["branch"]) == ("ci", "with-bugs", "main")
    assert entry["run_url"] == "https://example.test/run/1"


def test_env_is_read_from_environment_properties(write_result, results_dir):
    write_result("a", "T1", "passed", start=100, stop=200)
    (results_dir / "environment.properties").write_text("Environment=with-bugs\nUI=x\n")

    entry = run_history.summarize(results_dir, branch="b", commit="c")

    assert entry["env"] == "with-bugs"


def test_folder_without_results_raises(tmp_path):
    with pytest.raises(ValueError, match="nothing to record"):
        run_history.summarize(tmp_path)


def test_real_allure_output_with_retries_is_counted_right(tmp_path):
    """Run a tiny pytest project with allure-pytest and pytest-rerunfailures,
    so the counting is checked against the real result files, not our guess of them."""
    (tmp_path / "pytest.ini").write_text("[pytest]\n")
    (tmp_path / "test_sample.py").write_text(textwrap.dedent("""
        import pathlib
        import pytest

        FLAG = pathlib.Path(__file__).with_name("first-try-done")

        @pytest.mark.flaky(reruns=1)
        def test_times_out_then_passes():
            if not FLAG.exists():
                FLAG.write_text("1")
                raise TimeoutError("first try times out")

        @pytest.mark.flaky(reruns=1)
        def test_always_fails():
            assert 1 == 2

        def test_passes():
            pass

        def test_skipped():
            pytest.skip("not today")

        def test_broken():
            raise RuntimeError("the test itself broke")
    """))
    results = tmp_path / "allure-results"
    env = {key: value for key, value in os.environ.items() if key != "PYTEST_ADDOPTS"}
    env["PYTHONDONTWRITEBYTECODE"] = "1"

    run = subprocess.run(
        [sys.executable, "-m", "pytest", "-c", str(tmp_path / "pytest.ini"),
         "-p", "no:cacheprovider", "-p", "no:playwright", "-p", "no:html",
         f"--alluredir={results}", str(tmp_path / "test_sample.py")],
        cwd=tmp_path, env=env, capture_output=True, text=True, timeout=60)
    assert run.returncode == 1, run.stdout + run.stderr   # 1 = some tests failed, as planned

    entry = run_history.summarize(results, branch="b", commit="c")

    assert counts(entry) == {"passed": 2, "failed": 1, "broken": 1, "skipped": 1,
                             "total": 5, "retried": 2}


# ---------- The history file ----------

def test_history_keeps_only_the_newest_60_runs(tmp_path):
    history = tmp_path / "history" / "runs.json"   # folder doesn't exist yet

    for number in range(65):
        run_history.append(history, {"timestamp": f"run-{number:02d}"}, cap=60)

    saved = json.loads(history.read_text())
    assert len(saved) == 60
    assert saved[0]["timestamp"] == "run-05"
    assert saved[-1]["timestamp"] == "run-64"


def test_missing_history_file_counts_as_empty(tmp_path):
    assert run_history.load(tmp_path / "none-yet.json") == []


@pytest.mark.parametrize("broken_content", ["{not json", '{"a": 1}'],
                         ids=["invalid JSON", "JSON object, not a list"])
def test_broken_history_is_refused_and_left_untouched(tmp_path, broken_content):
    history = tmp_path / "runs.json"
    history.write_text(broken_content)

    with pytest.raises(ValueError):
        run_history.append(history, {"timestamp": "new run"})

    assert history.read_text() == broken_content
    assert not (tmp_path / "runs.json.tmp").exists()


def test_record_command_adds_one_ci_entry(tmp_path, write_result, results_dir):
    write_result("a", "T1", "passed", start=100, stop=200)
    history = tmp_path / "public" / "history" / "ci.json"

    run = subprocess.run(
        [sys.executable, str(SCRIPTS / "run_history.py"), "record",
         "--results", str(results_dir), "--history", str(history), "--source", "ci",
         "--branch", "main", "--commit", "abcdef1234567"],
        capture_output=True, text=True, timeout=30)

    assert run.returncode == 0, run.stderr
    [entry] = json.loads(history.read_text())
    assert (entry["source"], entry["branch"], entry["commit"], entry["passed"]) == \
           ("ci", "main", "abcdef1", 1)


def test_record_command_fails_when_there_are_no_results(tmp_path):
    history = tmp_path / "ci.json"

    run = subprocess.run(
        [sys.executable, str(SCRIPTS / "run_history.py"), "record",
         "--results", str(tmp_path), "--history", str(history), "--source", "ci",
         "--branch", "main", "--commit", "abc"],
        capture_output=True, text=True, timeout=30)

    assert run.returncode == 1
    assert "ERROR" in run.stderr
    assert not history.exists()
