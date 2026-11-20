"""Registration form rules, checked field by field without submitting.

The form validates each field when the user leaves it, so no accounts are
created on the shared demo site.

Boundary Value Analysis: test right at an edge and one step past it.
  Password length: rule is "at least 8 characters" -> test 7 and 8.
  Date of birth: must be a real calendar date -> leap-day and month edges.

Equivalence Partitioning: phone must be digits only -> one value per group.

Every password below also meets the other rules (upper and lower case,
a number, a symbol), so only the length changes between 7 and 8.
"""
import pytest
from playwright.sync_api import expect

pytestmark = [pytest.mark.ui]

PASSWORD_7 = "Abcde1!"    # 7 characters: one below the minimum
PASSWORD_8 = "Abcdef1!"   # 8 characters: exactly the minimum


@pytest.mark.istqb("Boundary Value Analysis")
def test_password_one_below_minimum_length_is_rejected(register_page):
    register_page.enter("password", PASSWORD_7)

    expect(register_page.error("password")).to_be_visible()


@pytest.mark.istqb("Boundary Value Analysis")
def test_password_at_minimum_length_is_accepted(register_page):
    register_page.enter("password", PASSWORD_8)

    expect(register_page.error("password")).to_be_hidden()


@pytest.mark.istqb("Error Guessing")
def test_password_length_message_matches_the_rule(register_page):
    """The rule list under the field says "at least 8 characters".
    The length error message should say the same number."""
    register_page.enter("password", PASSWORD_7)

    expect(register_page.error("password")).to_contain_text("8")


@pytest.mark.istqb("Boundary Value Analysis")
@pytest.mark.parametrize(
    "dob, valid",
    [
        ("2000-02-29", True),    # leap year: Feb 29 exists
        ("2001-02-29", False),   # not a leap year: one day past Feb 28
        ("1999-12-31", True),    # last day of the year
        ("2000-13-01", False),   # one month past December
        ("2000-1-01", False),    # wrong format (month needs two digits)
    ],
    ids=["leap-day", "feb-29-non-leap", "dec-31", "month-13", "short-month-format"],
)
def test_date_of_birth_must_be_a_real_calendar_date(register_page, dob, valid):
    register_page.enter("dob", dob)

    error = register_page.error("dob")
    if valid:
        expect(error).to_be_hidden()
    else:
        expect(error).to_be_visible()


@pytest.mark.istqb("Equivalence Partitioning")
@pytest.mark.parametrize(
    "phone, valid",
    [
        ("5551234567", True),     # digits only
        ("555-123-4567", False),  # digits with separators
        ("phone", False),         # letters
    ],
    ids=["digits", "with-dashes", "letters"],
)
def test_phone_accepts_digits_only(register_page, phone, valid):
    register_page.enter("phone", phone)

    error = register_page.error("phone")
    if valid:
        expect(error).to_be_hidden()
    else:
        expect(error).to_be_visible()
