"""Product detail and cart tests.

Boundary Value Analysis: test right at an edge and one step past it.
  Quantity starts at 1, the lowest valid value.
  Below the edge: pressing "-" at 1 must not go to 0.
  Above the edge: pressing "+" at 1 must give 2.

State Transition Testing: the cart moves between states.
  empty --add--> 1 item --add again--> 2 items
"""
import pytest
from playwright.sync_api import expect

pytestmark = [pytest.mark.ui]


@pytest.mark.istqb("Boundary Value Analysis")
def test_quantity_cannot_go_below_one(product_page):
    expect(product_page.quantity).to_have_value("1")

    product_page.click_decrease()

    expect(product_page.quantity).to_have_value("1")


@pytest.mark.istqb("Boundary Value Analysis")
def test_quantity_increases_from_one_to_two(product_page):
    expect(product_page.quantity).to_have_value("1")

    product_page.click_increase()

    expect(product_page.quantity).to_have_value("2")


@pytest.mark.smoke
@pytest.mark.istqb("State Transition Testing")
def test_cart_count_follows_each_add(product_page):
    cart_count = product_page.header.cart_quantity

    product_page.add_to_cart()
    expect(cart_count).to_have_text("1")

    product_page.add_to_cart()
    expect(cart_count).to_have_text("2")
