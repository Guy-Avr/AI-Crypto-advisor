"""Unit tests for coin_service with mocked httpx."""

from unittest.mock import MagicMock, patch

import httpx
import pytest

from app.services.coin_service import PRICES_UNAVAILABLE_MESSAGE, get_prices


def test_get_prices_empty_assets_returns_empty():
    """Empty user_assets returns ({}, None)."""
    prices, message = get_prices([])
    assert prices == {}
    assert message is None


def test_get_prices_invalid_symbols_filtered_out():
    """Invalid symbols are skipped; only valid enum symbols are requested."""
    with patch("app.services.coin_service.httpx.Client") as MockClient:
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"bitcoin": {"usd": 1.0}, "ethereum": {"usd": 1.0}}
        mock_client_instance = MagicMock()
        mock_client_instance.get.return_value = mock_response
        MockClient.return_value.__enter__.return_value = mock_client_instance
        MockClient.return_value.__exit__.return_value = None

        prices, message = get_prices(["BTC", "INVALID", "ETH"])
        assert message is None
        mock_client_instance.get.assert_called_once()
        call_kwargs = mock_client_instance.get.call_args.kwargs
        params = call_kwargs.get("params", {})
        ids = params.get("ids", "")
        assert "bitcoin" in ids
        assert "ethereum" in ids


def test_get_prices_success_returns_mapping():
    """Successful CoinGecko response returns prices dict and None message."""
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

        prices, message = get_prices(["BTC", "ETH"])
        assert message is None
        assert prices["BTC"] == 95000.5
        assert prices["ETH"] == 3500.25


def test_get_prices_http_error_returns_empty_and_message():
    """On HTTP error (e.g. 429) returns ({}, message)."""
    with patch("app.services.coin_service.httpx.Client") as MockClient:
        mock_client_instance = MagicMock()
        MockClient.return_value.__enter__.return_value = mock_client_instance
        MockClient.return_value.__exit__.return_value = None
        mock_client_instance.get.side_effect = httpx.HTTPStatusError(
            "429", request=MagicMock(), response=MagicMock()
        )

        prices, message = get_prices(["BTC"])
        assert prices == {}
        assert message == PRICES_UNAVAILABLE_MESSAGE


def test_get_prices_timeout_returns_empty_and_message():
    """On timeout returns ({}, message)."""
    with patch("app.services.coin_service.httpx.Client") as MockClient:
        mock_client_instance = MagicMock()
        MockClient.return_value.__enter__.return_value = mock_client_instance
        MockClient.return_value.__exit__.return_value = None
        mock_client_instance.get.side_effect = httpx.TimeoutException("timeout")

        prices, message = get_prices(["BTC"])
        assert prices == {}
        assert message == PRICES_UNAVAILABLE_MESSAGE
