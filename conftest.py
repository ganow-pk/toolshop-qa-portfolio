"""Shared fixtures and suite-wide rules.

Four rules are enforced here, so nobody has to remember them:
  1. Every test must carry an ISTQB test-design technique tag (@pytest.mark.istqb).
     A test without one stops the run before it starts.
  2. Elements are found by the app's data-test attribute (settings.TEST_ID_ATTRIBUTE).
  3. The HTML report shows each test's technique, and any healed test is labelled
     with its heal-log ID, so a healed pass is never passed off as a clean pass.
  4. UI tests get a screenshot embedded in the report (settings.REPORT_SCREENSHOTS),
     so evidence is in the report itself, not in a folder somewhere.

The Allure report (a second report, next to the HTML one) gets the same facts:
technique, heal ID, UI / API suite, screenshot, step log, and the Playwright
trace of a failed test. See the "Allure" section at the bottom of this file.
"""
import base64
import shutil
from pathlib import Path

import allure
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
    log.info("ENV   %s | UI %s | API %s", settings.ENV_NAME, settings.BASE_URL, settings.API_URL)

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
    home_page.open_first_in_stock_product()
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
    _attach_trace_to_allure(item, report)


def _attach_screenshot(item, report):
    """Rule 4: embed a screenshot of the page at the end of each UI test."""
    mode = settings.REPORT_SCREENSHOTS
    page = item.funcargs.get("page")
    if page is None or mode == "off":
        return
    # Screenshot the test step itself, plus any setup that broke before the test began.
    if report.when == "teardown" or (report.when == "setup" and not report.failed):
        return
    if mode == "failures" and not report.failed:
        return
    try:
        png = page.screenshot(full_page=True)
    except Exception as error:  # a broken screenshot must never hide the real result
        report.sections.append(("screenshot", f"Could not take screenshot: {error}"))
        return
    label = "Failure screenshot" if report.failed else "Evidence screenshot"
    allure.attach(png, name=label, attachment_type=allure.attachment_type.PNG)
    if html_extras is not None:
        png_text = base64.b64encode(png).decode()
        report.extras = getattr(report, "extras", []) + [html_extras.png(png_text, name=label)]


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
    report.title = f"Toolshop QA Portfolio - Test Report ({settings.ENV_NAME})"


# ---------- Allure: the second report ----------
# Plain markers (smoke, ui, api) become Allure tags on their own (allure-pytest
# does that). The markers with a value (istqb, healed) are mapped here.

ALLURE_CATEGORIES = Path(__file__).parent / "config" / "allure_categories.json"


def pytest_configure(config):
    """Short issue links: @allure.issue("8") opens GitHub issue #8."""
    if hasattr(config.option, "allure_link_pattern"):
        config.option.allure_link_pattern.append(("issue", settings.ISSUE_URL_PATTERN))


@pytest.fixture(autouse=True)
def _allure_labels(request):
    """Put each test's technique, heal ID, and UI/API suite on its Allure page."""
    node = request.node
    if node.get_closest_marker("ui"):
        allure.dynamic.parent_suite("UI tests")
    elif node.get_closest_marker("api"):
        allure.dynamic.parent_suite("API tests")

    technique = node.get_closest_marker("istqb")
    if technique and technique.args:
        allure.dynamic.label("ISTQB technique", technique.args[0])
        allure.dynamic.tag(technique.args[0])

    healed = node.get_closest_marker("healed")
    if healed and healed.args:
        heal_id = healed.args[0]
        allure.dynamic.label("Healed", heal_id)
        allure.dynamic.tag(f"healed {heal_id}")
        allure.dynamic.link(settings.HEAL_LOG_URL, name=f"Heal log: {heal_id}")

    # Allure lists every parametrize value on the test page. Never show a password.
    params = node.callspec.params if hasattr(node, "callspec") else {}
    for name in params:
        if "password" in name.lower():
            allure.dynamic.parameter(name, "******")


def _attach_trace_to_allure(item, report):
    """A failed UI test keeps a Playwright trace; attach it so Allure can open it."""
    if report.when != "teardown":
        return
    for name, path in report.user_properties:  # filled in by pytest-playwright
        if name == "playwright_trace":
            allure.attach.file(
                str(Path(item.config.invocation_params.dir, path)),
                name="Playwright trace",
                attachment_type="application/vnd.allure.playwright-trace",
                extension="zip",
            )


def pytest_sessionfinish(session):
    """Give Allure the failure categories and the environment of this run."""
    results_dir = getattr(session.config.option, "allure_report_dir", None)
    if not results_dir or not Path(results_dir).is_dir():
        return
    shutil.copyfile(ALLURE_CATEGORIES, Path(results_dir) / "categories.json")
    (Path(results_dir) / "environment.properties").write_text(
        f"Environment={settings.ENV_NAME}\nUI={settings.BASE_URL}\nAPI={settings.API_URL}\n"
    )
