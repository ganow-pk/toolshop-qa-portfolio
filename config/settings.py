"""One place for every setting the suite needs.

Change a value here (or set the matching environment variable) and the whole
suite follows. Tests and page objects never hard-code URLs or credentials.

Example: point the suite at the intentionally buggy build of the app
    TOOLSHOP_BASE_URL=https://with-bugs.practicesoftwaretesting.com pytest
"""
import os

# Web app and REST API under test (public practice site by Testsmith).
BASE_URL = os.getenv("TOOLSHOP_BASE_URL", "https://practicesoftwaretesting.com")
API_URL = os.getenv("TOOLSHOP_API_URL", "https://api.practicesoftwaretesting.com")

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
