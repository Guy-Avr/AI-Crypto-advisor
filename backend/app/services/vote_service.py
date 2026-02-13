"""
Vote service: store or update user feedback (up/down) per dashboard item.
Idempotent: one row per (user_id, section_type, item_id); update if exists.
"""

from uuid import UUID

from sqlalchemy.orm import Session

from app.models import Vote
from app.models.enums import SectionType, VoteType


def save_or_update_vote(
    db: Session,
    user_id: UUID,
    section_type: SectionType | str,
    item_id: str,
    vote_type: VoteType | str,
) -> str:
    """
    Store a vote or update existing one. Unique constraint (user_id, section_type, item_id)
    guarantees at most one vote per user per item per section – no duplicate rows.
    Returns "created" or "updated".
    """
    section_val = section_type.value if hasattr(section_type, "value") else str(section_type)
    vote_val = vote_type.value if hasattr(vote_type, "value") else str(vote_type)
    item_id_stripped = (item_id or "").strip()[:255]
    if not item_id_stripped:
        raise ValueError("item_id must be non-empty")

    existing = (
        db.query(Vote)
        .filter(
            Vote.user_id == user_id,
            Vote.section_type == section_val,
            Vote.item_id == item_id_stripped,
        )
        .first()
    )
    if existing:
        existing.vote_type = vote_val
        db.commit()
        db.refresh(existing)
        return "updated"
    vote = Vote(
        user_id=user_id,
        section_type=section_val,
        item_id=item_id_stripped,
        vote_type=vote_val,
    )
    db.add(vote)
    db.commit()
    db.refresh(vote)
    return "created"


def cancel_vote(
    db: Session,
    user_id: UUID,
    section_type: SectionType | str,
    item_id: str,
) -> bool:
    """
    Remove the user's vote for the given (section_type, item_id).
    Returns True if a vote was deleted, False if none existed.
    """
    section_val = section_type.value if hasattr(section_type, "value") else str(section_type)
    item_id_stripped = (item_id or "").strip()[:255]
    if not item_id_stripped:
        raise ValueError("item_id must be non-empty")

    existing = (
        db.query(Vote)
        .filter(
            Vote.user_id == user_id,
            Vote.section_type == section_val,
            Vote.item_id == item_id_stripped,
        )
        .first()
    )
    if not existing:
        return False
    db.delete(existing)
    db.commit()
    return True
