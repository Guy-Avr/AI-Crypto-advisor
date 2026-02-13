import os
from functools import lru_cache
from urllib.parse import quote_plus

from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Settings backed by environment variables."""

    def __init__(self) -> None:
        # Database
        self.POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
        self.POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "password")
        self.POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
        self.POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
        self.POSTGRES_DB: str = os.getenv("POSTGRES_DB", "ai_crypto_advisor")

        # App
        self.PROJECT_NAME: str = os.getenv("PROJECT_NAME", "AI Crypto Advisor")

        # JWT
        self.SECRET_KEY: str = os.getenv("SECRET_KEY", "")
        self.ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
        self.ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", str(60 * 24 * 7))
        )

        # CoinGecko
        self.COINGECKO_API_KEY: str = os.getenv("COINGECKO_API_KEY", "")
        self.COINGECKO_API_URL: str = os.getenv(
            "COINGECKO_API_URL", "https://api.coingecko.com/api/v3/simple/price"
        )
        self.COINGECKO_TIMEOUT: float = float(os.getenv("COINGECKO_TIMEOUT", "10"))

        # CryptoCompare (news)
        self.CRYPTOCOMPARE_NEWS_URL: str = os.getenv(
            "CRYPTOCOMPARE_NEWS_URL", "https://min-api.cryptocompare.com/data/v2/news/"
        )
        self.NEWS_TIMEOUT: float = float(os.getenv("NEWS_TIMEOUT", "10"))
        self.NEWS_LIMIT: int = int(os.getenv("NEWS_LIMIT", "10"))
        self.STATIC_NEWS_PATH: str = os.getenv("STATIC_NEWS_PATH", "")

        # CryptoPanic (optional – unused; kept for reference)
        self.CRYPTOPANIC_API_KEY: str = os.getenv("CRYPTOPANIC_API_KEY", "")

        # OpenRouter (AI insight)
        self.OPENROUTER_API_KEY: str = (os.getenv("OPENROUTER_API_KEY") or "").strip()
        self.OPENROUTER_URL: str = os.getenv(
            "OPENROUTER_URL", "https://openrouter.ai/api/v1/chat/completions"
        )
        self.OPENROUTER_MODEL_PRIMARY: str = os.getenv(
            "OPENROUTER_MODEL_PRIMARY", "google/gemma-3-12b-it:free"
        )
        self.OPENROUTER_MODEL_FALLBACK: str = os.getenv(
            "OPENROUTER_MODEL_FALLBACK", "google/gemma-3-4b-it:free"
        )
        self.OPENROUTER_TIMEOUT: float = float(os.getenv("OPENROUTER_TIMEOUT", "30"))
        self.OPENROUTER_MAX_TOKENS: int = int(os.getenv("OPENROUTER_MAX_TOKENS", "220"))
        self.OPENROUTER_TEMPERATURE: float = float(os.getenv("OPENROUTER_TEMPERATURE", "0.3"))
        self.OPENROUTER_REFERER: str = os.getenv("OPENROUTER_REFERER", "")
        self.OPENROUTER_TITLE: str = os.getenv("OPENROUTER_TITLE", "")

    @property
    def database_url(self) -> str:
        user = quote_plus(self.POSTGRES_USER)
        password = quote_plus(self.POSTGRES_PASSWORD)
        return (
            f"postgresql://{user}:{password}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
