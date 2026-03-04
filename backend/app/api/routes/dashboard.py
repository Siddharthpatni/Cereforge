from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.badge import Badge, UserBadge
from app.models.learning_path import PathEnrollment
from app.models.notification import Notification
from app.models.submission import TaskSubmission
from app.models.task import Task
from app.models.user import User
from app.services.xp_service import calculate_rank

router = APIRouter()


@router.get("")
async def get_dashboard(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Get dashboard data: stats, rank, featured task, badges, activity feed."""
    rank = calculate_rank(current_user.xp)

    # Task completions
    subs_result = await db.execute(
        select(TaskSubmission).where(TaskSubmission.user_id == current_user.id)
    )
    submissions = subs_result.scalars().all()
    completed_task_ids = {s.task_id for s in submissions}

    # Badge data
    all_badges_result = await db.execute(select(Badge).order_by(Badge.display_order))
    all_badges = all_badges_result.scalars().all()

    earned_result = await db.execute(select(UserBadge).where(UserBadge.user_id == current_user.id))
    earned_badges = {ub.badge_id: ub for ub in earned_result.scalars().all()}

    badges_data = [
        {
            "slug": b.slug,
            "name": b.name,
            "icon": b.icon,
            "description": b.description,
            "xp_bonus": b.xp_bonus,
            "earned": b.id in earned_badges,
            "earned_at": earned_badges[b.id].earned_at.isoformat()
            if b.id in earned_badges
            else None,
        }
        for b in all_badges
    ]

    # Stats
    stats = {
        "xp": current_user.xp,
        "tasks_completed": len(submissions),
        "total_tasks": 24,
        "badges_earned": len(earned_badges),
        "total_badges": 12,
    }

    # Featured / next task
    next_task = None
    all_tasks_result = await db.execute(
        select(Task).where(Task.is_active).order_by(Task.display_order)
    )
    for task in all_tasks_result.scalars().all():
        if task.id not in completed_task_ids:
            next_task = {
                "slug": task.slug,
                "title": task.title,
                "track": task.track,
                "difficulty": task.difficulty,
                "xp_reward": task.xp_reward,
                "description": task.description[:200],
            }
            break

    # Recent completions
    recent = sorted(submissions, key=lambda s: s.submitted_at, reverse=True)[:5]
    recent_completions = []
    for sub in recent:
        task_result = await db.execute(select(Task).where(Task.id == sub.task_id))
        t = task_result.scalar_one_or_none()
        if t:
            recent_completions.append(
                {
                    "task_slug": t.slug,
                    "task_title": t.title,
                    "track": t.track,
                    "xp_earned": sub.xp_awarded,
                    "submitted_at": sub.submitted_at.isoformat(),
                }
            )

    # Enrolled paths
    enrollments_result = await db.execute(
        select(PathEnrollment).where(PathEnrollment.user_id == current_user.id)
    )
    enrollments = enrollments_result.scalars().all()
    enrolled_paths = []
    for e in enrollments:
        path = e.path
        total_tasks = len(path.task_sequence) if path.task_sequence else 0
        completed_count = sum(1 for tid in (path.task_sequence or []) if tid in completed_task_ids)
        enrolled_paths.append(
            {
                "slug": path.slug,
                "title": path.title,
                "total_tasks": total_tasks,
                "completed_tasks": completed_count,
                "progress": round(completed_count / total_tasks * 100, 1) if total_tasks > 0 else 0,
            }
        )

    # Activity feed (recent notifications)
    activity_result = await db.execute(
        select(Notification)
        .where(Notification.user_id == current_user.id)
        .order_by(desc(Notification.created_at))
        .limit(10)
    )
    activity_feed = [
        {
            "type": n.type,
            "title": n.title,
            "body": n.body,
            "created_at": n.created_at.isoformat(),
            "metadata": n.metadata_,
        }
        for n in activity_result.scalars().all()
    ]

    return {
        "stats": stats,
        "rank": rank,
        "next_task": next_task,
        "recent_completions": recent_completions,
        "badges": badges_data,
        "enrolled_paths": enrolled_paths,
        "activity_feed": activity_feed,
    }


@router.get("/notifications")
async def get_notifications(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    unread_only: bool = False,
):
    """Get user notifications."""
    query = select(Notification).where(Notification.user_id == current_user.id)
    if unread_only:
        query = query.where(Notification.is_read.is_(False))
    query = query.order_by(desc(Notification.created_at)).limit(50)

    result = await db.execute(query)
    notifications = result.scalars().all()

    return [
        {
            "id": str(n.id),
            "type": n.type,
            "title": n.title,
            "body": n.body,
            "is_read": n.is_read,
            "metadata": n.metadata_,
            "created_at": n.created_at.isoformat(),
        }
        for n in notifications
    ]


@router.post("/notifications/mark-read", status_code=204)
async def mark_notifications_read(
    data: dict,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Mark notifications as read."""
    import uuid

    ids = [uuid.UUID(id_str) for id_str in data.get("ids", [])]

    if ids:
        result = await db.execute(
            select(Notification).where(
                Notification.id.in_(ids),
                Notification.user_id == current_user.id,
            )
        )
        for n in result.scalars().all():
            n.is_read = True
        await db.flush()
        await db.commit()

    return None
