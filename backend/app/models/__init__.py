from __future__ import annotations

from app.models.badge import Badge, UserBadge
from app.models.comment import Comment, Vote
from app.models.learning_path import LearningPath, PathEnrollment, PathLesson, PathModule
from app.models.notification import Notification
from app.models.otp import PasswordResetOTP
from app.models.post import Post
from app.models.submission import TaskSubmission
from app.models.task import Task, TaskResource
from app.models.user import User

# This ensures all models are known to SQLAlchemy's registry before they are used
# in relationships or by Alembic for autogenerating migrations.
__all__ = [
    "User",
    "Task",
    "TaskResource",
    "TaskSubmission",
    "Badge",
    "UserBadge",
    "Post",
    "Comment",
    "Vote",
    "LearningPath",
    "PathModule",
    "PathLesson",
    "PathEnrollment",
    "Notification",
    "PasswordResetOTP",
]
