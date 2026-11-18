"""Shared parent for every page object.

Rule of this framework: locators live ONLY in page objects, and every locator
uses the app's data-test attribute through get_by_test_id(). When the app
changes, a fix is one line in one file.
"""
from playwright.sync_api import Page

from config.logger import log
from pages.header import Header


class BasePage:
    PATH = "/"

    def __init__(self, page: Page) -> None:
        self.page = page
        self.header = Header(page)

    def open(self) -> "BasePage":
        # Relative path: pytest-playwright joins it with base_url from pytest.ini / settings.
        log.info("Open %s (%s)", type(self).__name__, self.PATH)
        # Heal H-003: wait for the page structure, not for every image and
        # third-party script ("load"). Tests then wait for the exact element
        # they need with expect(), so nothing is checked too early.
        self.page.goto(self.PATH, wait_until="domcontentloaded")
        return self
