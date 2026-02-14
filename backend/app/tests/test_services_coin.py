"""Unit tests for coin_service (cache refreshed from CoinGecko; get_prices reads cache)."""

from unittest.mock import MagicMock, patch

import httpx

from app.services.coin_service import (
    PRICES_UNAVAILABLE_MESSAGE,
    clear_prices_cache,
    get_prices,
    refresh_prices_cache,
)


def test_get_prices_empty_assets_returns_empty():
    """Empty user_assets returns ({}, None)."""
    prices, message = get_prices([])
    assert prices == {}
    assert message is None


def test_get_prices_invalid_symbols_filtered_out():
    """Invalid symbols are skipped; only requested valid symbols returned from cache."""
    with patch("app.services.coin_service.httpx.Client") as MockClient:
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"bitcoin": {"usd": 1.0}, "ethereum": {"usd": 2.0}}
        mock_client_instance = MagicMock()
        mock_client_instance.get.return_value = mock_response
        MockClient.return_value.__enter__.return_value = mock_client_instance
        MockClient.return_value.__exit__.return_value = None
        refresh_prices_cache()
    prices, message = get_prices(["BTC", "INVALID", "ETH"])
    assert message is None
    assert prices.get("BTC") == 1.0
    assert prices.get("ETH") == 2.0
    assert "INVALID" not in prices


def test_get_prices_success_returns_mapping():
    """After cache refresh, get_prices returns subset from cache."""
    with patch("app.services.coin_service.httpx.Client") as MockClient:
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "bitcoin": {"usd": 95000.5},
            "ethereum": {"usd": 3500.25},
        }
        mock_client_instance = MagicMock()
        mock_client_instance.get.return_value = mock_response
        MockClient.return_value.__enter__.return_value = mock_client_instance
        MockClient.return_value.__exit__.return_value = None
        refresh_prices_cache()
    prices, message = get_prices(["BTC", "ETH"])
    assert message is None
    assert prices["BTC"] == 95000.5
    assert prices["ETH"] == 3500.25


def test_get_prices_http_error_returns_empty_and_message():
    """When cache is empty and user wants assets, returns ({}, message)."""
    clear_prices_cache()
    with patch("app.services.coin_service.httpx.Client") as MockClient:
        mock_client_instance = MagicMock()
        MockClient.return_value.__enter__.return_value = mock_client_instance
        MockClient.return_value.__exit__.return_value = None
        mock_client_instance.get.side_effect = httpx.HTTPStatusError(
            "429", request=MagicMock(), response=MagicMock()
        )
        refresh_prices_cache()
    prices, message = get_prices(["BTC"])
    assert prices == {}
    assert message == PRICES_UNAVAILABLE_MESSAGE


def test_get_prices_timeout_returns_empty_and_message():
    """When cache is empty (refresh failed), returns ({}, message)."""
    clear_prices_cache()
    with patch("app.services.coin_service.httpx.Client") as MockClient:
        mock_client_instance = MagicMock()
        MockClient.return_value.__enter__.return_value = mock_client_instance
        MockClient.return_value.__exit__.return_value = None
        mock_client_instance.get.side_effect = httpx.TimeoutException("timeout")
        refresh_prices_cache()
    prices, message = get_prices(["BTC"])
    assert prices == {}
    assert message == PRICES_UNAVAILABLE_MESSAGE
