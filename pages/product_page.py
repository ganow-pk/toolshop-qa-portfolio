from playwright.sync_api import Page, expect

from config.logger import log
from pages.base_page import BasePage


class ProductPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.name = page.get_by_test_id("product-name")
        self.quantity = page.get_by_test_id("quantity")
        self.increase = page.get_by_test_id("increase-quantity")
        self.decrease = page.get_by_test_id("decrease-quantity")
        self.add_to_cart_button = page.get_by_test_id("add-to-cart")

    def wait_until_loaded(self) -> None:
        expect(self.add_to_cart_button).to_be_visible()
        log.info("Product page loaded: %s (quantity %s)",
                 self.name.inner_text().strip(), self.quantity.input_value())

    def click_increase(self) -> None:
        self.increase.click()
        log.info("Clicked + (quantity now %s)", self.quantity.input_value())

    def click_decrease(self) -> None:
        self.decrease.click()
        log.info("Clicked - (quantity now %s)", self.quantity.input_value())

    def add_to_cart(self) -> None:
        self.add_to_cart_button.click()
        log.info("Clicked Add to cart")
