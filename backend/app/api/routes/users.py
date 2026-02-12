from fastapi import APIRouter, Depends

from app.core.deps import get_current_user
from app.models import User
from app.schemas.user import UserMeResponse

router = APIRouter()


@router.get("/me", response_model=UserMeResponse)
def me(current_user: User = Depends(get_current_user)) -> UserMeResponse:
    """Return current user (id, email, name, onboarding done)."""
    return UserMeResponse(
        id=str(current_user.id),
        email=current_user.email,
        name=current_user.name,
        onboarding_done=current_user.preferences is not None,
    )
