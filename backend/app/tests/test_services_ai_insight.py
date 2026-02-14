"""Unit tests for ai_insight_service (no key = fallback; with mock = returns text)."""

from unittest.mock import MagicMock, patch

import pytest

from app.services.ai_insight_service import (
    FALLBACK_INSIGHT,
    build_prompt,
    get_ai_insight,
)


def test_build_prompt_includes_assets_and_investor_type():
    """build_prompt includes investor_type and content_types in context."""
    prompt = build_prompt(
        assets=["BTC", "ETH"],
        content_types=["news", "price"],
        investor_type="HODLer",
    )
    assert "HODLer" in prompt
    assert "BTC" in prompt or "ETH" in prompt
    assert "market news" in prompt or "prices" in prompt


def test_get_ai_insight_no_api_key_returns_fallback():
    """When OPENROUTER_API_KEY is missing, returns FALLBACK_INSIGHT."""
    with patch("app.services.ai_insight_service.get_settings") as mock_settings:
        mock_settings.return_value.OPENROUTER_API_KEY = ""
        result = get_ai_insight(assets=["BTC"])
        assert result == FALLBACK_INSIGHT


def test_get_ai_insight_with_mock_returns_text():
    """With API key and mocked 200 response, returns truncated insight text."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {"content": "Bitcoin remains volatile. Consider risk management."},
            }
        ]
    }
    with patch("app.services.ai_insight_service.get_settings") as mock_settings:
        mock_settings.return_value.OPENROUTER_API_KEY = "test-key"
        mock_settings.return_value.OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
        mock_settings.return_value.OPENROUTER_TIMEOUT = 30
        mock_settings.return_value.OPENROUTER_MAX_TOKENS = 220
        mock_settings.return_value.OPENROUTER_TEMPERATURE = 0.3
    with patch("app.services.ai_insight_service.httpx.Client") as MockClient:
        mock_client_instance = MagicMock()
        mock_client_instance.post.return_value = mock_response
        MockClient.return_value.__enter__.return_value = mock_client_instance
        MockClient.return_value.__exit__.return_value = None

        result = get_ai_insight(assets=["BTC"])
        assert "Bitcoin" in result or "volatile" in result
        assert result != FALLBACK_INSIGHT
