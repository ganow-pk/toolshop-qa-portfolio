"""Login page tests.

Equivalence Partitioning: inputs are split into groups (partitions) that the
app should treat the same way. One test value per partition is enough.

Partitions used:
  valid    - registered email + correct password       -> signed in
  invalid  - unregistered email + any password         -> "invalid email or password"
  invalid  - badly formatted email                     -> email field error
  invalid  - empty email                               -> email field error
  invalid  - empty password                            -> password field error

Left out on purpose: registered email + wrong password. On a shared public demo
site, failed attempts against the demo account could lock it for everyone.
See docs/HEALING_RULES.md, "Never harm a shared environment".
"""
import re

import pytest
from playwright.sync_api import expect

from config import settings

pytestmark = [pytest.mark.ui]


@pytest.mark.smoke
@pytest.mark.healed("H-001")
@pytest.mark.istqb("Equivalence Partitioning")
def test_valid_credentials_open_my_account(login_page):
    login_page.login(settings.CUSTOMER_EMAIL, settings.CUSTOMER_PASSWORD)

    expect(login_page.page).to_have_url(re.compile(r"/account"))
    expect(login_page.header.user_menu).to_be_visible()


@pytest.mark.istqb("Equivalence Partitioning")
def test_unregistered_email_is_rejected(login_page):
    login_page.login(settings.UNREGISTERED_EMAIL, "AnyPassword1!")

    expect(login_page.login_error).to_be_visible()
    expect(login_page.page).to_have_url(re.compile(r"/auth/login"))


@pytest.mark.istqb("Equivalence Partitioning")
@pytest.mark.parametrize(
    "email, password, error_field",
    [
        ("not-an-email", "AnyPassword1!", "email_error"),
        ("", "AnyPassword1!", "email_error"),
        (settings.UNREGISTERED_EMAIL, "", "password_error"),
    ],
    ids=["bad-email-format", "empty-email", "empty-password"],
)
def test_field_validation_messages(login_page, email, password, error_field):
    login_page.login(email, password)

    expect(getattr(login_page, error_field)).to_be_visible()
    expect(login_page.page).to_have_url(re.compile(r"/auth/login"))
