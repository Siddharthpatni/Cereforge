from __future__ import annotations

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.badge import Badge, UserBadge
from app.models.comment import Comment
from app.models.learning_path import PathEnrollment
from app.models.post import Post
from app.models.submission import TaskSubmission
from app.models.task import Task
from app.models.user import User
from app.schemas.user import MeResponse, RankInfo, UserResponse, UserUpdate
from app.services.xp_service import calculate_rank

router = APIRouter()

VALID_SKILL_LEVELS = {"absolute_beginner", "some_python", "ml_familiar", "advanced"}


class ProfileUpdate(BaseModel):
    """Fields a user may update on their own profile."""

    username: Optional[str] = Field(None, min_length=3, max_length=30, pattern=r"^[a-zA-Z0-9_]+$")
    background: Optional[str] = Field(None, max_length=500)
    skill_level: Optional[str] = None


@router.get("/me", response_model=MeResponse)
async def get_my_profile(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Get the currently authenticated user's own profile with full stats."""
    rank_res = calculate_rank(current_user.xp)

    # Get badges
    badges_result = await db.execute(
        select(UserBadge).where(UserBadge.user_id == current_user.id).limit(50)
    )
    user_badges = badges_result.scalars().all()
    badges_data = [
        {
            "slug": ub.badge.slug,
            "name": ub.badge.name,
            "icon": ub.badge.icon,
            "earned_at": ub.earned_at.isoformat() if ub.earned_at else None,
        }
        for ub in user_badges
    ]

    # Get enrolled paths
    enrollments_result = await db.execute(
        select(PathEnrollment).where(PathEnrollment.user_id == current_user.id)
    )
    enrollments = enrollments_result.scalars().all()
    paths_data = [
        {
            "slug": e.path.slug,
            "title": e.path.title,
            "enrolled_at": e.enrolled_at.isoformat() if e.enrolled_at else None,
        }
        for e in enrollments
    ]

    # Get stats
    submissions_result = await db.execute(
        select(TaskSubmission).where(TaskSubmission.user_id == current_user.id)
    )
    submissions = submissions_result.scalars().all()

    stats = {
        "tasks_completed": len(submissions),
        "total_tasks": 24,  # Updated for the 24 tasks
        "badges_earned": len(user_badges),
        "total_badges": 12,
        "xp": current_user.xp,
    }

    return MeResponse(
        user=UserResponse.model_validate(current_user),
        rank=RankInfo(
            name=rank_res["name"],
            color=rank_res["color"],
            next_rank=rank_res["next_rank"],
            xp_needed=rank_res["xp_needed"],
        ),
        badges=badges_data,
        enrolled_paths=paths_data,
        stats=stats,
    )


@router.patch("/me")
async def update_my_profile(
    body: UserUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Update the currently authenticated user's profile."""
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

    rank_res = calculate_rank(current_user.xp)

    return {"user": UserResponse.model_validate(current_user).model_dump(), "rank": rank_res}


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


class ChangePassword(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)


@router.post("/me/change-password")
async def change_password(
    body: ChangePassword,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Change the current user's password. Requires current password for verification."""
    from app.core.security import hash_password, verify_password

    if not verify_password(body.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect.",
        )

    current_user.password_hash = hash_password(body.new_password)
    await db.commit()
    return {"message": "Password changed successfully. Please log in again."}
