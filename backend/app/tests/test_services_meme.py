"""Unit tests for meme_service (load from JSON, category selection)."""

from pathlib import Path
from unittest.mock import patch

import pytest

from app.services.meme_service import get_meme


def test_get_meme_no_file_returns_none():
    """When memes file is missing or invalid, returns None."""
    with patch("app.services.meme_service._load_memes_by_category", return_value={}):
        assert get_meme("HODLer") is None


def test_get_meme_unknown_category_falls_back_to_general():
    """Unknown investor_type uses 'general' category."""
    categories = {
        "general": [
            {"title": "To the moon", "url": "https://x.com", "image_url": "https://i.imgflip.com/1.png"},
        ]
    }
    with patch("app.services.meme_service._load_memes_by_category", return_value=categories):
        meme = get_meme("UnknownType")
        assert meme is not None
        assert meme.title == "To the moon"
        assert meme.url == "https://x.com"
        assert meme.image_url == "https://i.imgflip.com/1.png"


def test_get_meme_known_category_returns_from_category():
    """Known investor_type returns meme from that category."""
    categories = {
        "HODLer": [
            {"title": "HODL", "url": "https://x.com", "image_url": "https://i.imgflip.com/2.jpg"},
        ],
        "general": [
            {"title": "General", "url": "https://y.com", "image_url": "https://i.imgflip.com/3.jpg"},
        ],
    }
    with patch("app.services.meme_service._load_memes_by_category", return_value=categories):
        meme = get_meme("HODLer")
        assert meme is not None
        assert meme.title == "HODL"
