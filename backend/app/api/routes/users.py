"""User profile routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
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
