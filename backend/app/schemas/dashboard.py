from pydantic import BaseModel


class NewsItem(BaseModel):
    title: str
    url: str
    source: str = ""
    published_at: str = ""
    coins: list[str] = []  # Coin symbols this news item is about (e.g. ["BTC", "ETH"])


class MemeItem(BaseModel):
    title: str
    url: str
    image_url: str


class PricesResponse(BaseModel):
    """Coin prices in USD. When the provider is unavailable, prices is empty and message explains."""

    prices: dict[str, float] = {}
    message: str | None = None  # Set when loading failed (e.g. "Price data is temporarily unavailable.")


class NewsResponse(BaseModel):
    """Market news section. When loading fails, news is empty and message explains."""

    news: list[NewsItem] = []
    message: str | None = None  # Set when loading failed


class AiInsightResponse(BaseModel):
    """AI insight of the day."""

    ai_insight: str = ""


class MemeResponse(BaseModel):
    """Fun crypto meme."""

    meme: MemeItem


class DashboardResponse(BaseModel):
    """Daily dashboard: 4 sections. Prefer separate GET /dashboard/{prices|news|ai-insight|meme} for different cache/update needs."""

    news: list[NewsItem] = []
    prices: dict[str, float] = {}
    ai_insight: str = ""
    meme: MemeItem | None = None
