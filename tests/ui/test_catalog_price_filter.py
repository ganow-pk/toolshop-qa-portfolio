"""Price range slider on the home page.

Equivalence Partitioning: a range that leaves out some of the products shown
by default must change the list, and every product left must be inside it.

Boundary Value Analysis around a real product price P, taken from the live
list (the cheapest product on the first page, e.g. 9.17 on main):
  The slider moves in whole dollars and no product has a whole-dollar price,
  so the tightest edges around P are floor(P) and ceil(P) (9 and 10).
    floor(P)   - ceil(P)      P is inside both edges     -> product shown
    floor(P)-1 - floor(P)     max one step below P       -> product hidden
    ceil(P)    - ceil(P)+1    min one step above P       -> product hidden
Each case also checks that every shown price is inside the range the slider shows.
"""
import math

import allure
import pytest

pytestmark = [pytest.mark.ui]

ISSUE = "#2 Price range slider does not filter the product list (with-bugs)"


def prices_outside(prices: list[float], low: int, high: int) -> list[float]:
    return [price for price in prices if not low <= price <= high]


@allure.issue("2", name=ISSUE)
@pytest.mark.istqb("Equivalence Partitioning")
def test_narrowing_the_price_range_filters_the_list(home_page):
    home_page.wait_for_products()
    names_before = home_page.product_name_texts()
    dearest = max(home_page.product_price_values())

    # Lower the max just below the dearest product shown, so it must disappear.
    low, _ = home_page.price_range_shown()
    home_page.set_price_range(low, math.floor(dearest))

    low, high = home_page.price_range_shown()
    prices = home_page.product_price_values()
    assert home_page.product_name_texts() != names_before, (
        f"The product list did not change after setting the price range to {low}-{high}")
    outside = prices_outside(prices, low, high)
    assert not outside, f"Prices outside the slider range {low}-{high}: {outside}"


@allure.issue("2", name=ISSUE)
@pytest.mark.istqb("Boundary Value Analysis")
@pytest.mark.parametrize(
    "low_offset, high_offset, product_shown",
    [
        (0, 1, True),     # floor(P) - ceil(P): P inside both edges
        (-1, 0, False),   # floor(P)-1 - floor(P): max one step below P
        (1, 2, False),    # ceil(P) - ceil(P)+1: min one step above P
    ],
    ids=["price-inside-tightest-range", "max-one-step-below-price", "min-one-step-above-price"],
)
def test_price_range_edges_around_a_real_price(home_page, low_offset, high_offset, product_shown):
    home_page.wait_for_products()
    prices = home_page.product_price_values()
    price = min(prices)
    product = home_page.product_name_texts()[prices.index(price)]
    assert price != int(price), (
        f"Test data changed: {product} costs a whole {price}; these edges assume cents")
    edge = math.floor(price)

    home_page.set_price_range(edge + low_offset, edge + high_offset)

    low, high = home_page.price_range_shown()
    names = home_page.product_name_texts()
    outside = prices_outside(home_page.product_price_values(), low, high)
    assert not outside, f"Prices outside the slider range {low}-{high}: {outside}"
    if product_shown:
        assert product in names, f"{product} ({price}) is inside {low}-{high} but not listed"
    else:
        assert product not in names, f"{product} ({price}) is outside {low}-{high} but still listed"
