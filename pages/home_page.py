from playwright.sync_api import Page, expect

from config.logger import log
from pages.base_page import BasePage


class HomePage(BasePage):
    PATH = "/"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.search_box = page.get_by_test_id("search-query")
        self.search_button = page.get_by_test_id("search-submit")
        self.search_caption = page.get_by_test_id("search-caption")
        self.product_names = page.get_by_test_id("product-name")
        # Product cards are links tagged data-test="product-<id>".
        self.product_cards = page.locator("a[data-test^='product-']")
        self.in_stock_cards = self.product_cards.filter(has_not=page.get_by_test_id("out-of-stock"))

    def search(self, term: str) -> None:
        log.info("Search for %r", term)
        self.search_box.fill(term)
        # Heal H-002: the caption updates before the product list does, so
        # waiting on the caption alone let the test read the OLD list.
        # Now we wait for the search API response, then for the page to
        # show exactly as many products as that response returned.
        with self.page.expect_response(lambda r: "/products/search" in r.url) as search_call:
            self.search_button.click()
        expected_count = len(search_call.value.json()["data"])
        log.info("Search API returned %d product(s); waiting for the page to show them", expected_count)
        expect(self.search_caption).to_contain_text(term)
        expect(self.product_names).to_have_count(expected_count)

    def wait_for_products(self) -> None:
        expect(self.product_names.first).to_be_visible()
        log.info("Product list loaded (%d shown)", self.product_names.count())

    def product_name_texts(self) -> list[str]:
        names = [name.strip() for name in self.product_names.all_inner_texts()]
        log.info("Products on page: %s", ", ".join(names) or "(none)")
        return names

    def open_first_in_stock_product(self) -> None:
        # Heal H-004: quantity and cart tests need a product that can be bought.
        # Stock differs between builds, so the test picks one instead of assuming.
        self.wait_for_products()
        card = self.in_stock_cards.first
        name = card.get_by_test_id("product-name")
        log.info("Open first in-stock product: %s", name.inner_text().strip())
        name.click()
