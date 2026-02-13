from uuid import UUID

from sqlalchemy.orm import Session

from app.models import Preferences
from app.schemas.preferences import OnboardingRequest


def save_preferences(
    db: Session,
    user_id: UUID,
    payload: OnboardingRequest,
) -> Preferences:
    """
    Save or update onboarding preferences for a user.
    Prevents duplicate rows: one preferences row per user (create or update).
    """
    existing = db.query(Preferences).filter(Preferences.user_id == user_id).first()
    content_types_values = [x.value for x in payload.content_types]
    assets_values = [a.value for a in payload.assets]
    if existing:
        existing.assets = assets_values
        existing.investor_type = payload.investor_type
        existing.content_types = content_types_values
        db.commit()
        db.refresh(existing)
        return existing
    pref = Preferences(
        user_id=user_id,
        assets=assets_values,
        investor_type=payload.investor_type,
        content_types=content_types_values,
    )
    db.add(pref)
    db.commit()
    db.refresh(pref)
    return pref
