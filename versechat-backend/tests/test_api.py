from fastapi.testclient import TestClient

from src.versechat_backend.app import app

client = TestClient(app)


def test_get_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"message": "healthy"}
