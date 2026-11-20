from playwright.sync_api import Page

from config.logger import log
from pages.base_page import BasePage


class CartPage(BasePage):
    """Checkout step 1: the cart."""

    PATH = "/checkout"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.product_titles = page.get_by_test_id("product-title")
        self.quantities = page.get_by_test_id("product-quantity")
        self.total = page.get_by_test_id("cart-total")
        self.proceed_button = page.get_by_test_id("proceed-1")

    def proceed(self) -> None:
        log.info("Cart: proceed to checkout")
        self.proceed_button.click()
