"""
Market news via CryptoCompare News API (free, no key). Fallback to static_news.json on failure.
Only headline, link, timestamp, and coins are used; source attributed to CryptoCompare.
"""

import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

from app.core.config import get_settings
from app.models.enums import AssetSymbol
from app.schemas.dashboard import NewsItem

logger = logging.getLogger(__name__)

# Default fallback path when STATIC_NEWS_PATH not set
_DEFAULT_STATIC_NEWS_PATH = Path(__file__).resolve().parent.parent.parent / "static_news.json"
NEWS_UNAVAILABLE_MESSAGE = (
    "News is temporarily unavailable. Please try again later."
)
# Source attribution for legal/professional use
NEWS_SOURCE_ATTRIBUTION = "CryptoCompare"

# All known coin symbols for extraction from title/body/categories (word-boundary match)
_KNOWN_SYMBOLS = [s.value for s in AssetSymbol]
_KNOWN_SYMBOLS_SET = set(_KNOWN_SYMBOLS)


def _extract_coins_from_text(text: str) -> list[str]:
    """Find coin symbols mentioned in text (e.g. BTC, ETH) using word boundaries."""
    if not text:
        return []
    text_upper = text.upper()
    found: list[str] = []
    for symbol in sorted(_KNOWN_SYMBOLS, key=len, reverse=True):
        if re.search(r"\b" + re.escape(symbol) + r"\b", text_upper):
            found.append(symbol)
    return list(dict.fromkeys(found))


def _published_on_to_iso(published_on: int | None) -> str:
    """Convert CryptoCompare Unix timestamp to ISO 8601 string for published_at."""
    if published_on is None:
        return ""
    try:
        return datetime.fromtimestamp(int(published_on), tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except (ValueError, OSError):
        return ""


def _parse_cryptocompare_response(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Parse CryptoCompare API response into list of { title, url, published_at, coins }."""
    items: list[dict[str, Any]] = []
    raw_list = data.get("Data") if isinstance(data, dict) else None
    if not isinstance(raw_list, list):
        return items

    for r in raw_list:
        if not isinstance(r, dict):
            continue
        # Use only headline, link, timestamp – no full article body in output
        title = (r.get("title") or "").strip()
        url = (r.get("url") or r.get("guid") or "").strip()
        published_on = r.get("published_on")
        published_at = _published_on_to_iso(published_on)

        if not title or not url:
            continue

        # Build coins: from categories (e.g. "BTC|MARKET|SOL") and from title/body for coverage
        coins_set: set[str] = set()
        categories = r.get("categories") or ""
        if isinstance(categories, str):
            for part in categories.split("|"):
                sym = part.strip().upper()
                if sym in _KNOWN_SYMBOLS_SET:
                    coins_set.add(sym)
        for sym in _extract_coins_from_text(title):
            coins_set.add(sym)
        body = (r.get("body") or "")[:2000]  # limit scan length
        for sym in _extract_coins_from_text(body):
            coins_set.add(sym)
        coins = sorted(coins_set)  # stable order for JSON

        items.append({
            "title": title,
            "url": url,
            "published_at": published_at,
            "coins": coins,
        })
    return items


def _get_static_news_path() -> Path:
    """Path to static_news.json: from env STATIC_NEWS_PATH or default next to backend."""
    settings = get_settings()
    if (settings.STATIC_NEWS_PATH or "").strip():
        return Path(settings.STATIC_NEWS_PATH.strip())
    return _DEFAULT_STATIC_NEWS_PATH


def _load_static_news() -> list[dict[str, Any]]:
    """Load fallback news from static_news.json. Return empty list on error."""
    path = _get_static_news_path()
    if not path.is_file():
        logger.warning("Static news file not found: %s", path)
        return []
    try:
        raw = path.read_text(encoding="utf-8")
        data = json.loads(raw)
    except (OSError, json.JSONDecodeError) as e:
        logger.warning("Failed to load static_news.json: %s", e)
        return []
    if not isinstance(data, list):
        return []
    items: list[dict[str, Any]] = []
    for entry in data:
        if not isinstance(entry, dict):
            continue
        title = entry.get("title") or ""
        url = entry.get("url") or ""
        published_at = entry.get("published_at") or ""
        coins = entry.get("coins")
        if not isinstance(coins, list):
            coins = []
        coins = [str(c).strip().upper() for c in coins if c]
        if title and url:
            items.append({"title": title, "url": url, "published_at": published_at, "coins": coins})
    return items


def fetch_market_news(user_coins: list[str]) -> list[dict[str, Any]]:
    """
    Fetch latest market news from CryptoCompare News API; filter by user coins; limit 10.
    Returns list of dicts with keys: title, url, published_at, coins (list of symbols).
    On API failure (network, rate limit, parse error), falls back to static_news.json.
    Output is JSON-ready for FastAPI/frontend. Source: CryptoCompare (headline/link/timestamp/coins only).
    """
    # Step 1: Normalize user coins for filtering (uppercase, non-empty)
    user_set = {str(c).strip().upper() for c in (user_coins or []) if c}

    # Step 2: Request latest news from CryptoCompare (no API key needed)
    settings = get_settings()
    news_url = settings.CRYPTOCOMPARE_NEWS_URL or "https://min-api.cryptocompare.com/data/v2/news/"
    news_timeout = max(5.0, float(settings.NEWS_TIMEOUT or 10))
    news_limit = max(1, int(settings.NEWS_LIMIT or 10))
    raw_items: list[dict[str, Any]] = []
    try:
        with httpx.Client(timeout=news_timeout) as client:
            response = client.get(news_url)
            response.raise_for_status()
            data = response.json()
        raw_items = _parse_cryptocompare_response(data)
    except (httpx.HTTPError, httpx.TimeoutException, OSError, json.JSONDecodeError) as e:
        logger.warning("CryptoCompare API failed, using static fallback: %s", e)
        raw_items = []

    # Step 3: If API returned no items, use local static_news.json
    if not raw_items:
        raw_items = _load_static_news()

    # Step 4: Filter to articles related to at least one of the user's coins (or all if no filter)
    if user_set:
        filtered = [i for i in raw_items if set(i.get("coins") or []) & user_set]
    else:
        filtered = raw_items

    # Step 5: Limit to latest news_limit items
    return filtered[:news_limit]


def get_news(assets: list[str] | None = None) -> tuple[list[NewsItem], str | None]:
    """
    Fetch recent crypto market news (CryptoCompare + static fallback).
    Returns (news_list, None) on success, or ([], message) when both API and fallback fail.
    """
    try:
        items = fetch_market_news(assets or [])
    except Exception as e:
        logger.exception("fetch_market_news failed: %s", e)
        return [], NEWS_UNAVAILABLE_MESSAGE

    # Map to dashboard schema and attribute source
    news: list[NewsItem] = []
    for it in items:
        # Include coin symbols so frontend can show "News for: BTC, ETH"
        coins = it.get("coins")
        if not isinstance(coins, list):
            coins = []
        news.append(
            NewsItem(
                title=it.get("title") or "",
                url=it.get("url") or "",
                source=NEWS_SOURCE_ATTRIBUTION,
                published_at=it.get("published_at") or "",
                coins=coins,
            )
        )
    return news, None


# Example usage (optional):
#   from app.services.news_service import fetch_market_news
#   items = fetch_market_news(["BTC", "ETH"])
#   # items is a list of dicts: [{"title": "...", "url": "...", "published_at": "...", "coins": ["BTC", ...]}, ...]
