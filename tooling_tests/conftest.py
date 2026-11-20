"""Shared fixtures for the tooling tests.

These tests check our own scripts (run history, dashboard, the CI site build,
the "is this a full run?" rule), not the Toolshop app. They are kept apart from
the product suite on purpose: no ISTQB tags, no reports, no browser, no network
beyond a small web server on this machine (127.0.0.1).

Run them with: scripts/check_tooling.sh
"""
import json
import socket
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from paths import TOOLING_TESTS


# ---------- Guard: only run with this folder's own pytest.ini ----------

@pytest.hookimpl(tryfirst=True)
def pytest_cmdline_main(config):
    """Refuse to run with the project's pytest.ini.

    `pytest tooling_tests` finds this folder's pytest.ini on its own. But if
    the project's pytest.ini is forced (`-c pytest.ini`, or an IDE setting),
    pytest would empty allure-results/ and overwrite report/index.html.
    This check stops the run before any of that happens.
    """
    if config.inipath != TOOLING_TESTS / "pytest.ini":
        raise pytest.UsageError(
            "Run the tooling tests with their own settings: scripts/check_tooling.sh "
            "(or: pytest -c tooling_tests/pytest.ini tooling_tests)"
        )


# ---------- Allure result files ----------

@pytest.fixture
def results_dir(tmp_path):
    """An empty allure-results folder in a temp folder."""
    folder = tmp_path / "allure-results"
    folder.mkdir()
    return folder


@pytest.fixture
def write_result(results_dir):
    """Write one fake Allure result file, like allure-pytest does after each test attempt."""
    def write(file_name, history_id, status, start, stop):
        result = {"historyId": history_id, "status": status, "start": start, "stop": stop}
        (results_dir / f"{file_name}-result.json").write_text(json.dumps(result))
    return write


# ---------- A tiny web server on this machine ----------

class FakeSite:
    """A local stand-in for the live GitHub Pages site.

    pages maps a path to (HTTP status, body). Any other path answers 404.
    requests lists every path asked for (with its query string).
    """

    def __init__(self, server):
        self.server = server
        self.pages = {}
        self.requests = []
        self.url = f"http://127.0.0.1:{server.server_port}"


@pytest.fixture
def fake_site():
    site = None

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            site.requests.append(self.path)
            status, body = site.pages.get(self.path.split("?")[0], (404, "Not Found"))
            self.send_response(status)
            self.end_headers()
            self.wfile.write(body.encode("utf-8"))

        def log_message(self, *args):   # keep the test output quiet
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)   # port 0: any free port
    site = FakeSite(server)
    # A short poll interval makes shutdown quick (the default waits up to 0.5 s).
    thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True)
    thread.start()
    yield site
    server.shutdown()
    server.server_close()


@pytest.fixture
def closed_port():
    """A port on this machine that nothing listens on (connection refused)."""
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]
