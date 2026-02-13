"""
AI Insight of the day via OpenRouter. Dynamic prompt from content_types + assets; static fallback on failure.
"""

import logging
import time
from typing import Any

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)

RETRY_DELAY_SEC = 3
MAX_RETRIES = 2
MAX_WORDS = 150

# Human-readable labels for content_types (for the prompt)
CONTENT_TYPE_LABELS: dict[str, str] = {
    "news": "market news",
    "price": "prices",
    "ai": "AI insights",
    "meme": "memes",
}

FALLBACK_INSIGHT = (
    "Crypto markets often move on macro news and sentiment. "
    "Diversify across assets you believe in long-term, and consider dollar-cost averaging. "
    "This is a static insight; add OPENROUTER_API_KEY for a daily AI-generated take."
)


def build_prompt(
    assets: list[str] | None = None,
    content_types: list[str] | None = None,
    investor_type: str | None = None,
) -> str:
    """
    Build a dynamic prompt from preferences: investor_type, content_types (dashboard sections),
    and assets. The model tailors the insight to this profile.
    """
    assets_str = ", ".join((assets or [])[:5]) if assets else "crypto"
    parts: list[str] = []
    if investor_type:
        parts.append(f"The user's investor type is: {investor_type}.")
    if content_types:
        labels = [CONTENT_TYPE_LABELS.get(ct, ct) for ct in content_types if ct]
        if labels:
            sections_desc = " and ".join(labels)
            parts.append(f"Their dashboard shows: {sections_desc}.")
    context = " ".join(parts) if parts else ""
    if context:
        context = context.rstrip() + " "

    return (
        f"{context}"
        f"In one short paragraph of at most {MAX_WORDS} words, give a neutral, professional "
        f"crypto market insight relevant to {assets_str}. No emojis, no financial advice. Be concise and factual."
    ).strip()


def _truncate_to_words(text: str, max_words: int = MAX_WORDS) -> str:
    """Limit text to max_words (whitespace-separated)."""
    words = text.split()
    if len(words) <= max_words:
        return text.strip()
    return " ".join(words[:max_words]).strip()


def get_ai_insight(
    assets: list[str] | None = None,
    content_types: list[str] | None = None,
    investor_type: str | None = None,
) -> str:
    """
    Get AI-generated crypto insight from OpenRouter. Prompt uses investor_type and
    content_types from preferences plus assets to tailor the answer.
    """
    settings = get_settings()
    api_key = (settings.OPENROUTER_API_KEY or "").strip()
    if not api_key:
        logger.debug("OPENROUTER_API_KEY missing or empty; using fallback insight")
        return FALLBACK_INSIGHT

    prompt = build_prompt(
        assets=assets,
        content_types=content_types,
        investor_type=investor_type,
    )

    headers: dict[str, str] = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    if (settings.OPENROUTER_REFERER or "").strip():
        headers["HTTP-Referer"] = settings.OPENROUTER_REFERER.strip()
    if (settings.OPENROUTER_TITLE or "").strip():
        headers["X-Title"] = settings.OPENROUTER_TITLE.strip()

    url = settings.OPENROUTER_URL or "https://openrouter.ai/api/v1/chat/completions"
    timeout = max(5.0, float(settings.OPENROUTER_TIMEOUT or 30))
    max_tokens = max(50, int(settings.OPENROUTER_MAX_TOKENS or 220))
    temperature = max(0.0, min(2.0, float(settings.OPENROUTER_TEMPERATURE or 0.3)))
    models_to_try = [
        (settings.OPENROUTER_MODEL_PRIMARY or "google/gemma-3-12b-it:free").strip(),
        (settings.OPENROUTER_MODEL_FALLBACK or "google/gemma-3-4b-it:free").strip(),
    ]

    for model in models_to_try:
        if not model:
            continue
        payload: dict[str, Any] = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        for attempt in range(MAX_RETRIES):
            try:
                with httpx.Client(timeout=timeout) as client:
                    response = client.post(url, json=payload, headers=headers)
                if response.status_code == 200:
                    try:
                        data = response.json()
                        choices = data.get("choices")
                        if isinstance(choices, list) and choices:
                            msg = choices[0].get("message") or {}
                            text = (msg.get("content") or "").strip()
                            if not text:
                                text = (choices[0].get("text") or "").strip()
                            if text:
                                return _truncate_to_words(text)
                    except Exception as e:
                        logger.warning("OpenRouter response parse failed: %s", e)
                    break  # try next model
                if response.status_code == 402:
                    logger.warning("OpenRouter 402 (Payment Required); skipping retries and fallback model")
                    return FALLBACK_INSIGHT
                if response.status_code == 429:
                    logger.warning(
                        "OpenRouter rate limit (429) for model=%s attempt=%s; retrying in %ss",
                        model, attempt + 1, RETRY_DELAY_SEC,
                    )
                    if attempt < MAX_RETRIES - 1:
                        time.sleep(RETRY_DELAY_SEC)
                        continue
                    break  # try next model
                logger.warning(
                    "OpenRouter API error: status=%s model=%s body=%s",
                    response.status_code, model, response.text[:500],
                )
                break
            except (httpx.HTTPError, httpx.TimeoutException) as e:
                logger.warning("OpenRouter API failed (model=%s): %s", model, e)
                break

    return FALLBACK_INSIGHT
