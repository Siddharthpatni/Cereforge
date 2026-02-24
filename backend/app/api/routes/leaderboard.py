"""Leaderboard routes."""

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.submission import TaskSubmission
from app.models.badge import UserBadge
from app.services.xp_service import calculate_rank

router = APIRouter()


@router.get("")
async def get_leaderboard(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
):
    """Get the global leaderboard sorted by XP."""
    offset = (page - 1) * limit

    # Get users ordered by XP
    users_result = await db.execute(
        select(User)
        .where(User.is_active == True)
        .order_by(desc(User.xp), User.created_at)
        .offset(offset)
        .limit(limit)
    )
    users = users_result.scalars().all()

    items = []
    for idx, user in enumerate(users):
        position = offset + idx + 1
        rank = calculate_rank(user.xp)

        # Count tasks
        tasks_result = await db.execute(
            select(func.count(TaskSubmission.id))
            .where(TaskSubmission.user_id == user.id)
        )
        tasks_completed = tasks_result.scalar() or 0

        # Count and get badges
        badges_result = await db.execute(
            select(UserBadge).where(UserBadge.user_id == user.id)
        )
        user_badges = badges_result.scalars().all()
        top_badges = [ub.badge.icon for ub in user_badges[:3]] if user_badges else []

        items.append({
            "position": position,
            "user": {
                "id": str(user.id),
                "username": user.username,
                "avatar_url": user.avatar_url,
            },
            "rank": rank,
            "xp": user.xp,
            "tasks_completed": tasks_completed,
            "badges_count": len(user_badges),
            "top_badges": top_badges,
        })

    # Find current user's position
    current_position = None
    rank_result = await db.execute(
        select(func.count(User.id))
        .where(User.is_active == True, User.xp > current_user.xp)
    )
    current_position = (rank_result.scalar() or 0) + 1

    return {
        "items": items,
        "current_user_position": current_position,
    }
