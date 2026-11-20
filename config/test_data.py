"""Test data in one place, separate from the tests that use it.

Every value here is invented for testing. Nothing belongs to a real person.
"""

# Guest checkout: the order confirmation goes to this (non-existent) address.
GUEST = {
    "email": "guest.tester@example.com",
    "first_name": "Pat",
    "last_name": "Tester",
}

# Billing address for checkout. Country uses the form's option value.
ADDRESS = {
    "country": "US",
    "postal_code": "80202",
    "house_number": "100",
    "street": "Test Street",
    "city": "Denver",
    "state": "CO",
}

PAYMENT_METHOD = "cash-on-delivery"
