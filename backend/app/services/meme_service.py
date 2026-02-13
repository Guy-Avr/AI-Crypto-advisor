"""
Fun crypto meme for the dashboard. Static list fallback (no external API required).
"""

import random

from app.schemas.dashboard import MemeItem

# Static list of crypto memes (safe, public URLs). Add more as needed.
MEMES: list[MemeItem] = [
    MemeItem(
        title="To the moon",
        url="https://www.reddit.com/r/cryptocurrency/",
        image_url="https://i.imgflip.com/2/3pq0uv.jpg",
    ),
    MemeItem(
        title="HODL",
        url="https://www.reddit.com/r/cryptocurrency/",
        image_url="https://i.imgflip.com/2/4goux.jpg",
    ),
    MemeItem(
        title="When BTC pumps",
        url="https://www.reddit.com/r/bitcoin/",
        image_url="https://i.imgflip.com/2/2gsodq.jpg",
    ),
    MemeItem(
        title="Diamond hands",
        url="https://www.reddit.com/r/cryptocurrency/",
        image_url="https://i.imgflip.com/2/5k2s2.jpg",
    ),
    MemeItem(
        title="Crypto winter",
        url="https://www.reddit.com/r/cryptocurrency/",
        image_url="https://i.imgflip.com/2/1bhk.jpg",
    ),
]


def get_meme() -> MemeItem | None:
    """Return a random crypto meme. Uses static list (no API)."""
    if not MEMES:
        return None
    return random.choice(MEMES)
