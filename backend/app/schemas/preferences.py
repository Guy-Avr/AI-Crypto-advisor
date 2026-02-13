from pydantic import BaseModel, Field

from app.models.enums import AssetSymbol, InvestorType, SectionType


class OnboardingRequest(BaseModel):
    """Body for POST /onboarding – assets, investor type, content types. Only enum values allowed."""

    assets: list[AssetSymbol] = Field(
        ...,
        min_length=1,
        max_length=50,
        description="List of supported asset symbols (use only values from AssetSymbol enum)",
    )
    investor_type: InvestorType
    content_types: list[SectionType] = Field(
        ...,
        min_length=1,
        max_length=4,
        description="Dashboard sections: news, price, ai, meme",
    )


class OnboardingResponse(BaseModel):
    """Response after saving onboarding preferences."""

    id: str
    user_id: str
    assets: list[str]
    investor_type: InvestorType
    content_types: list[str]
