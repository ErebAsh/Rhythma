import os
import sys

# ─── Mock external dependencies BEFORE importing main ──────────────────────
class MockGemini:
    """Mock the google.generativeai module so tests don't need it installed."""
    def __getattr__(self, name):
        return self

    def configure(self, *args, **kwargs):
        pass

    def GenerativeModel(self, *args, **kwargs):
        class MockModel:
            def generate_content(self, *args, **kwargs):
                class MockResponse:
                    text = "Mock Gemini response"
                return MockResponse()
        return MockModel()

sys.modules["google"] = MockGemini()
sys.modules["google.generativeai"] = MockGemini()

# ─── Set test environment variables BEFORE importing main ──────────────────
os.environ["JWT_SECRET"] = "test-secret-do-not-use-in-production"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["GEMINI_API_KEY"] = "mock-key"

# Now import main (all external deps are mocked)
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_login_success():
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "testuser", "password": "password123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_failure():
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "testuser", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert "detail" in response.json()


def test_protected_endpoint_without_token():
    response = client.post(
        "/api/v1/sms/send-summary",
        json={"phone_number": "+1234567890", "message": "Test"}
    )
    assert response.status_code == 401


def test_sms_rate_limiting():
    token_response = client.post(
        "/api/v1/auth/token",
        data={"username": "testuser", "password": "password123"}
    )
    assert token_response.status_code == 200
    token = token_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response1 = client.post(
        "/api/v1/sms/send-summary",
        json={"phone_number": "+1234567890", "message": "Test"},
        headers=headers
    )
    assert response1.status_code in [200, 501, 500]

    response2 = client.post(
        "/api/v1/sms/send-summary",
        json={"phone_number": "+1234567890", "message": "Test"},
        headers=headers
    )
    assert response2.status_code == 429