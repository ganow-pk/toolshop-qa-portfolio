"""Catalog sorting on the home page.

Equivalence Partitioning: each sort option is its own group (sort field x
direction), so each option is tested once. The check: after picking the
option, the products on the first page are in the order the option names.

CO2 rating options are not covered here (decided 2026-11-21):
  - the card shows the rating only as a highlighted letter, with no data-test
    text to read, so checking it would break the locator rule;
  - the option labels differ between builds ("CO2 Rating (A - E)" on main,
    "CO2 Rating (Best First)" on with-bugs), so one test could not pick the
    same option on both.
"""
import allure
import pytest

pytestmark = [pytest.mark.ui]


@allure.issue("6", name="#6 Sorting is reversed for every sort option (with-bugs)")
@pytest.mark.istqb("Equivalence Partitioning")
@pytest.mark.parametrize(
    "option, field, descending",
    [
        ("Name (A - Z)", "name", False),
        ("Name (Z - A)", "name", True),
        ("Price (High - Low)", "price", True),
        ("Price (Low - High)", "price", False),
    ],
    ids=["name-a-z", "name-z-a", "price-high-low", "price-low-high"],
)
def test_sort_option_orders_the_first_page(home_page, option, field, descending):
    home_page.wait_for_products()
    home_page.sort_by(option)

    if field == "name":
        shown = home_page.product_name_texts()
        expected = sorted(shown, key=str.casefold, reverse=descending)
    else:
        shown = home_page.product_price_values()
        expected = sorted(shown, reverse=descending)

    assert len(shown) > 1, f"Need at least two products to check the order, got {shown}"
    assert shown == expected, (
        f"'{option}' did not sort by {field}.\n"
        f"  Shown:    {shown}\n"
        f"  Expected: {expected}"
    )
