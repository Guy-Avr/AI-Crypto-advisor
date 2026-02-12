"""Test that GET /users/me is protected: 401 without token, 200 with valid token."""

import uuid

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_users_me_without_token_returns_401():
    """GET /users/me without Authorization header returns 401."""
    response = client.get("/users/me")
    assert response.status_code == 401


def test_users_me_with_invalid_token_returns_401():
    """GET /users/me with invalid Bearer token returns 401."""
    response = client.get(
        "/users/me",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert response.status_code == 401


def test_users_me_with_valid_token_returns_200():
    """Signup -> login -> GET /users/me with token returns 200 and user data."""
    email = f"test-{uuid.uuid4().hex}@example.com"
    password = "testpass123"
    name = "Test User"

    signup_res = client.post(
        "/auth/signup",
        json={"email": email, "name": name, "password": password},
    )
    assert signup_res.status_code == 200
    signup_data = signup_res.json()
    assert signup_data["email"] == email
    assert signup_data["name"] == name
    assert "id" in signup_data

    login_res = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]

    me_res = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["id"] == signup_data["id"]
    assert me_data["email"] == email
    assert me_data["name"] == name
    assert "onboarding_done" in me_data
    assert me_data["onboarding_done"] is False
