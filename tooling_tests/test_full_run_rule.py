"""conftest.py rule 6: which `pytest` command lines count as a full run.

Only a full run is added to the local dashboard history, so a quick partial
run never shows up as "only 3 tests ran" on the chart.

How this works: each command line is parsed the way pytest would parse it in
the project folder (with the project's pytest.ini), and the project's
_is_full_run() is asked about it. Parsing runs no tests and writes nothing.
"""
import importlib.util

import pytest
from _pytest.config import _prepareconfig   # what pytest's own test helper (pytester) uses

from paths import REPO


@pytest.fixture(scope="module")
def project_conftest():
    """The project's conftest.py, loaded as a plain module (not as pytest rules)."""
    spec = importlib.util.spec_from_file_location("project_conftest", REPO / "conftest.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def is_full_run(project_conftest, monkeypatch):
    monkeypatch.chdir(REPO)                        # so the project's pytest.ini is used
    monkeypatch.syspath_prepend(str(REPO))         # conftest.py imports config/, pages/, api/
    monkeypatch.delenv("PYTEST_ADDOPTS", raising=False)

    def check(args):
        # --noconftest: parse only; the project's rules are never switched on here.
        config = _prepareconfig([*args, "--noconftest"])
        try:
            return project_conftest._is_full_run(config)
        finally:
            config._ensure_unconfigure()
    return check


@pytest.mark.parametrize("args, recorded", [
    ([], True),
    (["--headed"], True),
    (["tests"], False),
    (["tests/api"], False),
    (["-k", "login"], False),
    (["-m", "api"], False),
    (["--collect-only"], False),
    (["--lf"], False),
    (["-x"], False),
    (["--maxfail", "3"], False),
    (["--deselect", "tests/api"], False),
    (["--sw"], False),
], ids=lambda value: (" ".join(value) or "plain pytest") if isinstance(value, list) else None)
def test_which_command_lines_count_as_a_full_run(is_full_run, args, recorded):
    assert is_full_run(args) is recorded, f"pytest {' '.join(args)}"
