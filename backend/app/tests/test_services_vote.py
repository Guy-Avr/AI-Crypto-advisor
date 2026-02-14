"""Unit tests for vote_service (DB required)."""

import uuid

import pytest
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models import User
from app.models.enums import SectionType, VoteType
from app.services.vote_service import cancel_vote, save_or_update_vote


def _make_test_user(db: Session) -> User:
    from app.core.security import hash_password
    user = User(
        email=f"vote-test-{uuid.uuid4().hex}@example.com",
        name="Vote Test",
        hashed_password=hash_password("pass123"),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def db_session():
    """Yield a real DB session (uses project DB)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_save_or_update_vote_created(db_session: Session):
    """First vote for (user, section, item) returns 'created'."""
    user = _make_test_user(db_session)
    action = save_or_update_vote(
        db_session, user.id, SectionType.news, "https://example.com/1", VoteType.up
    )
    assert action == "created"


def test_save_or_update_vote_updated(db_session: Session):
    """Second vote for same (user, section, item) returns 'updated'."""
    user = _make_test_user(db_session)
    save_or_update_vote(
        db_session, user.id, SectionType.price, "BTC|100", VoteType.up
    )
    action = save_or_update_vote(
        db_session, user.id, SectionType.price, "BTC|100", VoteType.down
    )
    assert action == "updated"


def test_save_or_update_vote_empty_item_id_raises(db_session: Session):
    """Empty item_id raises ValueError."""
    user = _make_test_user(db_session)
    with pytest.raises(ValueError, match="item_id"):
        save_or_update_vote(
            db_session, user.id, SectionType.ai, "  ", VoteType.up
        )


def test_cancel_vote_returns_true_when_deleted(db_session: Session):
    """cancel_vote returns True when a vote existed and was removed."""
    user = _make_test_user(db_session)
    save_or_update_vote(db_session, user.id, SectionType.meme, "meme-1", VoteType.up)
    removed = cancel_vote(db_session, user.id, SectionType.meme, "meme-1")
    assert removed is True


def test_cancel_vote_returns_false_when_none(db_session: Session):
    """cancel_vote returns False when no vote existed."""
    user = _make_test_user(db_session)
    removed = cancel_vote(db_session, user.id, SectionType.news, "no-such-id")
    assert removed is False
