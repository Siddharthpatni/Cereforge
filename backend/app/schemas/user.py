"""Pydantic schemas for user-related requests and responses."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


# ─── Request Schemas ───

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=30, pattern=r"^[a-zA-Z0-9_]+$")
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    skill_level: str = Field(...)
    background: Optional[str] = None

    @field_validator("skill_level")
    @classmethod
    def validate_skill_level(cls, v: str) -> str:
        valid = {"absolute_beginner", "some_python", "ml_familiar", "advanced"}
        if v not in valid:
            raise ValueError(f"skill_level must be one of: {valid}")
        return v


class UserLogin(BaseModel):
    email_or_username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class TokenRefresh(BaseModel):
    refresh_token: str


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=30, pattern=r"^[a-zA-Z0-9_]+$")
    skill_level: Optional[str] = None
    background: Optional[str] = None
    avatar_url: Optional[str] = None

    @field_validator("skill_level")
    @classmethod
    def validate_skill_level(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            valid = {"absolute_beginner", "some_python", "ml_familiar", "advanced"}
            if v not in valid:
                raise ValueError(f"skill_level must be one of: {valid}")
        return v


# ─── Response Schemas ───

class UserResponse(BaseModel):
    id: UUID
    username: str
    email: str
    avatar_url: Optional[str] = None
    skill_level: str
    background: Optional[str] = None
    xp: int
    is_email_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class RankInfo(BaseModel):
    name: str
    color: str
    next_rank: Optional[str] = None
    xp_needed: Optional[int] = None


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse
    rank: RankInfo


class RegisterResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse
    rank: RankInfo
    suggested_path: Optional[str] = None
    welcome_message: str


class MeResponse(BaseModel):
    user: UserResponse
    rank: RankInfo
    badges: list = []
    enrolled_paths: list = []
    stats: dict = {}
