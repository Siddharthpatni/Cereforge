"""Pydantic schemas for learning paths, badges, leaderboard, etc."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

# ─── Badge Schemas ───


class BadgeResponse(BaseModel):
    id: UUID
    slug: str
    name: str
    icon: str
    description: str
    condition_type: str
    xp_bonus: int
    display_order: int
    earned: bool = False
    earned_at: datetime | None = None

    model_config = {"from_attributes": True}


# ─── Learning Path Schemas ───


class LessonResponse(BaseModel):
    id: UUID
    title: str
    lesson_type: str
    duration_minutes: int
    external_url: str | None = None
    display_order: int

    model_config = {"from_attributes": True}


class ModuleResponse(BaseModel):
    id: UUID
    title: str
    display_order: int
    lessons: list[LessonResponse] = []

    model_config = {"from_attributes": True}


class LearningPathResponse(BaseModel):
    id: UUID
    slug: str
    title: str
    description: str
    for_skill_levels: list[str]
    duration_days: int
    task_sequence: list[UUID]
    display_order: int
    enrolled: bool = False
    recommended: bool = False
    progress: float = 0.0

    model_config = {"from_attributes": True}


class TaskBasicResponse(BaseModel):
    id: UUID
    slug: str
    title: str
    track: str
    difficulty: str
    xp_reward: int
    is_completed: bool = False
    sample_solution: str | None = None

    model_config = {"from_attributes": True}


class PathDetailResponse(BaseModel):
    id: UUID
    slug: str
    title: str
    description: str
    for_skill_levels: list[str]
    duration_days: int
    task_sequence: list[UUID]
    display_order: int
    modules: list[ModuleResponse] = []
    tasks: list[TaskBasicResponse] = []
    enrolled: bool = False
    progress: float = 0.0
    next_task: str | None = None

    model_config = {"from_attributes": True}


class EnrollResponse(BaseModel):
    enrolled: bool = True
    next_task_slug: str | None = None


# ─── Leaderboard Schemas ───


class LeaderboardEntry(BaseModel):
    position: int
    user: dict
    rank: dict
    xp: int
    tasks_completed: int
    badges_count: int
    top_badges: list[str] = []


class LeaderboardResponse(BaseModel):
    items: list[LeaderboardEntry]
    current_user_position: int | None = None


# ─── Dashboard Schemas ───


class DashboardResponse(BaseModel):
    stats: dict
    rank: dict
    next_task: dict | None = None
    recent_completions: list = []
    badges: list = []
    enrolled_paths: list = []
    activity_feed: list = []


# ─── Notification Schemas ───


class NotificationResponse(BaseModel):
    id: UUID
    type: str
    title: str
    body: str
    is_read: bool
    metadata: dict | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class MarkReadRequest(BaseModel):
    ids: list[UUID]


# ─── AI Mentor Schemas ───


class MentorGuidanceRequest(BaseModel):
    task_slug: str
    user_message: str


class CommunityAssistRequest(BaseModel):
    post_id: UUID


# ─── Generic Response ───


class SuccessResponse(BaseModel):
    data: dict | None = None
    message: str = "Success"
    status: str = "success"


class ErrorResponse(BaseModel):
    error: str
    detail: str
    status: str = "error"
