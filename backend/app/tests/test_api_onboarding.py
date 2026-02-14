"""API tests for onboarding endpoint."""

from fastapi.testclient import TestClient


def test_onboarding_requires_auth(client: TestClient):
    res = client.post(
        "/onboarding",
        json={"assets": ["BTC", "ETH"], "investor_type": "HODLer", "content_types": ["news", "price"]},
    )
    assert res.status_code == 401


def test_onboarding_success(client: TestClient, auth_headers):
    c, headers = auth_headers
    res = c.post(
        "/onboarding",
        headers=headers,
        json={"assets": ["BTC", "ETH"], "investor_type": "HODLer", "content_types": ["news", "price", "ai"]},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["investor_type"] == "HODLer"
    assert "BTC" in data["assets"]


def test_onboarding_twice_returns_409(client: TestClient, auth_headers):
    c, headers = auth_headers
    body = {"assets": ["BTC"], "investor_type": "DayTrader", "content_types": ["news"]}
    c.post("/onboarding", headers=headers, json=body)
    res = c.post("/onboarding", headers=headers, json=body)
    assert res.status_code == 409
