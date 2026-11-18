"""Top navigation bar. It appears on every page, so it is a component, not a page."""
from playwright.sync_api import Page


class Header:
    def __init__(self, page: Page) -> None:
        self.sign_in = page.get_by_test_id("nav-sign-in")
        self.user_menu = page.get_by_test_id("nav-menu")
        self.cart = page.get_by_test_id("nav-cart")
        self.cart_quantity = page.get_by_test_id("cart-quantity")
