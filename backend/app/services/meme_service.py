"""
Fun crypto meme for the dashboard. Loads from JSON with categories by investor_type.
"""

import json
import logging
import random
from pathlib import Path

from app.core.config import get_settings
from app.schemas.dashboard import MemeItem

logger = logging.getLogger(__name__)

# Default path when MEMES_JSON_PATH not set (backend/data/memes.json)
_DEFAULT_MEMES_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "memes.json"


def _get_memes_path() -> Path:
    """Path to memes.json: from env MEMES_JSON_PATH or default backend/data/memes.json."""
    settings = get_settings()
    if getattr(settings, "MEMES_JSON_PATH", None) and str(settings.MEMES_JSON_PATH).strip():
        return Path(str(settings.MEMES_JSON_PATH).strip())
    return _DEFAULT_MEMES_PATH


def _load_memes_by_category() -> dict[str, list[dict]]:
    """Load memes.json and return categories dict (category -> list of {title, url, image_url})."""
    path = _get_memes_path()
    if not path.is_file():
        logger.warning("Memes file not found: %s", path)
        return {}
    try:
        raw = path.read_text(encoding="utf-8")
        data = json.loads(raw)
    except (OSError, json.JSONDecodeError) as e:
        logger.warning("Failed to load memes.json: %s", e)
        return {}
    categories = data.get("categories")
    if not isinstance(categories, dict):
        return {}
    return categories


def get_meme(investor_type: str | None = None) -> MemeItem | None:
    """
    Return a random crypto meme. Picks from the category matching investor_type
    (e.g. HODLer, DayTrader); falls back to "general" if unknown or missing.
    """
    categories = _load_memes_by_category()
    if not categories:
        return None

    # Resolve category: use investor_type if it exists and has memes, else "general"
    category_key = (investor_type or "").strip()
    if not category_key or category_key not in categories:
        category_key = "general"
    pool = categories.get(category_key)
    if not isinstance(pool, list) or not pool:
        pool = categories.get("general") or []
    if not pool:
        # flatten all categories as last resort
        for v in categories.values():
            if isinstance(v, list) and v:
                pool = v
                break
    if not pool:
        return None

    item = random.choice(pool)
    if not isinstance(item, dict):
        return None
    title = item.get("title") or ""
    url = item.get("url") or ""
    image_url = item.get("image_url") or ""
    if not title or not url or not image_url:
        return None
    return MemeItem(title=title, url=url, image_url=image_url)
