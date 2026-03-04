from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

# ─── Request Schemas ───


class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=30, pattern=r"^[a-zA-Z0-9_]+$")
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    skill_level: str = Field(...)
    background: str | None = None

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
    username: str | None = Field(None, min_length=3, max_length=30, pattern=r"^[a-zA-Z0-9_]+$")
    skill_level: str | None = None
    background: str | None = None
    avatar_url: str | None = None

    @field_validator("skill_level")
    @classmethod
    def validate_skill_level(cls, v: str | None) -> str | None:
        if v is not None:
            valid = {"absolute_beginner", "some_python", "ml_familiar", "advanced"}
            if v not in valid:
                raise ValueError(f"skill_level must be one of: {valid}")
        return v


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp_code: str = Field(..., min_length=6, max_length=6)
    new_password: str = Field(..., min_length=8, max_length=128)


# ─── Response Schemas ───


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: str
    avatar_url: str | None = None
    skill_level: str
    background: str | None = None
    xp: int
    is_email_verified: bool
    is_admin: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}


class RankInfo(BaseModel):
    name: str
    color: str
    next_rank: str | None = None
    xp_needed: int | None = None


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
    suggested_path: str | None = None
    welcome_message: str


class MeResponse(BaseModel):
    user: UserResponse
    rank: RankInfo
    badges: list = []
    enrolled_paths: list = []
    stats: dict = {}


class AdminXPUpdate(BaseModel):
    xp: int = Field(..., ge=0)
