import pytest
from unittest.mock import patch

from test_auth import client, mock_auth_dependencies
import firebase_admin.auth
from api.assistant import _assistant_rate_history, ASSISTANT_RATE_LIMIT


@pytest.fixture
def auth_headers(mock_auth_dependencies):
    firebase_admin.auth.verify_id_token.return_value = {"phone_number": "+1234567890", "uid": "firebase_uid"}
    token_response = client.post(
        "/api/v1/auth/firebase-login",
        json={"id_token": "valid_token"}
    )
    token = token_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_chat_rate_limit_exceeded(auth_headers):
    _assistant_rate_history.clear()

    payload = {"message": "Hello", "language": "en"}

    # Exhaust the rate limit by sending ASSISTANT_RATE_LIMIT requests
    for _ in range(ASSISTANT_RATE_LIMIT):
        response = client.post("/api/v1/assistant/chat", json=payload, headers=auth_headers)
        assert response.status_code == 200

    # Next request should be rate limited
    response = client.post("/api/v1/assistant/chat", json=payload, headers=auth_headers)
    assert response.status_code == 429
    assert "Rate limit exceeded" in response.json()["detail"]
    assert "Retry-After" in response.headers


def test_chat_allowed_within_rate_limit(auth_headers):
    _assistant_rate_history.clear()

    payload = {"message": "Hello", "language": "en"}

    # Send one request — should succeed
    response = client.post("/api/v1/assistant/chat", json=payload, headers=auth_headers)
    assert response.status_code == 200


def test_rate_limit_resets_after_window(monkeypatch, auth_headers):
    _assistant_rate_history.clear()

    # Use a very short window for testing
    monkeypatch.setattr("api.assistant.ASSISTANT_RATE_WINDOW", 1)
    monkeypatch.setattr("api.assistant.ASSISTANT_RATE_LIMIT", 1)

    payload = {"message": "Hello", "language": "en"}

    # First request should succeed
    response = client.post("/api/v1/assistant/chat", json=payload, headers=auth_headers)
    assert response.status_code == 200

    # Second request should be rate limited
    response = client.post("/api/v1/assistant/chat", json=payload, headers=auth_headers)
    assert response.status_code == 429

    # After the window passes, request should succeed again
    import time
    time.sleep(1.1)
    _assistant_rate_history.clear()

    response = client.post("/api/v1/assistant/chat", json=payload, headers=auth_headers)
    assert response.status_code == 200