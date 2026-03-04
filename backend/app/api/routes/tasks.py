"""Task routes: list, detail, submit, get submission."""

from __future__ import annotations

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.post import Post
from app.models.submission import TaskSubmission
from app.models.task import Task
from app.models.user import User
from app.schemas.task import (
    BadgeEarned,
    Benchmarks,
    SubmissionDetailResponse,
    TaskListItem,
    TaskResponse,
    TaskSubmissionCreate,
    TaskSubmissionResponse,
)
from app.services.ai_detector import analyze_submission
from app.services.badge_engine import check_and_award_badges
from app.services.task_evaluator import evaluate_submission
from app.services.xp_service import award_xp, calculate_rank

router = APIRouter()


@router.get("", response_model=list[TaskListItem])
async def list_tasks(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    track: str | None = Query(None),
    difficulty: str | None = Query(None),
    task_status: str | None = Query(None, alias="status"),
    is_weekly: bool | None = Query(None),
):
    """List all tasks with optional filters."""
    query = select(Task).where(Task.is_active).order_by(Task.track, Task.display_order)

    if track:
        query = query.where(Task.track == track)
    if difficulty:
        query = query.where(Task.difficulty == difficulty)
    if is_weekly is not None:
        query = query.where(Task.is_weekly == is_weekly)

    result = await db.execute(query)
    tasks = result.scalars().all()

    # Get user's completed task IDs
    subs_result = await db.execute(
        select(TaskSubmission.task_id).where(TaskSubmission.user_id == current_user.id)
    )
    completed_ids = set(subs_result.scalars().all())

    show_beginner = current_user.skill_level in ("absolute_beginner", "some_python")

    items = []
    for task in tasks:
        completed = task.id in completed_ids
        if task_status == "completed" and not completed:
            continue
        if task_status == "incomplete" and completed:
            continue

        items.append(
            TaskListItem(
                id=task.id,
                slug=task.slug,
                track=task.track,
                difficulty=task.difficulty,
                title=task.title,
                description=task.description,
                xp_reward=task.xp_reward,
                display_order=task.display_order,
                colab_url=task.colab_url,
                is_weekly=task.is_weekly,
                completed=completed,
                show_beginner_guide=show_beginner,
            )
        )

    return items


@router.get("/{slug}", response_model=dict)
async def get_task(
    slug: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Get a single task by slug with resources and related posts."""
    result = await db.execute(select(Task).where(Task.slug == slug, Task.is_active))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    # Check if completed
    sub_result = await db.execute(
        select(TaskSubmission).where(
            TaskSubmission.user_id == current_user.id,
            TaskSubmission.task_id == task.id,
        )
    )
    completed = sub_result.scalar_one_or_none() is not None

    show_beginner = current_user.skill_level in ("absolute_beginner", "some_python")

    # Related community posts
    posts_result = await db.execute(
        select(Post)
        .where(Post.related_task_id == task.id, Post.is_deleted.is_(False))
        .order_by(Post.vote_score.desc())
        .limit(5)
    )
    related_posts = [
        {
            "id": str(p.id),
            "title": p.title,
            "vote_score": p.vote_score,
            "status": p.status,
            "author_username": p.author.username if p.author else "unknown",
        }
        for p in posts_result.scalars().all()
    ]

    task_data = TaskResponse.model_validate(task).model_dump()
    task_data["completed"] = completed
    task_data["show_beginner_guide"] = show_beginner
    task_data["related_posts"] = related_posts

    return task_data


@router.post("/{slug}/submit", response_model=TaskSubmissionResponse)
async def submit_task(
    slug: str,
    data: TaskSubmissionCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Submit a task solution. Awards XP and checks for badge unlocks."""
    # Find task
    result = await db.execute(select(Task).where(Task.slug == slug, Task.is_active))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    # Check if already submitted
    existing = await db.execute(
        select(TaskSubmission).where(
            TaskSubmission.user_id == current_user.id,
            TaskSubmission.task_id == task.id,
        )
    )
    existing_submission = existing.scalar_one_or_none()

    # Analyze for AI detection silently
    analysis = await analyze_submission(
        solution_content=data.solution_text,
        user_skill=current_user.skill_level,
        task_difficulty=task.difficulty,
    )

    # Replaced simulated delay with real AI code evaluation for insights/benchmarks
    eval_result = await evaluate_submission(
        solution_content=data.solution_text, task_title=task.title, task_difficulty=task.difficulty
    )

    # Validation Check: Reward 0 XP if flagged as AI or failed tests
    is_invalid = analysis["is_flagged"] or eval_result["tests_passed"] < eval_result["total_tests"]
    actual_xp = 0 if is_invalid else task.xp_reward

    newly_earned = []

    if existing_submission:
        previously_earned_xp = existing_submission.xp_awarded > 0

        # Overwrite previous solution
        existing_submission.solution_text = data.solution_text
        existing_submission.colab_link = data.colab_link
        existing_submission.notes = data.notes
        existing_submission.ai_flag_score = analysis["score"]
        existing_submission.is_ai_flagged = analysis["is_flagged"]
        existing_submission.ai_flag_reason = analysis["reason"]

        if not previously_earned_xp and not is_invalid:
            # Grant retroactive XP
            existing_submission.xp_awarded = actual_xp
            await award_xp(db, current_user.id, actual_xp)
            newly_earned = await check_and_award_badges(db, current_user.id)
            celebration = f"🎉 Task complete on retry! +{actual_xp} XP"
            if newly_earned:
                badge_names = ", ".join([b["name"] for b in newly_earned])
                celebration += f" | 🏆 Badge(s) unlocked: {badge_names}!"
        elif previously_earned_xp and not is_invalid:
            celebration = "Solution updated successfully! (XP already awarded)"
        else:
            celebration = (
                "Submission updated. (0 XP: Did not pass all tests or flagged as AI generated)"
            )
    else:
        # Create new submission
        submission = TaskSubmission(
            user_id=current_user.id,
            task_id=task.id,
            solution_text=data.solution_text,
            colab_link=data.colab_link,
            notes=data.notes,
            xp_awarded=actual_xp,
            ai_flag_score=analysis["score"],
            is_ai_flagged=analysis["is_flagged"],
            ai_flag_reason=analysis["reason"],
        )
        db.add(submission)

        # Award XP and Badges (only if valid)
        if actual_xp > 0:
            await award_xp(db, current_user.id, actual_xp)
            newly_earned = await check_and_award_badges(db, current_user.id)

        if is_invalid:
            celebration = (
                "Submission Recorded. (0 XP: Did not pass all tests or flagged as AI generated)"
            )
        else:
            celebration = f"🎉 Task complete! +{actual_xp} XP"
            if newly_earned:
                badge_names = ", ".join([b["name"] for b in newly_earned])
                celebration += f" | 🏆 Badge(s) unlocked: {badge_names}!"

    # Recalculate total XP (may have changed from badge bonuses)
    await db.refresh(current_user)
    rank = calculate_rank(current_user.xp)

    await db.commit()

    return TaskSubmissionResponse(
        xp_earned=actual_xp,
        total_xp=current_user.xp,
        rank=rank,
        newly_earned_badges=[BadgeEarned(**b) for b in newly_earned],
        celebration_message=celebration,
        benchmarks=Benchmarks(**eval_result),
    )


@router.get("/{slug}/submissions", response_model=Optional[SubmissionDetailResponse])
async def get_submission(
    slug: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Get the current user's submission for a task."""
    result = await db.execute(select(Task).where(Task.slug == slug))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    sub_result = await db.execute(
        select(TaskSubmission).where(
            TaskSubmission.user_id == current_user.id,
            TaskSubmission.task_id == task.id,
        )
    )
    submission = sub_result.scalar_one_or_none()
    if not submission:
        return None

    return SubmissionDetailResponse.model_validate(submission)
