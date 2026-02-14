"""API tests for auth endpoints."""

import uuid


def test_signup_success(client):
    email = "signup-" + uuid.uuid4().hex + "@example.com"
    res = client.post("/auth/signup", json={"email": email, "name": "User", "password": "pass123"})
    assert res.status_code == 200
    assert res.json()["email"] == email
    assert "id" in res.json()


def test_signup_duplicate_email_returns_409(client):
    email = "dup-" + uuid.uuid4().hex + "@example.com"
    client.post("/auth/signup", json={"email": email, "name": "A", "password": "pass123"})
    res = client.post("/auth/signup", json={"email": email, "name": "B", "password": "other"})
    assert res.status_code == 409


def test_login_success(client):
    email = "login-" + uuid.uuid4().hex + "@example.com"
    client.post("/auth/signup", json={"email": email, "name": "U", "password": "secret"})
    res = client.post("/auth/login", json={"email": email, "password": "secret"})
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_login_wrong_password_returns_401(client):
    email = "wrong-" + uuid.uuid4().hex + "@example.com"
    client.post("/auth/signup", json={"email": email, "name": "U", "password": "secret"})
    res = client.post("/auth/login", json={"email": email, "password": "wrong"})
    assert res.status_code == 401
