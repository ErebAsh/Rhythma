"""Phone-number validation on ``POST /sms/settings``.

Originally this module asserted that constructing ``SMSSettings`` with a
malformed number raised a Pydantic ``ValidationError``, via a
``@field_validator`` added in edc6517. That validator has been removed and
the tests moved down to the endpoint, for two reasons.

The first is that it never ran. ``field_validator`` was used without being
imported, so ``api/sms.py`` raised ``NameError`` at import time, ``main.py``
could not build the app, and every one of the 27 backend test modules
failed to collect — including this one.

The second is that it contradicted the endpoint. ``save_sms_settings``
already checks the E.164 pattern and answers **400** with a string
``detail``; a field validator answers **422** with a *list* of error
objects. Both clients read ``detail`` as a string when building a user-
facing message (``friendlyAuthError`` in ``web/src/api/client.ts`` does
exactly ``response.data.detail``), so the 422 shape renders as
``[object Object]``. Worse, the sibling condition — enabled with no number
— stayed on 400, so two spellings of the same mistake produced two
different status codes and two different body shapes.

The coverage the original test wanted is kept, asserted against the
behaviour a client actually sees.
"""

import os
import re
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import firebase_admin.auth  # noqa: E402
from test_auth import client, mock_auth_dependencies  # noqa: F401,E402

from api.sms import PHONE_PATTERN, SMSSettings  # noqa: E402
from services.rate_limit_service import RateLimitService  # noqa: E402

SETTINGS_URL = "/api/v1/sms/settings"


@pytest.fixture
def auth_headers(mock_auth_dependencies):  # noqa: F811
    """Same shape as ``test_sms.py`` — firebase-login, not password login."""
    RateLimitService.clear_all()

    firebase_admin.auth.verify_id_token.return_value = {
        "phone_number": "+1234567890",
        "uid": "firebase_uid",
    }
    token_response = client.post(
        "/api/v1/auth/firebase-login",
        json={"id_token": "valid_token"},
        headers={"X-Client-Platform": "mobile"},
    )
    token = token_response.json()["access_token"]

    RateLimitService.clear_all()
    return {"Authorization": f"Bearer {token}"}


# ── The model stays permissive; the route decides ─────────────────────────


def test_the_model_normalizes_but_does_not_reject():
    """``SMSSettings`` is a transport shape, not the validation boundary."""
    settings = SMSSettings(phoneNumber="+919876543210", enabled=False)
    assert settings.normalized_phone == "+919876543210"


def test_surrounding_whitespace_is_stripped():
    settings = SMSSettings(phoneNumber="  +919876543210  ", enabled=False)
    assert settings.normalized_phone == "+919876543210"


def test_an_empty_phone_normalizes_to_none():
    assert SMSSettings(phoneNumber="", enabled=False).normalized_phone is None


def test_a_whitespace_only_phone_normalizes_to_something_falsy():
    """``""`` rather than ``None``, which the route treats identically.

    ``normalized_phone`` returns ``None`` for an empty string but ``""``
    for a whitespace-only one, because the guard runs before the strip.
    The route only ever asks whether the value is falsy, so the difference
    is invisible there — asserted as falsy rather than as ``None`` so this
    documents the behaviour instead of demanding a change nothing needs.
    """
    assert not SMSSettings(phoneNumber="   ", enabled=False).normalized_phone


# ── The pattern itself ────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "number",
    ["+919876543210", "+14155552671", "+441632960961", "+61491570156"],
)
def test_the_pattern_accepts_real_e164_numbers(number):
    assert re.match(PHONE_PATTERN, number)


@pytest.mark.parametrize(
    "number",
    [
        "123",                 # too short, no country code
        "invalid_12345",       # the original test's case
        "919876543210",        # missing the leading +
        "+0123456789",         # country codes do not start with 0
        "+91 98765 43210",     # spaces are not E.164
        "+91-98765-43210",     # nor are dashes
        "++919876543210",
        "+9198765432101234567890",  # past the 15-digit ceiling
    ],
)
def test_the_pattern_rejects_malformed_numbers(number):
    assert not re.match(PHONE_PATTERN, number)


# ── What a client actually receives ───────────────────────────────────────


def test_a_malformed_number_is_a_400_with_a_readable_detail(auth_headers):
    """The case the removed validator would have turned into a 422.

    ``detail`` must be a string. Both clients interpolate it straight into
    a message, so a list here reaches the user as ``[object Object]``.
    """
    response = client.post(
        SETTINGS_URL,
        json={"phoneNumber": "invalid_12345", "enabled": False},
        headers=auth_headers,
    )
    assert response.status_code == 400
    detail = response.json()["detail"]
    assert isinstance(detail, str)
    assert "E.164 format" in detail


def test_enabling_without_a_number_is_also_a_400(auth_headers):
    """The sibling condition, on the same status code and the same shape."""
    response = client.post(
        SETTINGS_URL,
        json={"enabled": True},
        headers=auth_headers,
    )
    assert response.status_code == 400
    detail = response.json()["detail"]
    assert isinstance(detail, str)
    assert "phone number is required" in detail


def test_a_valid_number_is_accepted(auth_headers):
    response = client.post(
        SETTINGS_URL,
        json={"phoneNumber": "+919876543210", "enabled": True},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json() == {"phoneNumber": "+919876543210", "enabled": True}
