import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import InvestorType
from app.models.user import User


class Preferences(Base):
    __tablename__ = "preferences"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    assets: Mapped[list] = mapped_column(JSONB, nullable=False)  # e.g. ["BTC", "ETH"]
    investor_type: Mapped[InvestorType] = mapped_column(
        Enum(InvestorType, name="investor_enum", create_type=True),
        nullable=False,
    )
    content_types: Mapped[list] = mapped_column(
        JSONB, nullable=False
    )  # e.g. ["news", "ai", "memes"]
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    user: Mapped["User"] = relationship("User", back_populates="preferences")
