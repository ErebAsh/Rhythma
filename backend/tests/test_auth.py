import os
import sys
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

# Ensure backend directory is on the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ─── Mock google.generativeai ──────────────────────────────────────────────
class MockGemini:
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

sys.modules["google.generativeai"] = MockGemini()

# ─── Set environment variables ─────────────────────────────────────────────
os.environ["JWT_SECRET"] = "test-secret"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["GEMINI_API_KEY"] = "mock-key"

# ─── Mock firebase_admin ──────────────────────────────────────────────────
mock_firebase_admin = MagicMock()
mock_firebase_auth = MagicMock()
sys.modules["firebase_admin"] = mock_firebase_admin
sys.modules["firebase_admin.auth"] = mock_firebase_auth
sys.modules["firebase_admin.credentials"] = MagicMock()
sys.modules["firebase_admin.firestore"] = MagicMock()

# ─── Import main after mocks ──────────────────────────────────────────────
from main import app
import firebase_admin.auth
client = TestClient(app)

# ─── Fixture to mock UserService ──────────────────────
@pytest.fixture(autouse=True)
def mock_auth_dependencies():
    import core.auth_router as auth_router_module
    auth_router_module.login_attempts.clear()

    with patch("core.auth_router.UserService") as MockUserService1, \
         patch("core.auth.UserService") as MockUserService2, \
         patch("api.sms.UserService") as MockUserService3:

        test_user_data = {
            "id": "test-user-id-123",
            "phone": "+1234567890",
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-01T00:00:00Z"
        }

        def get_by_phone(phone):
            if phone == "+1234567890":
                return test_user_data.copy()
            return None

        def get_by_id(user_id):
            if user_id == "test-user-id-123":
                return test_user_data
            return None

        def create_user(user_dict):
            return "test-user-id-123"

        def update_user(user_id, update_data):
            if user_id == "test-user-id-123":
                test_user_data.update(update_data)
                return True
            return False

        for mock_us in [MockUserService1, MockUserService2, MockUserService3]:
            mock_us.get_user_by_phone.side_effect = get_by_phone
            mock_us.get_user_by_id.side_effect = get_by_id
            mock_us.create_user.side_effect = create_user
            mock_us.update_user.side_effect = update_user

        yield

# ─── Tests ──────────────────────────────────────────────────────────────────

def test_firebase_login_success():
    # Mock verify_id_token to return a valid payload
    firebase_admin.auth.verify_id_token.return_value = {"phone_number": "+1234567890", "uid": "firebase_uid"}
    
    response = client.post(
        "/api/v1/auth/firebase-login",
        json={"id_token": "valid_token"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_firebase_login_invalid_token():
    class InvalidIdTokenError(Exception):
        pass
    firebase_admin.auth.InvalidIdTokenError = InvalidIdTokenError
    firebase_admin.auth.verify_id_token.side_effect = InvalidIdTokenError("Invalid token")
    
    response = client.post(
        "/api/v1/auth/firebase-login",
        json={"id_token": "invalid_token"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid Firebase ID token"
    # reset side effect
    firebase_admin.auth.verify_id_token.side_effect = None

def test_protected_endpoint_without_token():
    response = client.post(
        "/api/v1/sms/send-summary",
        json={"phone_number": "+1234567890", "message": "Test"}
    )
    assert response.status_code == 401

def test_get_profile():
    firebase_admin.auth.verify_id_token.return_value = {"phone_number": "+1234567890", "uid": "firebase_uid"}
    token_response = client.post(
        "/api/v1/auth/firebase-login",
        json={"id_token": "valid_token"}
    )
    assert token_response.status_code == 200
    token = token_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/auth/profile", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["phone"] == "+1234567890"

def test_patch_profile():
    firebase_admin.auth.verify_id_token.return_value = {"phone_number": "+1234567890", "uid": "firebase_uid"}
    token_response = client.post(
        "/api/v1/auth/firebase-login",
        json={"id_token": "valid_token"}
    )
    token = token_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    update_payload = {
        "age": 25,
        "cycle_length": 29,
        "avatar": "assets/avatars/avatar_2.png"
    }
    response = client.patch("/api/v1/auth/profile", json=update_payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["age"] == 25
    assert data["cycle_length"] == 29
    assert data["avatar"] == "assets/avatars/avatar_2.png"