from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

# ─── Request Schemas ───


class TaskSubmissionCreate(BaseModel):
    solution_text: str = Field(..., min_length=10)
    colab_link: str | None = None
    notes: str | None = None

    @field_validator("colab_link")
    @classmethod
    def validate_colab_link(cls, v: str | None) -> str | None:
        if v is not None and v.strip() and "colab.research.google.com" not in v:
            raise ValueError("Colab link must be a valid Google Colab URL")
        return v


# ─── Response Schemas ───


class TaskResourceResponse(BaseModel):
    id: UUID
    title: str
    url: str
    resource_type: str
    display_order: int | None = None

    model_config = {"from_attributes": True}


class TaskResponse(BaseModel):
    id: UUID
    slug: str
    track: str
    difficulty: str
    title: str
    description: str
    beginner_guide: str
    hint: str
    xp_reward: int
    display_order: int
    colab_url: str
    is_weekly: bool = False
    resources: list[TaskResourceResponse] = []

    model_config = {"from_attributes": True}


class TaskListItem(BaseModel):
    id: UUID
    slug: str
    track: str
    difficulty: str
    title: str
    description: str
    xp_reward: int
    display_order: int
    colab_url: str
    is_weekly: bool = False
    completed: bool = False
    show_beginner_guide: bool = False

    model_config = {"from_attributes": True}


class BadgeEarned(BaseModel):
    slug: str
    name: str
    icon: str
    description: str
    xp_bonus: int
    track_color: str | None = None


class Benchmarks(BaseModel):
    execution_time_ms: int
    memory_usage_mb: float
    tests_passed: int
    total_tests: int
    insights: list[str]


class TaskSubmissionResponse(BaseModel):
    xp_earned: int
    total_xp: int
    rank: dict
    newly_earned_badges: list[BadgeEarned] = []
    celebration_message: str
    benchmarks: Benchmarks | None = None


class SubmissionDetailResponse(BaseModel):
    id: UUID
    task_id: UUID
    solution_text: str
    colab_link: str | None = None
    notes: str | None = None
    xp_awarded: int
    submitted_at: datetime

    model_config = {"from_attributes": True}
