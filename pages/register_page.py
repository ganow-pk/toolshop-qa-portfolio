from playwright.sync_api import Page

from config.logger import log
from pages.base_page import BasePage


class RegisterPage(BasePage):
    """Registration form. Fields are validated when the user leaves them (on blur),
    so tests can check every rule without submitting and creating accounts."""

    PATH = "/auth/register"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.form = page.get_by_test_id("register-form")

    def field(self, name: str):
        """Input by its data-test name, e.g. "dob", "phone", "password"."""
        return self.page.get_by_test_id(name)

    def error(self, name: str):
        """Error message under a field: data-test="<name>-error"."""
        return self.page.get_by_test_id(f"{name}-error")

    def enter(self, name: str, value: str) -> None:
        """Type a value, then leave the field so the form validates it."""
        shown = f"<{len(value)} characters>" if name == "password" else repr(value)
        log.info("Enter %s = %s, then leave the field", name, shown)
        field = self.field(name)
        field.fill(value)
        field.blur()
