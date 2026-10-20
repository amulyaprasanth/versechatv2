import uuid
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient


def test_conversations_api(client: TestClient):
    unique_email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    raw_password = "SecurePassword123!"
    fullname = "Conversation Tester"

    # 1. Register & login
    reg_response = client.post(
        "/auth/register",
        json={
            "fullname": fullname,
            "email": unique_email,
            "password": raw_password,
        },
    )
    assert reg_response.status_code == 201

    login_response = client.post(
        "/auth/token",
        data={"username": unique_email, "password": raw_password},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get initial conversations (should be empty)
    res = client.get("/conversations", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "conversations" in data
    assert len(data["conversations"]) == 0

    # 3. Create a conversation
    create_res = client.post(
        "/conversations",
        headers=headers,
        json={"title": "Test Genesis Chat"},
    )
    assert create_res.status_code == 201
    created = create_res.json()
    conv_id = created["id"]
    assert created["title"] == "Test Genesis Chat"

    # 4. List conversations (should now have 1)
    list_res = client.get("/conversations", headers=headers)
    assert list_res.status_code == 200
    assert len(list_res.json()["conversations"]) == 1
    assert list_res.json()["conversations"][0]["id"] == conv_id

    # 5. Get conversation details
    detail_res = client.get(f"/conversations/{conv_id}", headers=headers)
    assert detail_res.status_code == 200
    detail_data = detail_res.json()
    assert detail_data["id"] == conv_id
    assert detail_data["title"] == "Test Genesis Chat"
    assert "messages" in detail_data

    # 6. Delete conversation
    del_res = client.delete(f"/conversations/{conv_id}", headers=headers)
    assert del_res.status_code == 204

    # 7. Verify deletion
    list_after_del = client.get("/conversations", headers=headers)
    assert list_after_del.status_code == 200
    assert len(list_after_del.json()["conversations"]) == 0


def create_authenticated_conversation(client: TestClient):
    email = f"user_{uuid.uuid4().hex}@example.com"
    password = "SecurePassword123!"
    client.post(
        "/auth/register",
        json={"fullname": "Conversation Tester", "email": email, "password": password},
    )
    login = client.post("/auth/token", data={"username": email, "password": password})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    conversation = client.post("/conversations", headers=headers, json={})
    return headers, conversation.json()["id"]


def test_history_error_is_not_returned_as_empty_messages(
    client: TestClient, monkeypatch
):
    headers, conv_id = create_authenticated_conversation(client)
    failing_get_state = AsyncMock(side_effect=RuntimeError("checkpointer unavailable"))
    monkeypatch.setattr(client.app.state.agent, "aget_state", failing_get_state)

    response = client.get(f"/conversations/{conv_id}", headers=headers)

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Conversation history is temporarily unavailable"
    }


def test_failed_checkpoint_delete_preserves_conversation(
    client: TestClient, monkeypatch
):
    headers, conv_id = create_authenticated_conversation(client)
    failing_delete = AsyncMock(side_effect=RuntimeError("checkpointer unavailable"))
    monkeypatch.setattr(client.app.state.checkpointer, "adelete_thread", failing_delete)

    response = client.delete(f"/conversations/{conv_id}", headers=headers)

    assert response.status_code == 503
    remaining = client.get("/conversations", headers=headers)
    assert remaining.status_code == 200
    assert [item["id"] for item in remaining.json()["conversations"]] == [conv_id]
