"""Integration tests for auth success paths and token handling."""

import pytest


def test_login_success_returns_tokens(client):
    """POST /login with valid credentials returns access_token and refresh_token."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "superadmin@school.com",
            "password": "SuperAdmin@123",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert "data" in body
    data = body["data"]
    assert "access_token" in data
    assert "refresh_token" in data
    assert data.get("token_type") == "Bearer" or "token_type" in data


def test_me_returns_profile_after_login(client):
    """GET /me with valid token returns current user profile with roles."""
    # Login first
    login_resp = client.post(
        "/api/v1/auth/login",
        json={
            "email": "superadmin@school.com",
            "password": "SuperAdmin@123",
        },
    )
    assert login_resp.status_code == 200
    access_token = login_resp.json()["data"]["access_token"]

    # Call /me with token
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    data = body["data"]
    assert data["email"] == "superadmin@school.com"
    assert "roles" in data
    assert "permissions" in data
    assert data["id"] is not None


def test_refresh_token_returns_new_access_token(client):
    """POST /refresh-token with valid refresh_token returns new access_token."""
    # Login first
    login_resp = client.post(
        "/api/v1/auth/login",
        json={
            "email": "superadmin@school.com",
            "password": "SuperAdmin@123",
        },
    )
    assert login_resp.status_code == 200
    refresh_token = login_resp.json()["data"]["refresh_token"]

    # Call refresh-token
    response = client.post(
        "/api/v1/auth/refresh-token",
        json={"refresh_token": refresh_token},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    data = body["data"]
    assert "access_token" in data
    assert data["access_token"] != login_resp.json()["data"]["access_token"]  # New token


def test_logout_invalidates_refresh_token(client):
    """POST /logout with refresh_token invalidates token for future use."""
    # Login first
    login_resp = client.post(
        "/api/v1/auth/login",
        json={
            "email": "superadmin@school.com",
            "password": "SuperAdmin@123",
        },
    )
    assert login_resp.status_code == 200
    access_token = login_resp.json()["data"]["access_token"]
    refresh_token = login_resp.json()["data"]["refresh_token"]

    # Call logout
    logout_resp = client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": refresh_token},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert logout_resp.status_code == 200

    # Try to use refresh_token again (should fail)
    retry_refresh = client.post(
        "/api/v1/auth/refresh-token",
        json={"refresh_token": refresh_token},
    )
    assert retry_refresh.status_code in [401, 400]  # Unauthorized or invalid


def test_verify_token_endpoint_validates_token(client):
    """GET /verify-token with valid token returns valid=true."""
    # Login first
    login_resp = client.post(
        "/api/v1/auth/login",
        json={
            "email": "superadmin@school.com",
            "password": "SuperAdmin@123",
        },
    )
    assert login_resp.status_code == 200
    access_token = login_resp.json()["data"]["access_token"]

    # Verify token
    response = client.get(
        "/api/v1/auth/verify-token",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    data = body["data"]
    assert data.get("valid") is True
    assert "user_id" in data


def test_verify_token_without_auth_fails(client):
    """GET /verify-token without auth header returns 401."""
    response = client.get("/api/v1/auth/verify-token")
    assert response.status_code == 401


def test_change_password_requires_old_password(client):
    """POST /change-password requires current password and valid new password."""
    # Login first
    login_resp = client.post(
        "/api/v1/auth/login",
        json={
            "email": "superadmin@school.com",
            "password": "SuperAdmin@123",
        },
    )
    assert login_resp.status_code == 200
    access_token = login_resp.json()["data"]["access_token"]

    # Change password with wrong old password
    response = client.post(
        "/api/v1/auth/change-password",
        json={
            "old_password": "WrongPassword@123",
            "new_password": "NewPassword@123",
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code in [400, 401, 422]  # Bad request or unprocessable


def test_login_with_invalid_email_fails(client):
    """POST /login with non-existent email returns 401."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "nonexistent@school.local",
            "password": "AnyPassword@123",
        },
    )
    assert response.status_code == 401
    body = response.json()
    assert body["success"] is False


def test_login_with_wrong_password_fails(client):
    """POST /login with wrong password returns 401."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "superadmin@school.com",
            "password": "WrongPassword@123",
        },
    )
    assert response.status_code == 401
    body = response.json()
    assert body["success"] is False


def test_me_without_token_returns_401(client):
    """GET /me without Authorization header returns 401."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_me_with_invalid_token_returns_401(client):
    """GET /me with malformed token returns 401."""
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid.token.here"},
    )
    assert response.status_code == 401
