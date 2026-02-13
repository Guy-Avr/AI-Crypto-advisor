"""
CoinGecko API integration for crypto prices.
Uses the public API (api.coingecko.com) with ids and vs_currencies.
On API failure returns empty prices and an explanation message; no fabricated data.
"""

import logging
from typing import Any

import httpx

from app.core.config import get_settings
from app.models.enums import AssetSymbol

logger = logging.getLogger(__name__)

# Message returned when the price provider is unavailable (no invented data).
PRICES_UNAVAILABLE_MESSAGE = (
    "Price data is temporarily unavailable. Please try again later."
)

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


def get_prices(user_assets: list[str]) -> tuple[dict[str, float], str | None]:
    """
    Fetch current USD prices for the given asset symbols.
    Returns (prices, None) on success, or ({}, message) when the provider is unavailable.
    No fabricated data; message explains the failure.
    """
    if not user_assets:
        return {}, None

    allowed = {e.value for e in AssetSymbol}
    ids = []
    symbol_by_id: dict[str, str] = {}
    for symbol in user_assets:
        upper = symbol.upper().strip()
        if upper not in allowed:
            continue
        try:
            asset_enum = AssetSymbol(upper)
        except ValueError:
            continue
        cg_id = ASSET_TO_COINGECKO_ID.get(asset_enum)
        if cg_id and cg_id not in symbol_by_id:
            ids.append(cg_id)
            symbol_by_id[cg_id] = upper

    if not ids:
        return {}, None

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
    except (httpx.HTTPError, httpx.TimeoutException) as e:
        logger.warning("CoinGecko API failed: %s", e)
        return {}, PRICES_UNAVAILABLE_MESSAGE

    try:
        data = response.json()
    except Exception as e:
        logger.warning("CoinGecko response parse failed: %s", e)
        return {}, PRICES_UNAVAILABLE_MESSAGE

    result: dict[str, float] = {}
    for cg_id, symbol in symbol_by_id.items():
        coin = data.get(cg_id)
        if isinstance(coin, dict) and "usd" in coin:
            try:
                result[symbol] = float(coin["usd"])
            except (TypeError, ValueError):
                pass

    if not result:
        logger.warning("CoinGecko returned no prices for ids=%s", ids)
        return {}, PRICES_UNAVAILABLE_MESSAGE
    return result, None
