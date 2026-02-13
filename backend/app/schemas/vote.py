from pydantic import BaseModel, Field

from app.models.enums import SectionType, VoteType


class VoteRequest(BaseModel):
    """Body for POST /vote – cast or update a vote. One vote per (user, section_type, item_id)."""

    section_type: SectionType = Field(
        ...,
        description="Dashboard section: news, price, ai, or meme",
    )
    item_id: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="External content identifier (e.g. news id, coin symbol, meme id)",
    )
    vote_type: VoteType = Field(
        ...,
        description="up or down",
    )


class VoteResponse(BaseModel):
    """Response after casting or updating a vote."""

    status: str = "ok"
    action: str = Field(
        ...,
        description="created (new vote) or updated (existing vote changed)",
    )


class VoteCancelRequest(BaseModel):
    """Body for DELETE /vote – remove a vote (cancel)."""

    section_type: SectionType = Field(
        ...,
        description="Dashboard section: news, price, ai, or meme",
    )
    item_id: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="External content identifier for the vote to cancel",
    )


class VoteCancelResponse(BaseModel):
    """Response after cancelling a vote."""

    status: str = "ok"
    action: str = "cancelled"
