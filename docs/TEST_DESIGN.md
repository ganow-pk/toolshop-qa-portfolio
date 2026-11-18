# Test design map (ISTQB CTFL)

Every test in this suite is tagged with the ISTQB black-box technique it applies. The tag is **required**: a test without one stops the run (`conftest.py`, rule 1). The HTML report shows the technique next to each result.

| Technique | What it means in one line | Where it is used |
|-----------|---------------------------|------------------|
| Equivalence Partitioning | Split inputs into groups the app should treat the same; test one value per group. | `tests/ui/test_login.py`, `tests/ui/test_search.py`, `tests/api/test_products_api.py` |
| Boundary Value Analysis | Test exactly at an edge and one step past it, where off-by-one bugs live. | `tests/ui/test_product_and_cart.py` (quantity), `tests/api/test_products_api.py` (price filter) |
| Decision Table Testing | List every combination of conditions and the expected result; test each rule. | `tests/api/test_auth_api.py` |
| State Transition Testing | Model the states something moves through and test the moves. | `tests/ui/test_product_and_cart.py` (cart) |

## A judgment call worth noting
The login decision table has four rules, but only three run. Rule R2 (registered email + wrong password) could lock the shared demo account for everyone using this public practice site. It is documented, not executed. Full coverage on paper does not have to mean full execution on a shared environment.
