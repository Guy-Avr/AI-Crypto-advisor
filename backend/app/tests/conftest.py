"""Pytest fixtures for API and service tests."""

import uuid

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    """FastAPI TestClient using the main app."""
    return TestClient(app)


@pytest.fixture
def auth_headers(client: TestClient) -> tuple[TestClient, dict]:
    """
    Create a test user via signup + login and return (client, headers dict with Bearer token).
    Use when a test needs an authenticated user (e.g. onboarding, dashboard, vote).
    """
    email = f"test-{uuid.uuid4().hex}@example.com"
    password = "testpass123"
    name = "Test User"
    res = client.post(
        "/auth/signup",
        json={"email": email, "name": name, "password": password},
    )
    assert res.status_code == 200
    res = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert res.status_code == 200
    token = res.json()["access_token"]
    return client, {"Authorization": f"Bearer {token}"}
