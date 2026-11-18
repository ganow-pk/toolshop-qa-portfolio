"""Shared fixtures and suite-wide rules.

Four rules are enforced here, so nobody has to remember them:
  1. Every test must carry an ISTQB test-design technique tag (@pytest.mark.istqb).
     A test without one stops the run before it starts.
  2. Elements are found by the app's data-test attribute (settings.TEST_ID_ATTRIBUTE).
  3. The HTML report shows each test's technique, and any healed test is labelled
     with its heal-log ID, so a healed pass is never passed off as a clean pass.
  4. UI tests get a screenshot embedded in the report (settings.REPORT_SCREENSHOTS),
     so evidence is in the report itself, not in a folder somewhere.
"""
import base64

import pytest

try:  # pytest-html is optional: the suite still runs without it
    from pytest_html import extras as html_extras
except ImportError:
    html_extras = None

from api.toolshop_api import ToolshopApi
from config import settings
from config.logger import log
from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.product_page import ProductPage

ISTQB_TECHNIQUES = {
    "Equivalence Partitioning",
    "Boundary Value Analysis",
    "Decision Table Testing",
    "State Transition Testing",
    "Use Case Testing",
    "Error Guessing",
}


# ---------- Rule 1: every test declares its ISTQB technique ----------

def pytest_collection_modifyitems(config, items):
    problems = []
    for item in items:
        marker = item.get_closest_marker("istqb")
        if marker is None:
            problems.append(f"{item.nodeid}: missing @pytest.mark.istqb(...)")
        elif not marker.args or marker.args[0] not in ISTQB_TECHNIQUES:
            problems.append(f"{item.nodeid}: unknown technique {marker.args!r}")
    if problems:
        raise pytest.UsageError(
            "Test design rule broken. Tag each test with one of "
            f"{sorted(ISTQB_TECHNIQUES)}:\n  " + "\n  ".join(problems)
        )


# ---------- Rule 2: configuration and fixtures ----------

@pytest.fixture(autouse=True)
def _log_test_header(request):
    """First lines of every test's log: what it tests and which technique it uses."""
    technique = request.node.get_closest_marker("istqb")
    log.info("TEST  %s", request.node.name)
    log.info("ISTQB %s", technique.args[0] if technique else "-")
    log.info("ENV   UI %s | API %s", settings.BASE_URL, settings.API_URL)

@pytest.fixture(scope="session")
def base_url() -> str:
    """Overrides the plugin's base_url so the URL comes from config/settings.py."""
    return settings.BASE_URL


@pytest.fixture(scope="session", autouse=True)
def _use_data_test_attribute(playwright):
    playwright.selectors.set_test_id_attribute(settings.TEST_ID_ATTRIBUTE)


@pytest.fixture(scope="session")
def api(playwright):
    context = playwright.request.new_context(base_url=settings.API_URL)
    yield ToolshopApi(context)
    context.dispose()


@pytest.fixture
def login_page(page) -> LoginPage:
    return LoginPage(page).open()


@pytest.fixture
def home_page(page) -> HomePage:
    return HomePage(page).open()


@pytest.fixture
def product_page(home_page) -> ProductPage:
    home_page.open_first_product()
    product = ProductPage(home_page.page)
    product.wait_until_loaded()
    return product


# ---------- Rule 3: technique and heal columns in the HTML report ----------

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    technique = item.get_closest_marker("istqb")
    healed = item.get_closest_marker("healed")
    report.technique = technique.args[0] if technique and technique.args else ""
    report.heal_id = healed.args[0] if healed and healed.args else ""
    _attach_screenshot(item, report)


def _attach_screenshot(item, report):
    """Rule 4: embed a screenshot of the page at the end of each UI test."""
    mode = settings.REPORT_SCREENSHOTS
    page = item.funcargs.get("page")
    if html_extras is None or page is None or mode == "off":
        return
    # Screenshot the test step itself, plus any setup that broke before the test began.
    if report.when == "teardown" or (report.when == "setup" and not report.failed):
        return
    if mode == "failures" and not report.failed:
        return
    try:
        png = base64.b64encode(page.screenshot(full_page=True)).decode()
    except Exception as error:  # a broken screenshot must never hide the real result
        report.sections.append(("screenshot", f"Could not take screenshot: {error}"))
        return
    label = "Failure screenshot" if report.failed else "Evidence screenshot"
    report.extras = getattr(report, "extras", []) + [html_extras.png(png, name=label)]


@pytest.hookimpl(optionalhook=True)
def pytest_html_results_table_header(cells):
    cells.insert(2, "<th>ISTQB technique</th>")
    cells.insert(3, "<th>Healed (log ID)</th>")


@pytest.hookimpl(optionalhook=True)
def pytest_html_results_table_row(report, cells):
    cells.insert(2, f"<td>{getattr(report, 'technique', '')}</td>")
    cells.insert(3, f"<td>{getattr(report, 'heal_id', '')}</td>")


@pytest.hookimpl(optionalhook=True)
def pytest_html_report_title(report):
    report.title = "Toolshop QA Portfolio - Test Report"
