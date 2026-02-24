"""Learning path routes: list, detail, enroll."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.learning_path import LearningPath, PathEnrollment
from app.models.submission import TaskSubmission
from app.models.task import Task
from app.models.user import User
from app.schemas.common import (
    EnrollResponse,
    LearningPathResponse,
    LessonResponse,
    ModuleResponse,
    PathDetailResponse,
)

router = APIRouter()


@router.get("", response_model=list[LearningPathResponse])
async def list_learning_paths(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """List all learning paths with enrollment status and progress."""
    paths_result = await db.execute(
        select(LearningPath).where(LearningPath.is_active).order_by(LearningPath.display_order)
    )
    paths = paths_result.scalars().all()

    # Get user enrollments
    enrollments_result = await db.execute(
        select(PathEnrollment.path_id).where(PathEnrollment.user_id == current_user.id)
    )
    enrolled_ids = set(enrollments_result.scalars().all())

    # Get user completions
    subs_result = await db.execute(
        select(TaskSubmission.task_id).where(TaskSubmission.user_id == current_user.id)
    )
    completed_task_ids = set(subs_result.scalars().all())

    items = []
    for path in paths:
        enrolled = path.id in enrolled_ids
        recommended = current_user.skill_level in (path.for_skill_levels or [])

        # Calculate progress
        total_tasks = len(path.task_sequence) if path.task_sequence else 0
        completed_count = sum(1 for tid in (path.task_sequence or []) if tid in completed_task_ids)
        progress = (completed_count / total_tasks * 100) if total_tasks > 0 else 0

        items.append(
            LearningPathResponse(
                id=path.id,
                slug=path.slug,
                title=path.title,
                description=path.description,
                for_skill_levels=path.for_skill_levels or [],
                duration_days=path.duration_days,
                task_sequence=path.task_sequence or [],
                display_order=path.display_order,
                enrolled=enrolled,
                recommended=recommended,
                progress=round(progress, 1),
            )
        )

    return items


@router.get("/{slug}", response_model=PathDetailResponse)
async def get_learning_path(
    slug: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Get a learning path with modules, lessons, and progress."""
    result = await db.execute(
        select(LearningPath).where(LearningPath.slug == slug, LearningPath.is_active)
    )
    path = result.scalar_one_or_none()
    if not path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learning path not found")

    # Enrollment check
    enrollment_result = await db.execute(
        select(PathEnrollment).where(
            PathEnrollment.user_id == current_user.id,
            PathEnrollment.path_id == path.id,
        )
    )
    enrolled = enrollment_result.scalar_one_or_none() is not None

    # User completions
    subs_result = await db.execute(
        select(TaskSubmission.task_id).where(TaskSubmission.user_id == current_user.id)
    )
    completed_task_ids = set(subs_result.scalars().all())

    # Calculate progress
    total_tasks = len(path.task_sequence) if path.task_sequence else 0
    completed_count = sum(1 for tid in (path.task_sequence or []) if tid in completed_task_ids)
    progress = (completed_count / total_tasks * 100) if total_tasks > 0 else 0

    # Find next task
    next_task = None
    for tid in path.task_sequence or []:
        if tid not in completed_task_ids:
            task_result = await db.execute(select(Task.slug).where(Task.id == tid))
            task_slug = task_result.scalar_one_or_none()
            if task_slug:
                next_task = task_slug
            break

    # Build modules/lessons
    modules_data = [
        ModuleResponse(
            id=m.id,
            title=m.title,
            display_order=m.display_order,
            lessons=[LessonResponse.model_validate(lesson) for lesson in m.lessons],
        )
        for m in (path.modules or [])
    ]

    return PathDetailResponse(
        id=path.id,
        slug=path.slug,
        title=path.title,
        description=path.description,
        for_skill_levels=path.for_skill_levels or [],
        duration_days=path.duration_days,
        task_sequence=path.task_sequence or [],
        display_order=path.display_order,
        modules=modules_data,
        enrolled=enrolled,
        progress=round(progress, 1),
        next_task=next_task,
    )


@router.post("/{slug}/enroll", response_model=EnrollResponse)
async def enroll_in_path(
    slug: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Enroll in a learning path."""
    result = await db.execute(
        select(LearningPath).where(LearningPath.slug == slug, LearningPath.is_active)
    )
    path = result.scalar_one_or_none()
    if not path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learning path not found")

    # Check existing enrollment
    existing = await db.execute(
        select(PathEnrollment).where(
            PathEnrollment.user_id == current_user.id,
            PathEnrollment.path_id == path.id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already enrolled")

    enrollment = PathEnrollment(user_id=current_user.id, path_id=path.id)
    db.add(enrollment)

    # Find first task slug
    next_task_slug = None
    if path.task_sequence:
        task_result = await db.execute(select(Task.slug).where(Task.id == path.task_sequence[0]))
        next_task_slug = task_result.scalar_one_or_none()

    await db.flush()
    await db.commit()

    return EnrollResponse(enrolled=True, next_task_slug=next_task_slug)
