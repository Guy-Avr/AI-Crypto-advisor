from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models import User
from app.schemas.preferences import OnboardingRequest, OnboardingResponse
from app.services.preferences_service import save_preferences

router = APIRouter()


@router.post("/", response_model=OnboardingResponse)
def onboarding(
    body: OnboardingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OnboardingResponse:
    """Save onboarding preferences (assets, investor type, content types). Allowed only once per user."""
    if current_user.preferences is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Onboarding already completed",
        )
    pref = save_preferences(db, current_user.id, body)
    return OnboardingResponse(
        id=str(pref.id),
        user_id=str(pref.user_id),
        assets=pref.assets,
        investor_type=pref.investor_type,
        content_types=pref.content_types,
    )
