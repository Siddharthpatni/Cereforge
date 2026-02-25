"""XP calculation and rank determination service."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User

# Rank definitions: (name, min_xp, color, border_style)
RANKS: list[dict[str, Any]] = [
    {"name": "Trainee", "min_xp": 0, "color": "#6b7280", "border": "solid gray"},
    {"name": "Engineer", "min_xp": 200, "color": "#3b82f6", "border": "solid blue"},
    {"name": "Architect", "min_xp": 500, "color": "#8b5cf6", "border": "solid purple"},
    {"name": "Autonomous", "min_xp": 1000, "color": "#f59e0b", "border": "solid gold"},
    {
        "name": "CereForge Elite",
        "min_xp": 1800,
        "color": "#ffffff",
        "border": "animated rainbow gradient",
    },
]

# XP award amounts
XP_TASK_COMPLETION = None  # Uses task.xp_reward
XP_BADGE_EARNED = None  # Uses badge.xp_bonus
XP_ANSWER_POSTED = 5
XP_ANSWER_ACCEPTED = 50
XP_POST_UPVOTED = 2
XP_COMMENT_UPVOTED = 2


def calculate_rank(xp: int) -> dict:
    """Calculate rank from XP, returning rank info with next rank details."""
    current_rank = RANKS[0]
    for rank in RANKS:
        if xp >= rank["min_xp"]:
            current_rank = rank
        else:
            break

    current_idx = RANKS.index(current_rank)
    next_rank = RANKS[current_idx + 1] if current_idx < len(RANKS) - 1 else None

    return {
        "name": current_rank["name"],
        "color": current_rank["color"],
        "border": current_rank["border"],
        "min_xp": current_rank["min_xp"],
        "next_rank": next_rank["name"] if next_rank else None,
        "xp_needed": (next_rank["min_xp"] - xp) if next_rank else None,
        "next_rank_xp": next_rank["min_xp"] if next_rank else None,
    }


async def award_xp(db: AsyncSession, user_id: UUID, amount: int) -> int:
    """Award XP to a user, returns new total."""
    result = await db.execute(
        update(User).where(User.id == user_id).values(xp=User.xp + amount).returning(User.xp)
    )
    new_xp = result.scalar_one()
    return new_xp
