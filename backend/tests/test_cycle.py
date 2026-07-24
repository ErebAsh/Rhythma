import pytest
from unittest.mock import patch
from tests.test_auth import client, mock_auth_dependencies
import firebase_admin.auth

@pytest.fixture
def auth_headers(mock_auth_dependencies):
    firebase_admin.auth.verify_id_token.return_value = {"phone_number": "+1234567890", "uid": "firebase_uid"}
    token_response = client.post(
        "/api/v1/auth/firebase-login",
        json={"id_token": "valid_token"}
    )
    token = token_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def mock_cycle_service():
    with patch("api.cycle.CycleService") as MockCycleService:
        yield MockCycleService

def test_log_cycle_success(auth_headers, mock_cycle_service):
    mock_cycle_service.upsert_log.return_value = "log-123"
    payload = {
        "start_date": "2026-05-01",
        "flow_intensity": "medium",
        "symptoms": ["cramps"]
    }
    response = client.post("/api/v1/cycle/log", json=payload, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == "log-123"
    # assert the payload is included in the response
    assert response.json()["data"]["flow_intensity"] == "medium"

def test_log_cycle_missing_required_fields(auth_headers, mock_cycle_service):
    payload = {
        "flow_intensity": "medium"
    }
    response = client.post("/api/v1/cycle/log", json=payload, headers=auth_headers)
    assert response.status_code == 422
    assert "start_date" in str(response.json()["detail"])

def test_log_cycle_invalid_dates(auth_headers, mock_cycle_service):
    payload = {
        "start_date": "not-a-date"
    }
    response = client.post("/api/v1/cycle/log", json=payload, headers=auth_headers)
    assert response.status_code == 422
    assert "start_date" in str(response.json()["detail"])

def test_log_cycle_invalid_payload(auth_headers, mock_cycle_service):
    payload = {
        "start_date": "2026-05-01",
        "sleep_hours": "not-a-number"
    }
    response = client.post("/api/v1/cycle/log", json=payload, headers=auth_headers)
    assert response.status_code == 422
    assert "sleep_hours" in str(response.json()["detail"])

def test_get_cycle_history_success(auth_headers, mock_cycle_service):
    mock_cycle_service.get_logs_for_user.return_value = [
        {"start_date": "2026-05-01", "flow_intensity": "medium"}
    ]
    response = client.get("/api/v1/cycle/test-user-id-123/history", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()["entries"]) == 1
    mock_cycle_service.get_logs_for_user.assert_called_once_with("test-user-id-123", limit=10)

def test_get_cycle_history_unauthorized(auth_headers):
    response = client.get("/api/v1/cycle/other-user-id/history", headers=auth_headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized to view this user's data"

def test_get_cycle_history_empty_history(auth_headers, mock_cycle_service):
    mock_cycle_service.get_logs_for_user.return_value = []
    response = client.get("/api/v1/cycle/test-user-id-123/history", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()["entries"]) == 0
