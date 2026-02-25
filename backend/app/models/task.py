"""Task and TaskResource models."""

from __future__ import annotations


import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

track_enum = ENUM("llm", "rag", "vision", "agents", name="track_enum", create_type=True)
difficulty_enum = ENUM(
    "beginner", "intermediate", "expert", name="difficulty_enum", create_type=True
)
resource_type_enum = ENUM(
    "article", "video", "colab", "docs", name="resource_type_enum", create_type=True
)


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    track: Mapped[str] = mapped_column(track_enum, nullable=False)
    difficulty: Mapped[str] = mapped_column(difficulty_enum, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    beginner_guide: Mapped[str] = mapped_column(Text, nullable=False)
    hint: Mapped[str] = mapped_column(Text, nullable=False)
    xp_reward: Mapped[int] = mapped_column(Integer, nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False)
    colab_url: Mapped[str] = mapped_column(String(500), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    resources = relationship("TaskResource", back_populates="task", lazy="selectin")
    submissions = relationship("TaskSubmission", back_populates="task", lazy="noload")


class TaskResource(Base):
    __tablename__ = "task_resources"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    resource_type: Mapped[str] = mapped_column(resource_type_enum, nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, nullable=True)

    # Relationships
    task = relationship("Task", back_populates="resources")
