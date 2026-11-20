"""Guest checkout as a state machine.

State Transition Testing: model the states and test the moves between them.

  [Cart] --proceed--> [Sign in] --continue as guest--> [Address]
         --complete address--> [Payment] --pay--> [Payment accepted]

Valid moves are walked end to end, checking that each state shows what it should.
Invalid moves are checked too: the flow must not advance when a required
step is incomplete.

Uses guest checkout, so no shared account is logged in or changed.
Builds without guest checkout (with-bugs) skip these tests with a visible reason,
so a missing feature never shows up as a product failure.
"""
import pytest
from playwright.sync_api import expect

from config import settings, test_data

pytestmark = [
    pytest.mark.ui,
    pytest.mark.skipif(
        not settings.GUEST_CHECKOUT,
        reason=f"Guest checkout is not available on the {settings.ENV_NAME} build",
    ),
]


@pytest.mark.istqb("State Transition Testing")
def test_guest_checkout_moves_through_every_state(cart_with_item, checkout):
    # State: Cart
    expect(cart_with_item.product_titles).to_have_count(1)
    cart_with_item.proceed()

    # State: Sign in -> continue as guest
    checkout.open_guest_tab()
    expect(checkout.guest_email).to_be_visible()
    checkout.continue_as_guest(test_data.GUEST)

    # State: Address
    expect(checkout.street).to_be_visible()
    checkout.fill_address(test_data.ADDRESS)
    checkout.proceed_to_payment()

    # State: Payment -> Payment accepted
    expect(checkout.payment_method).to_be_visible()
    checkout.pay(test_data.PAYMENT_METHOD)
    expect(checkout.payment_success).to_be_visible()


@pytest.mark.istqb("State Transition Testing")
def test_address_step_does_not_advance_with_a_missing_street(cart_with_item, checkout):
    cart_with_item.proceed()
    checkout.continue_as_guest(test_data.GUEST)

    checkout.fill_address(test_data.ADDRESS, skip=("street",))

    expect(checkout.proceed_from_address).to_be_disabled()


@pytest.mark.istqb("State Transition Testing")
def test_payment_step_cannot_finish_without_a_payment_method(cart_with_item, checkout):
    cart_with_item.proceed()
    checkout.continue_as_guest(test_data.GUEST)
    checkout.fill_address(test_data.ADDRESS)
    checkout.proceed_to_payment()

    expect(checkout.payment_method).to_be_visible()
    expect(checkout.finish_button).to_be_disabled()
