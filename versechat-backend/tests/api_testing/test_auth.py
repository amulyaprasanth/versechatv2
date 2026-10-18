import uuid
import pytest
from fastapi.testclient import TestClient
from versechat_backend.app import app


def test_auth_flow_end_to_end(client: TestClient):
    unique_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    raw_password = "SecurePassword123!"
    fullname = "Test User"

    # 1. Register a new user
    reg_response = client.post(
        "/auth/register",
        json={
            "fullname": fullname,
            "email": unique_email,
            "password": raw_password,
        },
    )
    assert reg_response.status_code == 201, reg_response.text
    user_data = reg_response.json()
    assert user_data["email"] == unique_email.lower()
    assert user_data["fullname"] == fullname
    assert user_data["is_active"] is True
    assert "password" not in user_data
    assert "password_hash" not in user_data

    # 2. Reject duplicate registration with 409 Conflict
    dup_response = client.post(
        "/auth/register",
        json={
            "fullname": fullname,
            "email": unique_email,
            "password": raw_password,
        },
    )
    assert dup_response.status_code == 409
    assert "already exists" in dup_response.json()["detail"]

    # 3. Reject invalid email
    invalid_email_response = client.post(
        "/auth/register",
        json={
            "fullname": fullname,
            "email": "invalid-email-format",
            "password": raw_password,
        },
    )
    assert invalid_email_response.status_code == 422

    # 4. Reject short password (< 8 chars)
    short_pw_response = client.post(
        "/auth/register",
        json={
            "fullname": fullname,
            "email": f"short_{uuid.uuid4().hex[:8]}@example.com",
            "password": "short",
        },
    )
    assert short_pw_response.status_code == 422

    # 5. Login with correct credentials
    login_response = client.post(
        "/auth/token",
        data={"username": unique_email, "password": raw_password},
    )
    assert login_response.status_code == 200, login_response.text
    token_payload = login_response.json()
    assert "access_token" in token_payload
    assert token_payload["token_type"] == "bearer"
    token = token_payload["access_token"]

    # 6. Login with incorrect password
    bad_login_response = client.post(
        "/auth/token",
        data={"username": unique_email, "password": "WrongPassword123!"},
    )
    assert bad_login_response.status_code == 401

    # 7. Get current user profile with valid Bearer token
    me_response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_response.status_code == 200, me_response.text
    profile = me_response.json()
    assert profile["email"] == unique_email.lower()
    assert profile["fullname"] == fullname

    # 8. Access /auth/me with invalid token
    invalid_me_response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalid.token.value"},
    )
    assert invalid_me_response.status_code == 401
