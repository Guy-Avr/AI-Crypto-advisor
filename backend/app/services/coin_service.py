"""
Crypto prices: CoinGecko primary, Binance as fallback (no API key).
In-memory cache refreshed every 5 minutes. Per-request: filter cache by user_assets only.
"""

import logging
import threading
from typing import Any

import httpx

from app.core.config import get_settings
from app.models.enums import AssetSymbol

logger = logging.getLogger(__name__)

CACHE_TTL_SEC = 300  # 5 minutes
BINANCE_TICKER_URL = "https://api.binance.com/api/v3/ticker/price"

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


def _fetch_prices_binance(timeout: float = 10.0) -> dict[str, float]:
    """
    Fetch USD prices from Binance (no API key). Returns symbol -> price for our AssetSymbol set.
    Prefer XXXUSD when available, else XXXUSDT. Stablecoins USDT/USDC = 1.0.
    """
    result: dict[str, float] = {}
    try:
        with httpx.Client(timeout=timeout) as client:
            response = client.get(BINANCE_TICKER_URL)
            response.raise_for_status()
        items = response.json()
    except (httpx.HTTPError, httpx.TimeoutException) as e:
        logger.warning("Binance fallback failed: %s", e)
        return result
    except Exception as e:
        logger.warning("Binance fallback error: %s", e)
        return result

    if not isinstance(items, list):
        return result

    # Build map: "BTCUSD" -> price, "BTCUSDT" -> price, ...
    pair_to_price: dict[str, float] = {}
    for item in items:
        if isinstance(item, dict) and "symbol" in item and "price" in item:
            try:
                pair_to_price[item["symbol"]] = float(item["price"])
            except (TypeError, ValueError):
                pass

    # Map our symbols: prefer XXXUSD, else XXXUSDT (or 1.0 for USDT/USDC)
    for sym in AssetSymbol:
        s = sym.value
        if s in ("USDT", "USDC"):
            result[s] = 1.0
            continue
        pair_usd = f"{s}USD"
        pair_usdt = f"{s}USDT"
        if pair_usd in pair_to_price:
            result[s] = pair_to_price[pair_usd]
        elif pair_usdt in pair_to_price:
            result[s] = pair_to_price[pair_usdt]
    logger.info("Binance fallback: %s symbols", len(result))
    return result


def refresh_prices_cache() -> None:
    """
    Fetch USD prices for ALL AssetSymbol enum coins. Primary: CoinGecko; on failure use Binance fallback.
    Called every 5 minutes by a background thread; one API call per refresh.
    """
    ids = list(ASSET_TO_COINGECKO_ID.values())
    symbol_by_id: dict[str, str] = {cg_id: sym.value for sym, cg_id in ASSET_TO_COINGECKO_ID.items()}
    settings = get_settings()
    timeout = max(5.0, float(settings.COINGECKO_TIMEOUT or 10))
    result: dict[str, float] = {}

    # Try CoinGecko first
    url = settings.COINGECKO_API_URL or "https://api.coingecko.com/api/v3/simple/price"
    params: dict[str, Any] = {
        "ids": ",".join(ids),
        "vs_currencies": "usd",
    }
    try:
        with httpx.Client(timeout=timeout) as client:
            response = client.get(url, params=params)
            if response.status_code == 429:
                raise httpx.HTTPStatusError("429 Too Many Requests", request=response.request, response=response)
            response.raise_for_status()
        data = response.json()
        for cg_id, symbol in symbol_by_id.items():
            coin = data.get(cg_id)
            if isinstance(coin, dict) and "usd" in coin:
                try:
                    result[symbol] = float(coin["usd"])
                except (TypeError, ValueError):
                    pass
        if result:
            with _cache_lock:
                _prices_cache.clear()
                _prices_cache.update(result)
            logger.info("Prices cache refreshed from CoinGecko: %s symbols", len(result))
            return
    except (httpx.HTTPError, httpx.TimeoutException) as e:
        logger.warning("CoinGecko cache refresh failed: %s", e)
    except Exception as e:
        logger.warning("CoinGecko cache refresh error: %s", e)

    # Fallback: Binance (no API key)
    result = _fetch_prices_binance(timeout=timeout)
    if result:
        with _cache_lock:
            _prices_cache.clear()
            _prices_cache.update(result)
        logger.info("Prices cache refreshed from Binance fallback: %s symbols", len(result))


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
