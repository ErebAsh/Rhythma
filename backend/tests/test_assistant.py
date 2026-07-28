import os
import sys
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

os.environ["JWT_SECRET"] = "test-secret"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["GEMINI_API_KEY"] = "mock-key"

sys.modules["firebase_admin"] = MagicMock(_apps={})
sys.modules["firebase_admin.auth"] = MagicMock()
sys.modules["firebase_admin.credentials"] = MagicMock()
sys.modules["firebase_admin.firestore"] = MagicMock()

from main import app
from core.auth import get_current_user

client = TestClient(app)

TEST_USER_ID = "test-user-id"

def override_get_current_user():
    return {"id": TEST_USER_ID, "username": "testuser"}

@pytest.fixture(autouse=True)
def override_dependencies():
    app.dependency_overrides[get_current_user] = override_get_current_user
    yield
    app.dependency_overrides.clear()

from api.assistant import _session_store

@pytest.fixture(autouse=True)
def clear_session():
    _session_store.clear()
    yield
    _session_store.clear()


def test_chat_success():
    payload = {"message": "What is a normal cycle length?"}
    response = client.post("/api/v1/assistant/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert data["language"] == "en"
    assert "disclaimer" in data


def test_chat_with_language():
    payload = {"message": "How are you?", "language": "hi"}
    response = client.post("/api/v1/assistant/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["language"] == "hi"
    assert "response" in data


def test_chat_empty_message():
    payload = {"message": "   "}
    response = client.post("/api/v1/assistant/chat", json=payload)
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_chat_unauthorized():
    app.dependency_overrides.clear()
    payload = {"message": "Hello"}
    response = client.post("/api/v1/assistant/chat", json=payload)
    assert response.status_code == 401


def test_languages_success():
    response = client.get("/api/v1/assistant/languages")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    codes = [lang["code"] for lang in data]
    assert "en" in codes
    assert "hi" in codes
    assert "mr" in codes


def test_languages_unauthorized():
    app.dependency_overrides.clear()
    response = client.get("/api/v1/assistant/languages")
    assert response.status_code == 401


def test_chat_with_history():
    payload = {
        "message": "Tell me more",
        "history": [
            {"role": "user", "content": "What is PCOS?"},
            {"role": "model", "content": "PCOS is a hormonal disorder."},
        ]
    }
    response = client.post("/api/v1/assistant/chat", json=payload)
    assert response.status_code == 200
    assert "response" in response.json()
