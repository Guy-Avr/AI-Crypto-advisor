"""
CoinGecko API integration for crypto prices.
Uses an in-memory cache refreshed every 5 minutes with ALL enum coins from CoinGecko.
Per-request: filter cache by user_assets only (no direct API call per request).
"""

import logging
import threading
import time
from typing import Any

import httpx

from app.core.config import get_settings
from app.models.enums import AssetSymbol

logger = logging.getLogger(__name__)

CACHE_TTL_SEC = 300  # 5 minutes

# Message returned when the price provider is unavailable (no invented data).
PRICES_UNAVAILABLE_MESSAGE = (
    "Price data is temporarily unavailable. Please try again later."
)

# In-memory cache: symbol -> price (USD). Refreshed periodically for all enum coins.
_prices_cache: dict[str, float] = {}
_cache_lock = threading.Lock()

# CoinGecko coin id per supported asset (single source of truth: AssetSymbol enum)
ASSET_TO_COINGECKO_ID: dict[AssetSymbol, str] = {
    AssetSymbol.BTC: "bitcoin",
    AssetSymbol.ETH: "ethereum",
    AssetSymbol.BNB: "binancecoin",
    AssetSymbol.SOL: "solana",
    AssetSymbol.XRP: "ripple",
    AssetSymbol.USDT: "tether",
    AssetSymbol.USDC: "usd-coin",
    AssetSymbol.ADA: "cardano",
    AssetSymbol.DOGE: "dogecoin",
    AssetSymbol.AVAX: "avalanche-2",
    AssetSymbol.DOT: "polkadot",
    AssetSymbol.MATIC: "matic-network",
    AssetSymbol.LINK: "chainlink",
    AssetSymbol.UNI: "uniswap",
    AssetSymbol.ATOM: "cosmos",
    AssetSymbol.LTC: "litecoin",
    AssetSymbol.ETC: "ethereum-classic",
    AssetSymbol.XLM: "stellar",
    AssetSymbol.BCH: "bitcoin-cash",
    AssetSymbol.NEAR: "near",
    AssetSymbol.APT: "aptos",
    AssetSymbol.ARB: "arbitrum",
    AssetSymbol.OP: "optimism",
    AssetSymbol.INJ: "injective-protocol",
    AssetSymbol.SUI: "sui",
    AssetSymbol.SEI: "sei-network",
    AssetSymbol.TIA: "celestia",
    AssetSymbol.PEPE: "pepe",
    AssetSymbol.WIF: "dogwifcoin",
    AssetSymbol.FLOKI: "floki",
    AssetSymbol.BONK: "bonk",
}


def refresh_prices_cache() -> None:
    """
    Fetch USD prices for ALL AssetSymbol enum coins from CoinGecko and update in-memory cache.
    Called every 5 minutes by a background thread; one API call per refresh.
    """
    ids = list(ASSET_TO_COINGECKO_ID.values())
    symbol_by_id: dict[str, str] = {cg_id: sym.value for sym, cg_id in ASSET_TO_COINGECKO_ID.items()}
    settings = get_settings()
    url = settings.COINGECKO_API_URL or "https://api.coingecko.com/api/v3/simple/price"
    timeout = max(5.0, float(settings.COINGECKO_TIMEOUT or 10))
    params: dict[str, Any] = {
        "ids": ",".join(ids),
        "vs_currencies": "usd",
    }
    try:
        with httpx.Client(timeout=timeout) as client:
            response = client.get(url, params=params)
            response.raise_for_status()
        data = response.json()
    except (httpx.HTTPError, httpx.TimeoutException) as e:
        logger.warning("CoinGecko cache refresh failed: %s", e)
        return
    except Exception as e:
        logger.warning("CoinGecko cache refresh error: %s", e)
        return

    result: dict[str, float] = {}
    for cg_id, symbol in symbol_by_id.items():
        coin = data.get(cg_id)
        if isinstance(coin, dict) and "usd" in coin:
            try:
                result[symbol] = float(coin["usd"])
            except (TypeError, ValueError):
                pass
    with _cache_lock:
        _prices_cache.clear()
        _prices_cache.update(result)
    logger.info("Prices cache refreshed: %s symbols", len(result))


def get_prices(user_assets: list[str]) -> tuple[dict[str, float], str | None]:
    """
    Return USD prices for the given asset symbols from the in-memory cache.
    No direct CoinGecko call; cache is refreshed every 5 minutes with all enum coins.
    Returns (prices, None) on success, or ({}, message) when cache has no data for requested assets.
    """
    if not user_assets:
        return {}, None

    allowed = {e.value for e in AssetSymbol}
    wanted = [s.upper().strip() for s in user_assets if s and s.upper().strip() in allowed]
    if not wanted:
        return {}, None

    with _cache_lock:
        result = {s: _prices_cache[s] for s in wanted if s in _prices_cache}

    if not result and wanted:
        return {}, PRICES_UNAVAILABLE_MESSAGE
    return result, None


def clear_prices_cache() -> None:
    """Clear the in-memory prices cache (for tests)."""
    with _cache_lock:
        _prices_cache.clear()
