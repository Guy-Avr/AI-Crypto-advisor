"""API tests for dashboard endpoint."""

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient


def test_dashboard_requires_auth(client: TestClient):
    res = client.get("/dashboard")
    assert res.status_code == 401


def test_dashboard_without_onboarding_returns_404(client: TestClient, auth_headers):
    c, headers = auth_headers
    res = c.get("/dashboard", headers=headers)
    assert res.status_code == 404


def test_dashboard_with_onboarding_returns_200(client: TestClient, auth_headers):
    c, headers = auth_headers
    c.post(
        "/onboarding",
        headers=headers,
        json={"assets": ["BTC"], "investor_type": "HODLer", "content_types": ["news", "price", "ai", "meme"]},
    )
    with patch("app.services.coin_service.httpx.Client") as MockClient:
        mock_r = MagicMock()
        mock_r.raise_for_status = MagicMock()
        mock_r.json.return_value = {"bitcoin": {"usd": 50000.0}}
        MockClient.return_value.__enter__.return_value.get.return_value = mock_r
        MockClient.return_value.__exit__.return_value = None
        with patch("app.services.news_service.fetch_market_news", return_value=[]):
            res = c.get("/dashboard", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "prices" in data and "news" in data and "ai_insight" in data and "meme" in data
