"""Authentication routes: register, login, refresh, logout, me."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, get_user_id_from_token
from app.models.user import User
from app.models.badge import UserBadge
from app.models.submission import TaskSubmission
from app.models.learning_path import PathEnrollment
from app.schemas.user import (
    UserRegister, UserLogin, TokenRefresh, UserUpdate,
    UserResponse, AuthResponse, RegisterResponse, MeResponse, RankInfo,
)
from app.services.xp_service import calculate_rank

router = APIRouter()


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: UserRegister,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Register a new user account."""
    # Check if username or email already exists
    existing = await db.execute(
        select(User).where(
            or_(User.username == data.username, User.email == data.email)
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already registered",
        )

    user = User(
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password),
        skill_level=data.skill_level,
        background=data.background,
    )
    db.add(user)
    await db.flush()

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    rank = calculate_rank(user.xp)

    # Suggest learning path for beginners
    suggested_path = None
    welcome_message = f"Welcome to CereForge, {user.username}! 🚀"
    if data.skill_level == "absolute_beginner":
        suggested_path = "zero-to-ai-path"
        welcome_message = f"Welcome to CereForge, {user.username}! 🚀 We've recommended the Zero to AI learning path based on your background. Start there — it's built for exactly where you are."
    elif data.skill_level == "some_python":
        suggested_path = "zero-to-ai-path"
        welcome_message = f"Welcome to CereForge, {user.username}! 🐍 Your Python skills are a great foundation. Check out the Zero to AI path to start your AI engineering journey."
    elif data.skill_level == "ml_familiar":
        welcome_message = f"Welcome to CereForge, {user.username}! 🧪 Great that you have ML experience. Dive into our intermediate and expert tasks to level up your AI engineering skills."
    elif data.skill_level == "advanced":
        welcome_message = f"Welcome to CereForge, {user.username}! ⚡ Expert detected. Go straight to the expert-level tasks and show the community what you've got."

    await db.commit()

    return RegisterResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
        rank=RankInfo(
            name=rank["name"],
            color=rank["color"],
            next_rank=rank["next_rank"],
            xp_needed=rank["xp_needed"],
        ),
        suggested_path=suggested_path,
        welcome_message=welcome_message,
    )


@router.post("/login", response_model=AuthResponse)
async def login(
    data: UserLogin,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Log in with email/username and password."""
    result = await db.execute(
        select(User).where(
            or_(User.email == data.email_or_username, User.username == data.email_or_username)
        )
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    rank = calculate_rank(user.xp)

    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
        rank=RankInfo(
            name=rank["name"],
            color=rank["color"],
            next_rank=rank["next_rank"],
            xp_needed=rank["xp_needed"],
        ),
    )


@router.post("/refresh")
async def refresh_token(
    data: TokenRefresh,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Refresh access token using a valid refresh token."""
    user_id_str = get_user_id_from_token(data.refresh_token, token_type="refresh")
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    from uuid import UUID
    result = await db.execute(select(User).where(User.id == UUID(user_id_str)))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    new_access_token = create_access_token(user.id)
    return {"access_token": new_access_token, "token_type": "bearer"}


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Log out (client should discard tokens)."""
    return None


@router.get("/me", response_model=MeResponse)
async def get_me(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get current user's full profile with rank, badges, enrolled paths, and stats."""
    rank = calculate_rank(current_user.xp)

    # Get badges
    badges_result = await db.execute(
        select(UserBadge).where(UserBadge.user_id == current_user.id)
    )
    user_badges = badges_result.scalars().all()
    badges_data = [
        {
            "slug": ub.badge.slug,
            "name": ub.badge.name,
            "icon": ub.badge.icon,
            "earned_at": ub.earned_at.isoformat() if ub.earned_at else None,
        }
        for ub in user_badges
    ]

    # Get enrolled paths
    enrollments_result = await db.execute(
        select(PathEnrollment).where(PathEnrollment.user_id == current_user.id)
    )
    enrollments = enrollments_result.scalars().all()
    paths_data = [
        {
            "slug": e.path.slug,
            "title": e.path.title,
            "enrolled_at": e.enrolled_at.isoformat() if e.enrolled_at else None,
        }
        for e in enrollments
    ]

    # Get stats
    submissions_result = await db.execute(
        select(TaskSubmission).where(TaskSubmission.user_id == current_user.id)
    )
    submissions = submissions_result.scalars().all()

    stats = {
        "tasks_completed": len(submissions),
        "total_tasks": 12,
        "badges_earned": len(user_badges),
        "total_badges": 12,
        "xp": current_user.xp,
    }

    return MeResponse(
        user=UserResponse.model_validate(current_user),
        rank=RankInfo(
            name=rank["name"],
            color=rank["color"],
            next_rank=rank["next_rank"],
            xp_needed=rank["xp_needed"],
        ),
        badges=badges_data,
        enrolled_paths=paths_data,
        stats=stats,
    )


@router.patch("/me", response_model=dict)
async def update_me(
    data: UserUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update current user's profile."""
    if data.username is not None:
        # Check uniqueness
        existing = await db.execute(
            select(User).where(User.username == data.username, User.id != current_user.id)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already taken")
        current_user.username = data.username

    if data.skill_level is not None:
        current_user.skill_level = data.skill_level
    if data.background is not None:
        current_user.background = data.background
    if data.avatar_url is not None:
        current_user.avatar_url = data.avatar_url

    await db.flush()
    await db.commit()

    return {"user": UserResponse.model_validate(current_user).model_dump()}
