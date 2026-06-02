"""Review SQLAlchemy models."""

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.session import Base


class ReviewRecord(Base):
    """Review record model stored in PostgreSQL."""

    __tablename__ = "review_records"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    knowledge_node_id: Mapped[str] = mapped_column(
        String(100),
        index=True,
        nullable=False,
    )
    quality: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )  # 0-5: 0-2 fail/reset, 3 okay, 4-5 good
    ease_factor: Mapped[float] = mapped_column(
        Float,
        default=2.5,
        nullable=False,
    )
    interval: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )  # days
    repetitions: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    next_review_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    mastery_level: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )  # 0.0 - 1.0
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        Index("ix_review_records_user_node", "user_id", "knowledge_node_id"),
        Index("ix_review_records_next_review", "next_review_date"),
    )

    def __repr__(self) -> str:
        return f"<ReviewRecord user={self.user_id} node={self.knowledge_node_id} q={self.quality}>"


class LearningStats(Base):
    """Learning statistics model stored in PostgreSQL."""

    __tablename__ = "learning_stats"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    total_reviews: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )
    total_learning_time: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )  # minutes
    nodes_mastered: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )
    current_streak: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )
    longest_streak: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )
    last_review_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return f"<LearningStats user={self.user_id} streak={self.current_streak}>"
