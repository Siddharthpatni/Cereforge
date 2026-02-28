"""Learning path, module, lesson, and enrollment models."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

# No typing imports needed
from sqlalchemy import ARRAY, Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

lesson_type_enum = ENUM(
    "article", "video", "colab", "quiz", name="lesson_type_enum", create_type=True
)


class LearningPath(Base):
    __tablename__ = "learning_paths"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    for_skill_levels: Mapped[list] = mapped_column(ARRAY(String), nullable=False)
    duration_days: Mapped[int] = mapped_column(Integer, nullable=False)
    task_sequence: Mapped[list] = mapped_column(ARRAY(UUID(as_uuid=True)), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationships
    modules = relationship(
        "PathModule", back_populates="path", lazy="selectin", order_by="PathModule.display_order"
    )
    enrollments = relationship("PathEnrollment", back_populates="path", lazy="noload")


class PathModule(Base):
    __tablename__ = "path_modules"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    path_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("learning_paths.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationships
    path = relationship("LearningPath", back_populates="modules")
    lessons = relationship(
        "PathLesson", back_populates="module", lazy="selectin", order_by="PathLesson.display_order"
    )


class PathLesson(Base):
    __tablename__ = "path_lessons"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    module_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("path_modules.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    lesson_type: Mapped[str] = mapped_column(lesson_type_enum, nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    external_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationships
    module = relationship("PathModule", back_populates="lessons")


class PathEnrollment(Base):
    __tablename__ = "path_enrollments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    path_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("learning_paths.id"), nullable=False
    )
    enrolled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = ({"sqlite_autoincrement": True},)

    # Relationships
    user = relationship("User", back_populates="path_enrollments")
    path = relationship("LearningPath", back_populates="enrollments", lazy="selectin")
