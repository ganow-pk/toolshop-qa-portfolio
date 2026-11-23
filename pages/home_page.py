from playwright.sync_api import Page, Request, expect

from config import settings
from config.logger import log
from pages.base_page import BasePage

# The price slider moves 1 dollar per arrow key and 20 dollars per Page Up / Page Down
# (10% of its 0-200 scale, checked on both builds 2026-11-21). Every key press
# asks the API for a new product list, so big jumps keep the number of calls low
# (a shared site: no flooding).
SLIDER_PAGE_STEP = 20


class HomePage(BasePage):
    PATH = "/"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.search_box = page.get_by_test_id("search-query")
        self.search_button = page.get_by_test_id("search-submit")
        self.search_caption = page.get_by_test_id("search-caption")
        self.product_names = page.get_by_test_id("product-name")
        self.product_prices = page.get_by_test_id("product-price")
        # Product cards are links tagged data-test="product-<id>".
        self.product_cards = page.locator("a[data-test^='product-']")
        self.in_stock_cards = self.product_cards.filter(has_not=page.get_by_test_id("out-of-stock"))

        # Filters column
        self.sort_select = page.get_by_test_id("sort")
        # Category checkboxes are tagged data-test="category-<id>".
        self.category_checkboxes = page.locator("input[data-test^='category-']")
        # The price slider is a third-party widget (ngx-slider) with no data-test
        # attributes. Its two handles are found by their accessibility role and
        # label instead: the most stable hook the app offers for them.
        self.price_min_handle = page.get_by_role("slider", name="ngx-slider", exact=True)
        self.price_max_handle = page.get_by_role("slider", name="ngx-slider-max", exact=True)

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

    def product_price_values(self) -> list[float]:
        """Prices on the cards as numbers: "$14.15" -> 14.15."""
        prices = [float(text.strip().lstrip("$").replace(",", ""))
                  for text in self.product_prices.all_inner_texts()]
        log.info("Prices on page: %s", ", ".join(f"{p:.2f}" for p in prices) or "(none)")
        return prices

    def open_first_in_stock_product(self) -> None:
        # Heal H-004: quantity and cart tests need a product that can be bought.
        # Stock differs between builds, so the test picks one instead of assuming.
        self.wait_for_products()
        card = self.in_stock_cards.first
        name = card.get_by_test_id("product-name")
        log.info("Open first in-stock product: %s", name.inner_text().strip())
        name.click()

    # ---------- Sort ----------

    def sort_by(self, option_label: str) -> None:
        """Pick a sort option by the text the customer sees, e.g. "Name (A - Z)"."""
        log.info("Sort by %r", option_label)
        with self.page.expect_request(self._is_product_list_call) as list_call:
            self.sort_select.select_option(label=option_label)
        self._wait_until_page_shows(list_call.value)

    # ---------- Price range slider ----------

    def price_range_shown(self) -> tuple[int, int]:
        """The range the slider currently shows: (min handle, max handle)."""
        low = int(self.price_min_handle.get_attribute("aria-valuenow"))
        high = int(self.price_max_handle.get_attribute("aria-valuenow"))
        log.info("Price slider shows %d-%d", low, high)
        return low, high

    def set_price_range(self, low: int, high: int) -> None:
        """Move the slider handles with the keyboard to low-high (whole dollars),
        then wait until the page shows the product list for the final range."""
        log.info("Set price range to %d-%d", low, high)
        current_low, _ = self.price_range_shown()
        # A handle cannot pass the other one, so move the max handle first,
        # unless the new range lies entirely below the current min.
        if high < current_low:
            moves = [(self.price_min_handle, low), (self.price_max_handle, high)]
        else:
            moves = [(self.price_max_handle, high), (self.price_min_handle, low)]
        presses = [(handle, key) for handle, target in moves
                   for key in self._keys_to_move(handle, target)]
        if not presses:
            log.info("Slider already shows %d-%d", low, high)
            return

        # Each key press triggers a product-list call, and the page draws
        # whichever answer arrives LAST, even an older one. So wait for each
        # answer before the next press: calls never overlap, and the last
        # answer the page draws is the one for the final range.
        for handle, key in presses:
            with self.page.expect_request(self._is_product_list_call) as list_call:
                handle.press(key)
            list_call.value.response()
        expect(self.price_min_handle).to_have_attribute("aria-valuenow", str(low))
        expect(self.price_max_handle).to_have_attribute("aria-valuenow", str(high))
        self._wait_until_page_shows(list_call.value)

    @staticmethod
    def _keys_to_move(handle, target: int) -> list[str]:
        """Keys that move a handle from where it is to target: Page Up/Down for
        each full 20-dollar jump, then arrow keys for the rest."""
        distance = target - int(handle.get_attribute("aria-valuenow"))
        jump_key, step_key = ("PageUp", "ArrowRight") if distance > 0 else ("PageDown", "ArrowLeft")
        jumps, steps = divmod(abs(distance), SLIDER_PAGE_STEP)
        return [jump_key] * jumps + [step_key] * steps

    # ---------- Categories ----------

    def category_labels(self) -> list[str]:
        """The name shown next to each category checkbox, top to bottom."""
        expect(self.category_checkboxes.first).to_be_visible()
        # Each checkbox sits inside its <label>; the label's text is the category name.
        labels = self.category_checkboxes.evaluate_all(
            "boxes => boxes.map(box => box.closest('label').innerText.trim())")
        log.info("Categories in the filter: %s", ", ".join(repr(label) for label in labels))
        return labels

    # ---------- Waiting for the product list ----------

    @staticmethod
    def _is_product_list_call(request: Request) -> bool:
        """The call that loads the product grid: <API>/products, with or without
        a query string (main sends its filters in the body, with-bugs in the URL)."""
        return (request.url.split("?")[0] == f"{settings.API_URL}/products"
                and request.method != "OPTIONS")

    def _wait_until_page_shows(self, list_call: Request) -> None:
        """Wait for the product-list API answer, then for the page to show
        exactly those products in that order. Reading the page any earlier
        could read the old list (the same trap as heal H-002)."""
        response = list_call.response()
        assert response is not None, f"Product list call failed: {list_call.url}"
        names = [product["name"] for product in response.json()["data"]]
        log.info("Products API returned %d product(s); waiting for the page to show them", len(names))
        expect(self.product_names).to_have_text(names)
