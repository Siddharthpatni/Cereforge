"""Celery background tasks."""

from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "cereforge",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


@celery_app.task
def check_badges_background(user_id: str):
    """Background task to check and award badges."""
    import asyncio
    from uuid import UUID

    from app.core.database import async_session_factory
    from app.services.badge_engine import check_and_award_badges

    async def _run():
        async with async_session_factory() as db:
            await check_and_award_badges(db, UUID(user_id))
            await db.commit()

    asyncio.run(_run())


@celery_app.task
def send_email_background(to_email: str, subject: str, body: str):
    """Background task to send email notification."""
    import asyncio

    async def _run():
        if not settings.email_enabled:
            return
        try:
            from email.mime.text import MIMEText

            import aiosmtplib

            msg = MIMEText(body, "html")
            msg["From"] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
            msg["To"] = to_email
            msg["Subject"] = subject

            await aiosmtplib.send(
                msg,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USER,
                password=settings.SMTP_PASSWORD,
                use_tls=True,
            )
        except Exception as e:
            print(f"Email send failed: {e}")

    asyncio.run(_run())
