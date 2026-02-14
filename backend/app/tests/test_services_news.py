"""Unit tests for news_service with mocked httpx."""

from unittest.mock import MagicMock, patch

import httpx

from app.services.news_service import fetch_market_news, get_news


def test_fetch_market_news_success_parses_response():
    mock_data = {"Data": [{"title": "Bitcoin Rises", "url": "https://example.com/btc", "published_on": 1609459200, "categories": "BTC|MARKET", "body": ""}]}
    with patch("app.services.news_service.httpx.Client") as MockClient:
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = mock_data
        mock_client_instance = MagicMock()
        mock_client_instance.get.return_value = mock_response
        MockClient.return_value.__enter__.return_value = mock_client_instance
        MockClient.return_value.__exit__.return_value = None
        items = fetch_market_news(["BTC"])
    assert len(items) == 1
    assert items[0]["title"] == "Bitcoin Rises"
    assert "BTC" in items[0]["coins"]


def test_fetch_market_news_http_error_falls_back():
    with patch("app.services.news_service.httpx.Client") as MockClient:
        mock_client_instance = MagicMock()
        MockClient.return_value.__enter__.return_value = mock_client_instance
        MockClient.return_value.__exit__.return_value = None
        mock_client_instance.get.side_effect = httpx.HTTPStatusError("429", request=MagicMock(), response=MagicMock())
        items = fetch_market_news([])
    assert isinstance(items, list)


def test_get_news_returns_list_and_none_message():
    with patch("app.services.news_service.fetch_market_news") as mock_fetch:
        mock_fetch.return_value = [{"title": "T", "url": "https://u", "published_at": "", "coins": []}]
        news, message = get_news(["BTC"])
    assert len(news) == 1
    assert news[0].title == "T"
    assert message is None
