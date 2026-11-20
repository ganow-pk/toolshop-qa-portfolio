from playwright.sync_api import Page

from config.logger import log
from pages.base_page import BasePage


class CheckoutPage(BasePage):
    """Checkout steps 2 to 4: sign in (or guest), billing address, payment."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        # Step 2: continue as guest
        self.guest_email = page.get_by_test_id("guest-email")
        self.guest_first_name = page.get_by_test_id("guest-first-name")
        self.guest_last_name = page.get_by_test_id("guest-last-name")
        self.guest_submit = page.get_by_test_id("guest-submit")
        self.proceed_as_guest = page.get_by_test_id("proceed-2-guest")
        # Step 3: billing address
        self.country = page.get_by_test_id("country")
        self.postal_code = page.get_by_test_id("postal_code")
        self.house_number = page.get_by_test_id("house_number")
        self.street = page.get_by_test_id("street")
        self.city = page.get_by_test_id("city")
        self.state = page.get_by_test_id("state")
        self.proceed_from_address = page.get_by_test_id("proceed-3")
        # Step 4: payment
        self.payment_method = page.get_by_test_id("payment-method")
        self.finish_button = page.get_by_test_id("finish")
        self.payment_success = page.get_by_test_id("payment-success-message")
        self.payment_error = page.get_by_test_id("payment-error-message")

    def continue_as_guest(self, guest: dict) -> None:
        log.info("Sign-in step: continue as guest %s %s", guest["first_name"], guest["last_name"])
        self.guest_email.fill(guest["email"])
        self.guest_first_name.fill(guest["first_name"])
        self.guest_last_name.fill(guest["last_name"])
        self.guest_submit.click()
        self.proceed_as_guest.click()

    def fill_address(self, address: dict, skip: tuple = ()) -> None:
        """Fill the billing address. Fields named in `skip` are left empty
        (used by tests of what happens when a required field is missing)."""
        log.info("Address step: fill address%s", f" (leaving out {', '.join(skip)})" if skip else "")
        self.country.select_option(address["country"])
        for name in ("postal_code", "house_number", "street", "city", "state"):
            field = getattr(self, name)
            field.fill("" if name in skip else address[name])

    def proceed_to_payment(self) -> None:
        log.info("Address step: proceed to payment")
        self.proceed_from_address.click()

    def pay(self, method: str) -> None:
        log.info("Payment step: pay with %s", method)
        self.payment_method.select_option(method)
        self.finish_button.click()
