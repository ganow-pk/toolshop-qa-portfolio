"""Login API tests.

Decision Table Testing: list every combination of conditions and the
expected action, then test each row (a "rule").

  Rule | Email registered? | Password correct? | Expected
  -----|-------------------|-------------------|-------------------------
  R1   | yes               | yes               | 200 + access token
  R2   | yes               | no                | 401  (NOT RUN, see below)
  R3   | no                | yes*              | 401
  R4   | no                | no                | 401
  * "correct" here means the demo password, sent with an unknown email.

R2 is documented but not executed: repeated wrong passwords against the shared
demo account could lock it for every other person using this practice site.
Knowing which test NOT to run is part of the job.
"""
import pytest

from config import settings

pytestmark = [pytest.mark.api]


@pytest.mark.smoke
@pytest.mark.healed("H-001")
@pytest.mark.istqb("Decision Table Testing")
def test_r1_registered_email_correct_password_returns_token(api):
    response = api.login(settings.CUSTOMER_EMAIL, settings.CUSTOMER_PASSWORD)

    assert response.status == 200, response.text()
    body = response.json()
    assert body.get("access_token"), f"No access_token in {body}"


@pytest.mark.istqb("Decision Table Testing")
@pytest.mark.parametrize(
    "password",
    [settings.CUSTOMER_PASSWORD, "WrongPassword1!"],
    ids=["R3-unknown-email-demo-password", "R4-unknown-email-wrong-password"],
)
def test_unregistered_email_is_unauthorized(api, password):
    response = api.login(settings.UNREGISTERED_EMAIL, password)

    assert response.status == 401, f"Expected 401, got {response.status}: {response.text()}"
    assert "access_token" not in response.json()
