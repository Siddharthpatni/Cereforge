"""Admin routes for portal."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user, get_db
from app.models.post import Post
from app.models.submission import TaskSubmission
from app.models.user import User

router = APIRouter()

async def require_admin(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    return current_user


@router.get("/stats")
async def get_admin_stats(
    db: Annotated[AsyncSession, Depends(get_db)],
    admin_user: Annotated[User, Depends(require_admin)],
):
    """Get high-level statistics for the admin dashboard."""
    total_users_result = await db.execute(select(func.count(User.id)))
    total_users = total_users_result.scalar() or 0

    total_submissions_result = await db.execute(select(func.count(TaskSubmission.id)))
    total_submissions = total_submissions_result.scalar() or 0

    flagged_result = await db.execute(select(func.count(TaskSubmission.id)).where(TaskSubmission.is_ai_flagged.is_(True)))
    total_flagged = flagged_result.scalar() or 0

    active_posts_result = await db.execute(select(func.count(Post.id)).where(Post.is_deleted.is_(False)))
    total_active_posts = active_posts_result.scalar() or 0

    return {
        "total_users": total_users,
        "total_submissions": total_submissions,
        "total_flagged": total_flagged,
        "total_active_posts": total_active_posts,
    }

@router.get("/submissions")
async def get_recent_submissions(
    db: Annotated[AsyncSession, Depends(get_db)],
    admin_user: Annotated[User, Depends(require_admin)],
):
    """Retrieve 50 most recent submissions."""
    result = await db.execute(
        select(TaskSubmission)
        .options(selectinload(TaskSubmission.user), selectinload(TaskSubmission.task))
        .order_by(TaskSubmission.submitted_at.desc())
        .limit(50)
    )
    submissions = result.scalars().all()
    
    return [
        {
            "id": str(sub.id),
            "username": sub.user.username if sub.user else "Unknown",
            "task_title": sub.task.title if sub.task else "Unknown",
            "is_ai_flagged": sub.is_ai_flagged,
            "ai_flag_score": sub.ai_flag_score,
            "submitted_at": sub.submitted_at.isoformat(),
        }
        for sub in submissions
    ]

@router.get("/users")
async def get_all_users(
    db: Annotated[AsyncSession, Depends(get_db)],
    admin_user: Annotated[User, Depends(require_admin)],
):
    """Retrieve all users."""
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    users = result.scalars().all()
    
    from app.services.xp_service import calculate_rank
    
    return [
        {
            "id": str(u.id),
            "username": u.username,
            "email": u.email,
            "xp": u.xp,
            "rank": calculate_rank(u.xp)["name"],
            "created_at": u.created_at.isoformat(),
            "is_admin": u.is_admin
        }
        for u in users
    ]

@router.get("/ai-flagged")
async def get_ai_flagged(
    db: Annotated[AsyncSession, Depends(get_db)],
    admin_user: Annotated[User, Depends(require_admin)],
):
    """Retrieve only AI-flagged submissions."""
    result = await db.execute(
        select(TaskSubmission)
        .options(selectinload(TaskSubmission.user), selectinload(TaskSubmission.task))
        .where(TaskSubmission.is_ai_flagged.is_(True))
        .order_by(TaskSubmission.ai_flag_score.desc())
    )
    submissions = result.scalars().all()
    
    return [
        {
            "id": str(sub.id),
            "username": sub.user.username if sub.user else "Unknown",
            "task_title": sub.task.title if sub.task else "Unknown",
            "ai_flag_score": sub.ai_flag_score,
            "ai_flag_reason": sub.ai_flag_reason,
            "submitted_at": sub.submitted_at.isoformat(),
            "solution_text": sub.solution_text,
        }
        for sub in submissions
    ]
