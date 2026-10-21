import uuid
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient


def authenticated_user(client: TestClient) -> tuple[dict[str, str], str]:
    email = f"user_{uuid.uuid4().hex}@example.com"
    password = "SecurePassword123!"
    client.post(
        "/auth/register",
        json={"fullname": "Ask Tester", "email": email, "password": password},
    )
    login = client.post("/auth/token", data={"username": email, "password": password})
    assert login.status_code == 200
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    conversation = client.post(
        "/conversations", headers=headers, json={"title": "Ask test conversation"}
    )
    assert conversation.status_code == 201
    return headers, conversation.json()["id"]


def test_ask_success(client: TestClient):
    headers, conv_id = authenticated_user(client)

    response = client.post(
        "/ask",
        headers=headers,
        json={"query": "Who led Israel out of Egypt?", "conv_id": conv_id},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["role"] == "assistant"
    assert body["content"] == "Test answer"
    uuid.UUID(body["id"])


def test_ask_returns_500_when_agent_fails(client: TestClient, monkeypatch):
    headers, conv_id = authenticated_user(client)
    failing_ainvoke = AsyncMock(side_effect=RuntimeError("Agent service unavailable"))
    monkeypatch.setattr(client.app.state.agent, "ainvoke", failing_ainvoke)

    response = client.post(
        "/ask",
        headers=headers,
        json={"query": "Who led Israel out of Egypt?", "conv_id": conv_id},
    )

    assert response.status_code == 500
    assert response.json() == {"detail": "internal error occured"}
    failing_ainvoke.assert_awaited_once()


def test_ask_requires_authentication(client: TestClient):
    response = client.post(
        "/ask",
        json={"query": "Who led Israel out of Egypt?", "conv_id": str(uuid.uuid4())},
    )

    assert response.status_code == 401


def test_ask_rejects_missing_query(client: TestClient):
    headers, conv_id = authenticated_user(client)
    response = client.post("/ask", headers=headers, json={"conv_id": conv_id})
    assert response.status_code == 422


def test_ask_rejects_empty_query(client: TestClient):
    headers, conv_id = authenticated_user(client)
    response = client.post(
        "/ask", headers=headers, json={"query": "", "conv_id": conv_id}
    )
    assert response.status_code == 422


def test_ask_rejects_query_over_max_length(client: TestClient):
    headers, conv_id = authenticated_user(client)
    response = client.post(
        "/ask", headers=headers, json={"query": "a" * 2001, "conv_id": conv_id}
    )
    assert response.status_code == 422
