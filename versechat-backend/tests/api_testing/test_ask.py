from unittest.mock import AsyncMock

from versechat_backend.models.chat import ChatResponse


def test_ask_success(client):

    response = client.post("/ask", json={"query": "Who led israel out of egypt?"})

    assert response.status_code == 200
    body = ChatResponse.model_validate(response.json())
    assert body.role == "assistant"
    assert body.content
    assert isinstance(body.content, str)
    assert isinstance(body.sources, list)


def test_ask_returns_500_when_agent_fails(client, monkeypatch):
    failing_ask = AsyncMock(side_effect=RuntimeError("Agent service unavailable"))

    monkeypatch.setattr(client.app.state.agent, "ask", failing_ask)

    response = client.post(
        "/ask",
        json={"query": "Who led Israel out of Egypt?"},
    )

    assert response.status_code == 500
    assert response.json() == {"detail": "internal error occured"}

    failing_ask.assert_awaited_once_with("Who led Israel out of Egypt?")


def test_ask_rejects_missing_query(client):
    response = client.post("/ask", json={})

    assert response.status_code == 422


def test_ask_rejects_empty_query(client):
    response = client.post("/ask", json={"query": ""})

    assert response.status_code == 422


def test_ask_rejects_query_over_max_length(client):
    response = client.post("/ask", json={"query": "a" * 2001})

    assert response.status_code == 422
