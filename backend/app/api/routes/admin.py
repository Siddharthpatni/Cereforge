"""Admin routes for portal."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user, get_db
from app.core.security import hash_password
from app.models.post import Post
from app.models.submission import TaskSubmission
from app.models.user import User
from app.schemas.user import AdminXPUpdate
from app.services.xp_service import calculate_rank

router = APIRouter()


async def require_admin(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required"
        )
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

    flagged_result = await db.execute(
        select(func.count(TaskSubmission.id)).where(TaskSubmission.is_ai_flagged.is_(True))
    )
    total_flagged = flagged_result.scalar() or 0

    active_posts_result = await db.execute(
        select(func.count(Post.id)).where(Post.is_deleted.is_(False))
    )
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
    """Retrieve all users with sensitive data for admin view."""
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    users = result.scalars().all()

    return [
        {
            "id": str(u.id),
            "username": u.username,
            "email": u.email,
            "password_hash": u.password_hash,
            "xp": u.xp,
            "rank": calculate_rank(u.xp)["name"],
            "created_at": u.created_at.isoformat(),
            "is_admin": u.is_admin,
        }
        for u in users
    ]


@router.patch("/users/{user_id}/xp")
async def update_user_xp(
    user_id: str,
    data: AdminXPUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    admin_user: Annotated[User, Depends(require_admin)],
):
    """Manually update a user's XP."""
    try:
        u_id = uuid.UUID(user_id)
    except ValueError as err:
        raise HTTPException(status_code=400, detail="Invalid user ID format") from err

    result = await db.execute(select(User).where(User.id == u_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.xp = data.xp
    await db.commit()

    return {"message": f"XP for {user.username} updated to {user.xp}", "new_xp": user.xp}


class AdminStatusUpdate(BaseModel):
    is_active: bool


@router.patch("/users/{user_id}/status")
async def update_user_status(
    user_id: str,
    data: AdminStatusUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    admin_user: Annotated[User, Depends(require_admin)],
):
    """Ban or unban a user account."""
    try:
        u_id = uuid.UUID(user_id)
    except ValueError as err:
        raise HTTPException(status_code=400, detail="Invalid user ID format") from err

    result = await db.execute(select(User).where(User.id == u_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.is_admin:
        raise HTTPException(status_code=400, detail="Cannot ban an admin account")

    user.is_active = data.is_active
    await db.commit()
    action = "unbanned" if data.is_active else "banned"
    return {"message": f"User {user.username} has been {action}", "is_active": user.is_active}


class AdminPasswordReset(BaseModel):
    new_password: str = Field(..., min_length=8)


@router.patch("/users/{user_id}/password")
async def admin_reset_user_password(
    user_id: str,
    data: AdminPasswordReset,
    db: Annotated[AsyncSession, Depends(get_db)],
    admin_user: Annotated[User, Depends(require_admin)],
):
    """Force-reset any user's password."""
    try:
        u_id = uuid.UUID(user_id)
    except ValueError as err:
        raise HTTPException(status_code=400, detail="Invalid user ID format") from err

    result = await db.execute(select(User).where(User.id == u_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.password_hash = hash_password(data.new_password)
    await db.commit()
    return {"message": f"Password reset for {user.username}"}


@router.delete("/posts/{post_id}", status_code=204)
async def admin_delete_post(
    post_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    admin_user: Annotated[User, Depends(require_admin)],
):
    """Soft-delete any community post."""
    try:
        p_id = uuid.UUID(post_id)
    except ValueError as err:
        raise HTTPException(status_code=400, detail="Invalid post ID format") from err

    result = await db.execute(select(Post).where(Post.id == p_id))
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    post.is_deleted = True
    await db.commit()


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
