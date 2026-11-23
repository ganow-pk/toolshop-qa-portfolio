"""Category filter on the home page.

Error Guessing: a category name that failed to load tends to show up as an
empty label or a placeholder such as "Undefined" or "null". Every category
the customer can pick must have a real name.

Not asserted on purpose (checked on main 2026-11-21): "every category lists
at least one product". Main does not guarantee it: "Grinder" has no products
at all, and "Workbench" has none inside the slider's default 1-100 range.
"""
import allure
import pytest

pytestmark = [pytest.mark.ui]

PLACEHOLDER_NAMES = {"", "undefined", "null", "none", "nan"}


@allure.issue("3", name='#3 Category filter shows an "Undefined" entry (with-bugs)')
@pytest.mark.istqb("Error Guessing")
def test_every_category_in_the_filter_has_a_real_name(home_page):
    labels = home_page.category_labels()

    assert labels, "The category filter lists no categories"
    placeholders = [label for label in labels if label.strip().lower() in PLACEHOLDER_NAMES]
    assert not placeholders, f"Category labels that are not real names: {placeholders} (all: {labels})"
