"""Badge condition checking and awarding engine."""

from typing import Any, cast
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.badge import Badge, UserBadge
from app.models.comment import Comment
from app.models.notification import Notification
from app.models.submission import TaskSubmission
from app.models.task import Task
from app.models.user import User
from app.services.xp_service import award_xp

# Track color mapping for badge unlock cinematic
TRACK_COLORS = {
    "llm": "#00f5ff",
    "rag": "#9d4edd",
    "vision": "#00ff88",
    "agents": "#ffaa00",
}


async def check_and_award_badges(
    db: AsyncSession,
    user_id: UUID,
) -> list[dict]:
    """Check all badge conditions for a user and award any newly earned badges.

    Returns list of newly earned badge dicts (for API response).
    """
    # Fetch user
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        return []

    # Fetch all badges
    badges_result = await db.execute(select(Badge).order_by(Badge.display_order))
    all_badges = badges_result.scalars().all()

    # Fetch user's existing badges
    existing_result = await db.execute(
        select(UserBadge.badge_id).where(UserBadge.user_id == user_id)
    )
    existing_badge_ids = set(existing_result.scalars().all())

    # Fetch user's completions by track
    completions_result = await db.execute(
        select(Task.track, func.count(TaskSubmission.id))
        .join(Task, TaskSubmission.task_id == Task.id)
        .where(TaskSubmission.user_id == user_id)
        .group_by(Task.track)
    )
    track_counts: dict[str, int] = {row[0]: row[1] for row in completions_result.all()}

    # Total completions
    total_completions = sum(track_counts.values())

    # Count accepted answers
    accepted_result = await db.execute(
        select(func.count(Comment.id))
        .where(Comment.author_id == user_id, Comment.is_accepted)
    )
    accepted_answers = accepted_result.scalar() or 0

    newly_earned = []

    for badge in all_badges:
        # Skip if already earned
        if badge.id in existing_badge_ids:
            continue

        # Check condition
        earned = _check_badge_condition(
            badge=badge,
            track_counts=track_counts,
            total_completions=total_completions,
            accepted_answers=accepted_answers,
            user_skill_level=user.skill_level,
        )

        if earned:
            # Award badge
            user_badge = UserBadge(user_id=user_id, badge_id=badge.id)
            db.add(user_badge)

            # Award XP bonus
            await award_xp(db, user_id, badge.xp_bonus)

            # Create notification
            notification = Notification(
                user_id=user_id,
                type="badge_earned",
                title=f"Badge Unlocked: {badge.name}!",
                body=badge.description,
                metadata_={"badge_id": str(badge.id), "badge_slug": badge.slug},
            )
            db.add(notification)

            # Determine track color for cinematic
            track_color = _get_badge_track_color(badge)

            newly_earned.append({
                "slug": badge.slug,
                "name": badge.name,
                "icon": badge.icon,
                "description": badge.description,
                "xp_bonus": badge.xp_bonus,
                "track_color": track_color,
            })

    if newly_earned:
        await db.flush()

    return newly_earned


def _check_badge_condition(
    badge: Badge,
    track_counts: dict[str, int],
    total_completions: int,
    accepted_answers: int,
    user_skill_level: str,
) -> bool:
    """Evaluate a single badge's condition."""
    ctype = badge.condition_type
    cval = cast(dict[str, Any], badge.condition_value or {})

    if ctype == "track_count":
        track = str(cval.get("track", ""))
        count = int(cval.get("count", 0))
        return track_counts.get(track, 0) >= count

    elif ctype == "all_tracks":
        required_tracks = {"llm", "rag", "vision", "agents"}
        return all(track_counts.get(t, 0) >= 1 for t in required_tracks)

    elif ctype == "total_tasks":
        return total_completions >= cval.get("total_tasks", 0)

    elif ctype == "accepted_answers":
        return accepted_answers >= cval.get("count", 0)

    elif ctype == "skill_and_tasks":
        required_skill = cval.get("skill_level")
        required_tasks = cval.get("tasks_completed", 0)
        return user_skill_level == required_skill and total_completions >= required_tasks

    return False


def _get_badge_track_color(badge: Badge) -> str | None:
    """Determine the track color for a badge's unlock cinematic."""
    ctype = badge.condition_type
    cval = cast(dict[str, Any], badge.condition_value or {})

    if ctype == "track_count":
        track = str(cval.get("track", ""))
        return TRACK_COLORS.get(track, "#00f5ff")
    elif ctype == "all_tracks":
        return "#ffffff"
    elif ctype == "total_tasks":
        return "#ffd700"
    elif ctype == "accepted_answers":
        return "#9d4edd"
    elif ctype == "skill_and_tasks":
        return "#00f5ff"
    return "#00f5ff"
