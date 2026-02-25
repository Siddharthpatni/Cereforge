"""Badge routes: list all badges with earned status."""

from __future__ import annotations


from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.badge import Badge, UserBadge
from app.models.user import User
from app.schemas.common import BadgeResponse

router = APIRouter()


@router.get("", response_model=list[BadgeResponse])
async def list_badges(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """List all badges with earned status for the current user."""
    badges_result = await db.execute(select(Badge).order_by(Badge.display_order))
    all_badges = badges_result.scalars().all()

    earned_result = await db.execute(select(UserBadge).where(UserBadge.user_id == current_user.id))
    earned_badges = {ub.badge_id: ub for ub in earned_result.scalars().all()}

    items = []
    for badge in all_badges:
        ub = earned_badges.get(badge.id)
        items.append(
            BadgeResponse(
                id=badge.id,
                slug=badge.slug,
                name=badge.name,
                icon=badge.icon,
                description=badge.description,
                condition_type=badge.condition_type,
                xp_bonus=badge.xp_bonus,
                display_order=badge.display_order,
                earned=ub is not None,
                earned_at=ub.earned_at if ub else None,
            )
        )

    return items
