"""Leaderboard routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.badge import UserBadge
from app.models.submission import TaskSubmission
from app.models.user import User
from app.services.xp_service import calculate_rank

router = APIRouter()


@router.get("")
async def get_leaderboard(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100, alias="size"),
):
    """Get the global leaderboard sorted by XP with pagination."""
    offset = (page - 1) * size

    # Total user count for pagination (excluding admins)
    total_result = await db.execute(
        select(func.count(User.id)).where(User.is_active, User.is_admin.is_(False))
    )
    total = total_result.scalar() or 0
    pages = max(1, (total + size - 1) // size)

    # Get users ordered by XP (excluding admins)
    users_result = await db.execute(
        select(User)
        .where(User.is_active, User.is_admin.is_(False))
        .order_by(desc(User.xp), User.created_at)
        .offset(offset)
        .limit(size)
    )
    users = users_result.scalars().all()

    items = []
    for idx, user in enumerate(users):
        position = offset + idx + 1
        rank = calculate_rank(user.xp)

        # Count tasks
        tasks_result = await db.execute(
            select(func.count(TaskSubmission.id)).where(TaskSubmission.user_id == user.id)
        )
        tasks_completed = tasks_result.scalar() or 0

        # Count badges
        badges_result = await db.execute(
            select(func.count(UserBadge.id)).where(UserBadge.user_id == user.id)
        )
        badges_count = badges_result.scalar() or 0

        items.append(
            {
                "position": position,
                "user": {
                    "id": str(user.id),
                    "username": user.username,
                    "avatar_url": user.avatar_url,
                },
                "rank": rank,
                "xp": user.xp,
                "tasks_completed": tasks_completed,
                "badges_count": badges_count,
            }
        )

    # Find current user's rank
    rank_result = await db.execute(
        select(func.count(User.id)).where(User.is_active, User.xp > current_user.xp)
    )
    current_rank = (rank_result.scalar() or 0) + 1

    # Current user's task count
    my_tasks_result = await db.execute(
        select(func.count(TaskSubmission.id)).where(TaskSubmission.user_id == current_user.id)
    )
    my_tasks = my_tasks_result.scalar() or 0

    return {
        "items": items,
        "total": total,
        "page": page,
        "pages": pages,
        "current_user_rank": {
            "rank": current_rank,
            "total_xp": current_user.xp,
            "tasks_completed": my_tasks,
        },
    }
