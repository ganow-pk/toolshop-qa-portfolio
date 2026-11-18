"""Product search tests.

Equivalence Partitioning on the search term:
  term that matches products    -> only matching products are listed
  term that matches nothing     -> empty result, no error
"""
import pytest
from playwright.sync_api import expect

pytestmark = [pytest.mark.ui]


@pytest.mark.smoke
@pytest.mark.healed("H-002")
@pytest.mark.istqb("Equivalence Partitioning")
def test_search_lists_only_matching_products(home_page):
    home_page.wait_for_products()
    home_page.search("Pliers")

    names = home_page.product_name_texts()
    assert names, "Expected at least one product for 'Pliers'"
    not_matching = [n for n in names if "pliers" not in n.lower()]
    assert not not_matching, f"Products that do not match 'Pliers': {not_matching}"


@pytest.mark.istqb("Equivalence Partitioning")
def test_search_with_no_match_shows_no_products(home_page):
    home_page.wait_for_products()
    home_page.search("zzz-no-such-tool")

    expect(home_page.product_names).to_have_count(0)
