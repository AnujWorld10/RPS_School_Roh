def test_login_invalid_credentials(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "missing@school.local", "password": "WrongPassword@123"},
    )
    assert response.status_code == 401
    assert response.json()["success"] is False


def test_me_requires_token(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
