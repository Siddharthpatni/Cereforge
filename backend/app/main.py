"""FastAPI application factory with middleware, CORS, and router mounting."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.core.config import settings
from app.core.redis import close_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — startup and shutdown events."""
    logger.info(f"Starting {settings.APP_NAME} v1.0")
    yield
    await close_redis()
    logger.info(f"Shutting down {settings.APP_NAME}")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        description="The AI & Autonomous Systems Learning Platform — Train Machines. Earn Your Rank.",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Sentry
    if settings.SENTRY_DSN:
        try:
            import sentry_sdk
            sentry_sdk.init(dsn=settings.SENTRY_DSN, traces_sample_rate=0.1)
        except ImportError:
            logger.warning("sentry-sdk not installed, skipping Sentry init")

    # Mount routers
    from app.api.routes import auth, tasks, community, badges, leaderboard, learning_paths, users, dashboard

    app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
    app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["Tasks"])
    app.include_router(community.router, prefix="/api/v1", tags=["Community"])
    app.include_router(badges.router, prefix="/api/v1/badges", tags=["Badges"])
    app.include_router(leaderboard.router, prefix="/api/v1/leaderboard", tags=["Leaderboard"])
    app.include_router(learning_paths.router, prefix="/api/v1/learning-paths", tags=["Learning Paths"])
    app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
    app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])

    # Health endpoints
    @app.get("/api/v1/health", tags=["System"])
    async def health_check():
        db_ok = True
        redis_ok = True
        try:
            from app.core.database import engine
            async with engine.connect() as conn:
                await conn.execute(
                    __import__("sqlalchemy").text("SELECT 1")
                )
        except Exception:
            db_ok = False

        try:
            from app.core.redis import get_redis
            r = await get_redis()
            await r.ping()
        except Exception:
            redis_ok = False

        return {
            "status": "healthy" if (db_ok and redis_ok) else "degraded",
            "db": "connected" if db_ok else "disconnected",
            "redis": "connected" if redis_ok else "disconnected",
            "version": "1.0.0",
        }

    @app.get("/api/v1/health/ready", tags=["System"])
    async def readiness_check():
        return {"status": "ready"}

    return app


app = create_app()
