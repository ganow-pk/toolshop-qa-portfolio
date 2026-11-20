"""One place for every setting the suite needs.

Change a value here (or set the matching environment variable) and the whole
suite follows. Tests and page objects never hard-code URLs or credentials.

Switch the whole suite to another environment with one word:
    TOOLSHOP_ENV=with-bugs pytest
"""
import os

# Environment profiles. Each one is a complete description of a place to test.
#   route_prefix: "/#" for builds that use hash routing (pages live at /#/auth/login)
#   guest_checkout: whether the build offers "Continue as Guest" at checkout
ENVIRONMENTS = {
    "main": {
        "base_url": "https://practicesoftwaretesting.com",
        "api_url": "https://api.practicesoftwaretesting.com",
        "route_prefix": "",
        "guest_checkout": True,
    },
    # Intentionally buggy build of the same app, made for bug-hunting practice.
    "with-bugs": {
        "base_url": "https://with-bugs.practicesoftwaretesting.com",
        "api_url": "https://api-with-bugs.practicesoftwaretesting.com",
        "route_prefix": "/#",
        # No guest checkout on this build (checked 2026-11-20): checkout tests skip.
        "guest_checkout": False,
    },
}

ENV_NAME = os.getenv("TOOLSHOP_ENV", "main")
if ENV_NAME not in ENVIRONMENTS:
    raise ValueError(f"TOOLSHOP_ENV={ENV_NAME!r} is not one of {sorted(ENVIRONMENTS)}")
_env = ENVIRONMENTS[ENV_NAME]

# Single values can still be overridden one at a time.
BASE_URL = os.getenv("TOOLSHOP_BASE_URL", _env["base_url"])
API_URL = os.getenv("TOOLSHOP_API_URL", _env["api_url"])
ROUTE_PREFIX = os.getenv("TOOLSHOP_ROUTE_PREFIX", _env["route_prefix"])
GUEST_CHECKOUT = _env["guest_checkout"]

# Public demo account published by the site for practice.
# Heal H-001: "customer@" was locked by other users of this public site
# (API answered 423 Locked), so the suite uses the second demo account.
# Read from the environment first so real secrets are never committed.
CUSTOMER_EMAIL = os.getenv("TOOLSHOP_CUSTOMER_EMAIL", "customer2@practicesoftwaretesting.com")
CUSTOMER_PASSWORD = os.getenv("TOOLSHOP_CUSTOMER_PASSWORD", "welcome01")

# An address that is NOT registered. Negative login tests use this so they
# never count failed attempts against the shared demo account (see docs/HEALING_RULES.md).
UNREGISTERED_EMAIL = "not-a-user@example.com"

# Screenshots embedded in the HTML report for UI tests:
#   "all"      - every UI test gets a screenshot (evidence on passes too)
#   "failures" - only failed UI tests
#   "off"      - none
REPORT_SCREENSHOTS = os.getenv("TOOLSHOP_REPORT_SCREENSHOTS", "all")

# Attribute the app puts on elements for testing: <button data-test="login-submit">
TEST_ID_ATTRIBUTE = "data-test"

# Allure report links (see README, "Allure report").
#   @allure.issue("8") on a test links to GitHub issue #8.
#   A test marked @pytest.mark.healed(...) links to the heal log.
ISSUE_URL_PATTERN = "https://github.com/ganow-pk/toolshop-qa-portfolio/issues/{}"
HEAL_LOG_URL = "https://github.com/ganow-pk/toolshop-qa-portfolio/blob/main/docs/heal_log.md"
