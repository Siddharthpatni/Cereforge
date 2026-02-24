"""Pydantic schemas for community posts, comments, and voting."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


# ─── Request Schemas ───

class PostCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=300)
    body: str = Field(..., min_length=10)
    track: Optional[str] = None
    tags: list[str] = Field(default_factory=list, max_length=5)
    colab_link: Optional[str] = None
    related_task_id: Optional[UUID] = None
    is_beginner_friendly: bool = False

    @field_validator("track")
    @classmethod
    def validate_track(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            valid = {"llm", "rag", "vision", "agents"}
            if v not in valid:
                raise ValueError(f"track must be one of: {valid}")
        return v

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str]) -> list[str]:
        cleaned = []
        for tag in v[:5]:
            tag = tag.lower().strip().replace(" ", "-")[:30]
            if tag:
                cleaned.append(tag)
        return cleaned


class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=300)
    body: Optional[str] = Field(None, min_length=10)


class CommentCreate(BaseModel):
    body: str = Field(..., min_length=1)
    parent_id: Optional[UUID] = None


class VoteCreate(BaseModel):
    target_id: UUID
    target_type: str
    value: int

    @field_validator("target_type")
    @classmethod
    def validate_target_type(cls, v: str) -> str:
        if v not in {"post", "comment"}:
            raise ValueError("target_type must be 'post' or 'comment'")
        return v

    @field_validator("value")
    @classmethod
    def validate_value(cls, v: int) -> int:
        if v not in {1, -1}:
            raise ValueError("value must be +1 or -1")
        return v


# ─── Response Schemas ───

class AuthorResponse(BaseModel):
    id: UUID
    username: str
    avatar_url: Optional[str] = None
    xp: int
    skill_level: str

    model_config = {"from_attributes": True}


class CommentResponse(BaseModel):
    id: UUID
    post_id: UUID
    author: AuthorResponse
    parent_id: Optional[UUID] = None
    body: str
    vote_score: int
    is_accepted: bool
    created_at: datetime
    updated_at: datetime
    replies: list["CommentResponse"] = []

    model_config = {"from_attributes": True}


class PostResponse(BaseModel):
    id: UUID
    author: AuthorResponse
    title: str
    body: str
    track: Optional[str] = None
    tags: list[str] = []
    colab_link: Optional[str] = None
    status: str
    accepted_answer_id: Optional[UUID] = None
    vote_score: int
    view_count: int
    is_beginner_friendly: bool
    related_task_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PostListItem(BaseModel):
    id: UUID
    author: AuthorResponse
    title: str
    body: str
    track: Optional[str] = None
    tags: list[str] = []
    colab_link: Optional[str] = None
    status: str
    vote_score: int
    view_count: int
    is_beginner_friendly: bool
    comment_count: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}


class PostListResponse(BaseModel):
    items: list[PostListItem]
    total: int
    page: int
    pages: int


class VoteResponse(BaseModel):
    new_score: int
    user_vote: int
