from dataclasses import dataclass

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps import get_current_user
from app.models import User
from app.schemas.dashboard import (
    AiInsightResponse,
    DashboardResponse,
    MemeResponse,
    NewsResponse,
    PricesResponse,
)
from app.services.ai_insight_service import get_ai_insight
from app.services.coin_service import get_prices
from app.services.meme_service import get_meme
from app.services.news_service import get_news

router = APIRouter()


@dataclass
class DashboardContext:
    """User's dashboard preferences: assets, content_types, investor_type (for AI insight)."""

    has_preferences: bool
    assets: list[str]
    content_types: list[str]
    investor_type: str  # e.g. "HODLer", "DayTrader" from preferences


def get_dashboard_context(current_user: User = Depends(get_current_user)) -> DashboardContext:
    """Dependency: extract assets, content_types, investor_type from current user's preferences."""
    if not current_user.preferences:
        return DashboardContext(has_preferences=False, assets=[], content_types=[], investor_type="")
    raw = current_user.preferences.content_types or []
    content_types = [str(c).strip().lower() for c in raw if c is not None]
    assets = current_user.preferences.assets
    if not isinstance(assets, list):
        assets = []
    it = current_user.preferences.investor_type
    investor_type = getattr(it, "value", str(it) if it else "") or ""
    return DashboardContext(
        has_preferences=True,
        assets=list(assets),
        content_types=content_types,
        investor_type=investor_type or "",
    )


@router.get("", response_model=DashboardResponse)
def get_dashboard(ctx: DashboardContext = Depends(get_dashboard_context)) -> DashboardResponse:
    """Aggregated dashboard: prices, news, AI insight, meme in one call. Requires onboarding."""
    if not ctx.has_preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Complete onboarding to see dashboard",
        )
    prices, prices_message = get_prices(ctx.assets)
    news, news_message = get_news(ctx.assets)
    ai_insight = get_ai_insight(
        assets=ctx.assets,
        content_types=ctx.content_types,
        investor_type=ctx.investor_type or None,
    )
    meme = get_meme(investor_type=ctx.investor_type or None)
    
    return DashboardResponse(
        prices=prices,
        news=news,
        ai_insight=ai_insight,
        meme=meme,
    )


@router.get("/prices", response_model=PricesResponse)
def get_dashboard_prices(ctx: DashboardContext = Depends(get_dashboard_context)) -> PricesResponse:
    """Coin prices in USD for the user's chosen assets. Empty prices + message if no assets."""
    if not ctx.has_preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Complete onboarding to see prices",
        ) 
    prices, message = get_prices(ctx.assets)
    return PricesResponse(prices=prices, message=message)


@router.get("/news", response_model=NewsResponse)
def get_dashboard_news(ctx: DashboardContext = Depends(get_dashboard_context)) -> NewsResponse:
    """Market news (CryptoCompare). Requires onboarding (preferences)."""
    if not ctx.has_preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Complete onboarding to see news",
        )
    news, message = get_news(ctx.assets)
    return NewsResponse(news=news, message=message)


@router.get("/ai-insight", response_model=AiInsightResponse)
def get_dashboard_ai_insight(ctx: DashboardContext = Depends(get_dashboard_context)) -> AiInsightResponse:
    """AI insight of the day. Requires onboarding (preferences)."""
    if not ctx.has_preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Complete onboarding to see AI insight",
        )
    return AiInsightResponse(
        ai_insight=get_ai_insight(
            assets=ctx.assets,
            content_types=ctx.content_types,
            investor_type=ctx.investor_type or None,
        )
    )


@router.get("/meme", response_model=MemeResponse)
def get_dashboard_meme(ctx: DashboardContext = Depends(get_dashboard_context)) -> MemeResponse:
    """Fun crypto meme, chosen by investor_type. Requires onboarding (preferences)."""
    if not ctx.has_preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Complete onboarding to see meme",
        )
    meme = get_meme(investor_type=ctx.investor_type or None)
    if not meme:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No meme available",
        )
    return MemeResponse(meme=meme)
