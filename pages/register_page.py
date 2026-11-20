from playwright.sync_api import Page

from config.logger import log
from pages.base_page import BasePage


class RegisterPage(BasePage):
    """Registration form. Field errors only show after Register is clicked.

    Tests fill ONE field, then click Register. The rest of the form is empty,
    so the browser blocks the submit: no request reaches the app and no
    account is created on the shared site."""

    PATH = "/auth/register"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.form = page.get_by_test_id("register-form")
        self.register_submit = page.get_by_test_id("register-submit")

    def field(self, name: str):
        """Input by its data-test name, e.g. "dob", "phone", "password"."""
        return self.page.get_by_test_id(name)

    def error(self, name: str):
        """Error message under a field: data-test="<name>-error"."""
        return self.page.get_by_test_id(f"{name}-error")

    def enter(self, name: str, value: str) -> None:
        """Type a value into one field, then click Register so the form shows
        its validation messages. Safe only while the rest of the form is empty."""
        shown = f"<{len(value)} characters>" if name == "password" else repr(value)
        log.info("Enter %s = %s", name, shown)
        self.field(name).fill(value)
        log.info("Click Register to show validation (form is incomplete, nothing is sent)")
        self.register_submit.click()
