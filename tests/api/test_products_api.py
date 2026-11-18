"""Products API tests.

Equivalence Partitioning: one valid search term, one that matches nothing.
Boundary Value Analysis: the price filter must include products priced exactly
at its edges and exclude anything outside them.
"""
import pytest

pytestmark = [pytest.mark.api]

REQUIRED_FIELDS = {"id", "name", "price"}


def products_from(response) -> list[dict]:
    assert response.status == 200, f"HTTP {response.status}: {response.text()}"
    return response.json()["data"]


@pytest.mark.smoke
@pytest.mark.istqb("Equivalence Partitioning")
def test_product_list_returns_products_with_required_fields(api):
    products = products_from(api.list_products())

    assert products, "Product list is empty"
    for product in products:
        missing = REQUIRED_FIELDS - product.keys()
        assert not missing, f"Product {product.get('id')} is missing {missing}"


@pytest.mark.istqb("Equivalence Partitioning")
def test_search_returns_only_matching_products(api):
    products = products_from(api.search_products("pliers"))

    assert products, "Expected products for 'pliers'"
    not_matching = [p["name"] for p in products if "pliers" not in p["name"].lower()]
    assert not not_matching, f"Not matching 'pliers': {not_matching}"


@pytest.mark.istqb("Equivalence Partitioning")
def test_search_with_no_match_returns_empty_list(api):
    assert products_from(api.search_products("zzz-no-such-tool")) == []


@pytest.mark.istqb("Boundary Value Analysis")
def test_price_filter_stays_inside_its_boundaries(api):
    # Step 1: find a real price to use as an exact boundary.
    edge = float(products_from(api.list_products())[0]["price"])
    low, high = edge, edge + 10

    # Step 2: filter, then check every product sits inside [low, high].
    products = products_from(api.products_in_price_range(low, high))

    prices = [float(p["price"]) for p in products]
    assert prices, f"Expected at least the product priced exactly {edge}"
    assert edge in prices, f"Product priced exactly at the lower boundary ({edge}) was excluded"
    outside = [p for p in prices if not low <= p <= high]
    assert not outside, f"Prices outside {low}-{high}: {outside}"
