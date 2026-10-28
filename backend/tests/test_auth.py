from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_chat_rejects_missing_token():
    response = client.post(
        "/api/chat",
        json={"message": "hi"},
    )
    assert response.status_code == 401


def test_chat_rejects_garbage_token():
    response = client.post(
        "/api/chat",
        json={"message": "hi"},
        headers={"Authorization": "Bearer not-a-real-token"},
    )
    assert response.status_code == 401