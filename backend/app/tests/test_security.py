"""Unit tests for security (hash, verify, JWT)."""

from unittest.mock import patch

import pytest

from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_hash_password_returns_non_empty_string():
    h = hash_password("mypassword")
    assert isinstance(h, str)
    assert len(h) > 0
    assert h != "mypassword"


def test_verify_password_match():
    h = hash_password("secret")
    assert verify_password("secret", h) is True


def test_verify_password_no_match():
    h = hash_password("secret")
    assert verify_password("wrong", h) is False


def test_create_and_decode_access_token():
    from app.core.config import get_settings
    get_settings.cache_clear()
    try:
        with patch("app.core.security.get_settings") as mock_settings:
            mock_settings.return_value.SECRET_KEY = "test-secret-key-for-tests"
            mock_settings.return_value.ALGORITHM = "HS256"
            mock_settings.return_value.ACCESS_TOKEN_EXPIRE_MINUTES = 60
            token = create_access_token({"sub": "user-id-123"})
            assert isinstance(token, str)
            payload = decode_access_token(token)
            assert payload is not None
            assert payload.get("sub") == "user-id-123"
            assert "exp" in payload
    finally:
        get_settings.cache_clear()


def test_decode_access_token_invalid_returns_none():
    assert decode_access_token("invalid.jwt.here") is None
