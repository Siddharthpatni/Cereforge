"""User profile routes."""

from __future__ import annotations

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.badge import Badge, UserBadge
from app.models.comment import Comment
from app.models.post import Post
from app.models.submission import TaskSubmission
from app.models.task import Task
from app.models.user import User
from app.services.xp_service import calculate_rank

router = APIRouter()

VALID_SKILL_LEVELS = {"absolute_beginner", "some_python", "ml_familiar", "advanced"}


class ProfileUpdate(BaseModel):
    """Fields a user may update on their own profile."""

    username: Optional[str] = Field(None, min_length=3, max_length=30, pattern=r"^[a-zA-Z0-9_]+$")
    background: Optional[str] = Field(None, max_length=500)
    skill_level: Optional[str] = None


@router.get("/me")
async def get_my_profile(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Get the currently authenticated user's own profile."""
    return {
        "id": str(current_user.id),
        "username": current_user.username,
        "email": current_user.email,
        "avatar_url": current_user.avatar_url,
        "skill_level": current_user.skill_level,
        "background": current_user.background,
        "xp": current_user.xp,
        "is_admin": current_user.is_admin,
        "created_at": current_user.created_at.isoformat(),
    }


@router.patch("/me")
async def update_my_profile(
    body: ProfileUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Update the currently authenticated user's profile."""
    if body.skill_level and body.skill_level not in VALID_SKILL_LEVELS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"skill_level must be one of: {', '.join(sorted(VALID_SKILL_LEVELS))}",
        )

    # Check username uniqueness if changing
    if body.username and body.username != current_user.username:
        existing = await db.execute(select(User).where(User.username == body.username))
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username is already taken.",
            )
        current_user.username = body.username

    if body.background is not None:
        current_user.background = body.background
    if body.skill_level is not None:
        current_user.skill_level = body.skill_level

    await db.commit()
    await db.refresh(current_user)

    return {
        "id": str(current_user.id),
        "username": current_user.username,
        "email": current_user.email,
        "avatar_url": current_user.avatar_url,
        "skill_level": current_user.skill_level,
        "background": current_user.background,
        "xp": current_user.xp,
        "created_at": current_user.created_at.isoformat(),
    }


@router.get("/{username}")
async def get_user_profile(
    username: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Get a user's public profile."""
    result = await db.execute(select(User).where(User.username == username, User.is_active))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    rank = calculate_rank(user.xp)

    # Badges
    badges_result = await db.execute(select(UserBadge).where(UserBadge.user_id == user.id))
    user_badges = badges_result.scalars().all()

    all_badges_result = await db.execute(select(Badge).order_by(Badge.display_order))
    all_badges = all_badges_result.scalars().all()
    earned_ids = {ub.badge_id for ub in user_badges}
    earned_dates = {ub.badge_id: ub.earned_at for ub in user_badges}

    badges_data = [
        {
            "slug": b.slug,
            "name": b.name,
            "icon": b.icon,
            "description": b.description,
            "xp_bonus": b.xp_bonus,
            "earned": b.id in earned_ids,
            "earned_at": earned_dates[b.id].isoformat() if b.id in earned_dates else None,
        }
        for b in all_badges
    ]

    # Completions
    completions_result = await db.execute(
        select(TaskSubmission, Task)
        .join(Task, TaskSubmission.task_id == Task.id)
        .where(TaskSubmission.user_id == user.id)
        .order_by(desc(TaskSubmission.submitted_at))
    )
    completions = [
        {
            "task_slug": task.slug,
            "task_title": task.title,
            "track": task.track,
            "xp_earned": sub.xp_awarded,
            "submitted_at": sub.submitted_at.isoformat(),
        }
        for sub, task in completions_result.all()
    ]

    # Posts
    posts_result = await db.execute(
        select(Post)
        .where(Post.author_id == user.id, Post.is_deleted.is_(False))
        .order_by(desc(Post.created_at))
        .limit(20)
    )
    posts_data = [
        {
            "id": str(p.id),
            "title": p.title,
            "vote_score": p.vote_score,
            "status": p.status,
            "created_at": p.created_at.isoformat(),
        }
        for p in posts_result.scalars().all()
    ]

    # Stats
    posts_count = await db.execute(
        select(func.count(Post.id)).where(Post.author_id == user.id, Post.is_deleted.is_(False))
    )
    answers_count = await db.execute(
        select(func.count(Comment.id)).where(
            Comment.author_id == user.id, Comment.is_deleted.is_(False)
        )
    )

    return {
        "user": {
            "id": str(user.id),
            "username": user.username,
            "avatar_url": user.avatar_url,
            "skill_level": user.skill_level,
            "background": user.background,
            "xp": user.xp,
            "created_at": user.created_at.isoformat(),
        },
        "rank": rank,
        "stats": {
            "xp": user.xp,
            "tasks_completed": len(completions),
            "posts_count": posts_count.scalar() or 0,
            "answers_count": answers_count.scalar() or 0,
            "badges_earned": len(user_badges),
        },
        "badges": badges_data,
        "completions": completions,
        "posts": posts_data,
    }
