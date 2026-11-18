from playwright.sync_api import Page

from config.logger import log
from pages.base_page import BasePage


class LoginPage(BasePage):
    PATH = "/auth/login"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.email = page.get_by_test_id("email")
        self.password = page.get_by_test_id("password")
        self.submit = page.get_by_test_id("login-submit")
        # Error messages
        self.login_error = page.get_by_test_id("login-error")        # bad email/password combination
        self.email_error = page.get_by_test_id("email-error")        # email field validation
        self.password_error = page.get_by_test_id("password-error")  # password field validation

    def login(self, email: str, password: str) -> None:
        # The password itself is never logged, only whether one was given.
        log.info("Log in as %r (password %s)", email, "given" if password else "EMPTY")
        self.email.fill(email)
        self.password.fill(password)
        self.submit.click()
        log.info("Clicked Login")
