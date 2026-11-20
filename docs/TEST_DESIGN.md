# Test design map (ISTQB CTFL)

Every test in this suite is tagged with the ISTQB black-box technique it applies. The tag is **required**: a test without one stops the run (`conftest.py`, rule 1). The HTML report shows the technique next to each result.

| Technique | What it means in one line | Where it is used |
|-----------|---------------------------|------------------|
| Equivalence Partitioning | Split inputs into groups the app should treat the same; test one value per group. | `tests/ui/test_login.py`, `tests/ui/test_search.py`, `tests/ui/test_registration.py` (phone), `tests/api/test_products_api.py` |
| Boundary Value Analysis | Test exactly at an edge and one step past it, where off-by-one bugs live. | `tests/ui/test_product_and_cart.py` (quantity), `tests/ui/test_registration.py` (password length 7/8, calendar dates), `tests/api/test_products_api.py` (price filter) |
| Decision Table Testing | List every combination of conditions and the expected result; test each rule. | `tests/api/test_auth_api.py` |
| State Transition Testing | Model the states something moves through and test the moves, valid and invalid. | `tests/ui/test_product_and_cart.py` (cart count), `tests/ui/test_checkout.py` (guest checkout: cart → sign in → address → payment) |
| Error Guessing | Use experience to target likely mistakes. | `tests/ui/test_registration.py` (does the length error message match the rule?) |

## Avoiding side effects on a shared site
- **Registration** rules are checked field by field: the form validates each field when the user leaves it, so the tests never submit and never create accounts.
- **Checkout** uses guest checkout, so no shared account is logged in or changed.

## A judgment call worth noting
The login decision table has four rules, but only three run. Rule R2 (registered email + wrong password) could lock the shared demo account for everyone using this public practice site. It is documented, not executed. Full coverage on paper does not have to mean full execution on a shared environment.

## Retry policy: API tests get one second chance, for network errors only
The API tests call the public practice site, which is sometimes slow. On PR #13, 4 of 7 API tests failed in CI with `APIRequestContext.fetch: Timeout 30000ms exceeded`, and a plain re-run passed. Because the `test` check must pass before anything merges into main, a slow external site would otherwise block pull requests.

The rule (`conftest.py`, rule 5, using `pytest-rerunfailures`):
- **API tests only.** A test marked `api` is retried **once**, after a 5-second pause.
- **Only when the request itself failed:** Playwright's `APIRequestContext` timed out or could not connect (`ECONNREFUSED`, `ECONNRESET`, DNS errors). The patterns are in `conftest.py` (`API_RETRY_ON`).
- **Real failures fail at once.** A failed assertion, including a wrong status code (`assert 404 == 200`), is never retried.
- **UI tests are never retried.** A UI timeout can be a locator or wait problem, and those get triaged and healed ([HEALING_RULES.md](HEALING_RULES.md)), not retried away.
- **Retries stay visible.** The HTML report lists every rerun as its own "Rerun" row with the error, and the Allure report shows it on the test's Retries tab. A test that needed a retry is never shown as a clean first-try pass.

A retry is not a heal: it changes nothing in the test and loosens no assertion. If the same test needs a retry again and again, treat that as a finding and investigate.
