from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models import User
from app.schemas.vote import (
    VoteCancelRequest,
    VoteCancelResponse,
    VoteRequest,
    VoteResponse,
)
from app.services.vote_service import cancel_vote, save_or_update_vote

router = APIRouter()


@router.post("/", response_model=VoteResponse)
def post_vote(
    body: VoteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> VoteResponse:
    """
    Cast or update a vote (up/down) for a dashboard item. Idempotent: same (section_type, item_id)
    updates the existing vote. Requires authentication.
    """
    try:
        action = save_or_update_vote(
            db=db,
            user_id=current_user.id,
            section_type=body.section_type,
            item_id=body.item_id.strip(),
            vote_type=body.vote_type,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return VoteResponse(status="ok", action=action)


@router.delete("/", response_model=VoteCancelResponse)
def delete_vote(
    body: VoteCancelRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> VoteCancelResponse:
    """
    Cancel (remove) a vote for the given section and item. Returns 404 if no vote existed.
    """
    try:
        removed = cancel_vote(
            db=db,
            user_id=current_user.id,
            section_type=body.section_type,
            item_id=body.item_id.strip(),
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No vote found for this section and item",
        )
    return VoteCancelResponse(status="ok", action="cancelled")
