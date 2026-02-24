"""Post model (community Q&A)."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

post_status_enum = ENUM("open", "solved", "closed", name="post_status_enum", create_type=True)


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    author_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    track: Mapped[str | None] = mapped_column(
        ENUM("llm", "rag", "vision", "agents", name="track_enum", create_type=False),
        nullable=True,
    )
    tags: Mapped[list] = mapped_column(JSON, default=list, server_default="[]")
    colab_link: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(post_status_enum, default="open", server_default="open")
    accepted_answer_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    vote_score: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    view_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    is_beginner_friendly: Mapped[bool] = mapped_column(Boolean, default=False)
    related_task_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=True
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    __table_args__ = (Index("ix_posts_status", "status"),)

    # Relationships
    author = relationship("User", back_populates="posts", lazy="selectin")
    comments = relationship("Comment", back_populates="post", lazy="noload")
    related_task = relationship("Task", lazy="selectin")
