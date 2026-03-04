"""Authentication routes: register, login, refresh, logout, me."""

from __future__ import annotations

import random
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_user_id_from_token,
    hash_password,
    verify_password,
)
from app.models.otp import PasswordResetOTP
from app.models.user import User
from app.schemas.user import (
    AuthResponse,
    ForgotPasswordRequest,
    RankInfo,
    RegisterResponse,
    ResetPasswordRequest,
    TokenRefresh,
    UserLogin,
    UserRegister,
    UserResponse,
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
        select(User).where(or_(User.username == data.username, User.email == data.email))
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
    await db.commit()
    await db.refresh(user)

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


@router.post("/forgot-password")
async def forgot_password(
    data: ForgotPasswordRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Generate and 'send' OTP for password reset."""
    # Check if user exists
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user:
        # For security, we still return 200 even if user doesn't exist
        # to avoid email enumeration.
        return {"message": "If this email is registered, an OTP has been sent."}

    # Generate 6-digit OTP
    otp_code = "".join([str(random.randint(0, 9)) for _ in range(6)])

    # Save OTP to DB
    otp_record = PasswordResetOTP(email=data.email, otp_code=otp_code)
    db.add(otp_record)
    await db.commit()

    # MOCK EMAIL SENDING
    logger.warning("--- [MOCK EMAIL] ---")
    logger.warning(f"TO: {data.email}")
    logger.warning("SUBJECT: CereForge Password Reset OTP")
    logger.warning(f"OTP CODE: {otp_code}")
    logger.warning("---------------------")

    return {"message": "OTP sent successfully to your registered email."}


@router.post("/reset-password")
async def reset_password(
    data: ResetPasswordRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Verify OTP and update user's password."""
    from datetime import datetime, timezone

    # Find the most recent valid OTP
    result = await db.execute(
        select(PasswordResetOTP)
        .where(
            PasswordResetOTP.email == data.email,
            PasswordResetOTP.otp_code == data.otp_code,
            PasswordResetOTP.is_used is False,
            PasswordResetOTP.expires_at > datetime.now(timezone.utc),
        )
        .order_by(PasswordResetOTP.created_at.desc())
    )
    otp_record = result.scalars().first()

    if not otp_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired OTP code."
        )

    # Find user
    user_result = await db.execute(select(User).where(User.email == data.email))
    user = user_result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    # Update password
    user.password_hash = hash_password(data.new_password)

    # Mark OTP as used
    otp_record.is_used = True

    await db.commit()

    return {"message": "Password has been reset successfully. You can now log in."}
