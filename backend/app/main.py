"""FastAPI application factory with middleware, CORS, and router mounting."""

from __future__ import annotations

import time
import uuid
from contextlib import asynccontextmanager
from datetime import timezone

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core.redis import close_redis

# ── Security Headers Middleware ──────────────────────────────────────────────


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        if settings.is_production:
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline' fonts.googleapis.com; "
                "font-src fonts.gstatic.com; img-src 'self' data:;"
            )
        return response


# ── Request ID + Logging Middleware ──────────────────────────────────────────


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        start_time = time.perf_counter()

        logger.info(
            f"→ {request.method} {request.url.path}",
            extra={"request_id": request_id},
        )

        response = await call_next(request)

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        response.headers["X-Request-ID"] = request_id

        logger.info(
            f"← {request.method} {request.url.path} {response.status_code} ({duration_ms}ms)",
            extra={"request_id": request_id},
        )

        return response


# ── Lifespan ─────────────────────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — startup and shutdown events."""
    # ── Startup security checks ────────────────────────────────────────────
    import os

    jwt_secret = os.getenv("JWT_SECRET_KEY", "")
    if len(jwt_secret) < 32:
        raise RuntimeError(
            "JWT_SECRET_KEY must be at least 32 characters. "
            'Generate with: python -c "import secrets; print(secrets.token_hex(64))"'
        )

    required_vars = ["DATABASE_URL", "JWT_SECRET_KEY"]
    missing = [v for v in required_vars if not os.getenv(v)]
    if missing:
        raise RuntimeError(f"Missing required environment variables: {missing}")

    logger.info(f"Starting {settings.APP_NAME} v1.0.0")
    logger.info(f"Environment: {settings.APP_ENV}")
    yield
    await close_redis()
    logger.info(f"Shutting down {settings.APP_NAME}")


# ── App Factory ──────────────────────────────────────────────────────────────


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        description="Forge Your AI Mind — The competitive learning platform for AI & Autonomous Systems engineers.",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Middleware stack (order matters — first added = outermost)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestContextMiddleware)
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
    from app.api.routes import (
        admin,
        auth,
        badges,
        community,
        dashboard,
        leaderboard,
        learning_paths,
        tasks,
        users,
    )

    app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
    app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["tasks"])
    app.include_router(community.router, prefix="/api/v1/posts", tags=["community"])
    app.include_router(community.vote_router, prefix="/api/v1", tags=["votes"])
    app.include_router(community.ai_router, prefix="/api/v1", tags=["ai-mentor"])
    app.include_router(badges.router, prefix="/api/v1/badges", tags=["badges"])
    app.include_router(leaderboard.router, prefix="/api/v1/leaderboard", tags=["leaderboard"])
    app.include_router(learning_paths.router, prefix="/api/v1/paths", tags=["paths"])
    app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
    app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["dashboard"])
    app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])

    # ── Global Exception Handlers ────────────────────────────────────────────

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Return a clean 422 with per-field error messages."""
        errors = []
        for err in exc.errors():
            field = " → ".join(str(loc) for loc in err.get("loc", []))
            errors.append(
                {
                    "field": field,
                    "message": err.get("msg", "Validation error"),
                    "type": err.get("type"),
                }
            )
        return JSONResponse(
            status_code=422,
            content={"detail": errors, "type": "validation_error"},
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Return a clean JSON error for all HTTP exceptions."""
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail, "status_code": exc.status_code},
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        """Catch unhandled ValueError as a 400 Bad Request."""
        logger.warning(f"ValueError: {exc} | path={request.url.path}")
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc), "type": "bad_request"},
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        """Catch all unhandled exceptions — return 500 without leaking stack traces."""
        request_id = getattr(request.state, "request_id", "unknown")
        logger.error(f"Unhandled exception [{request_id}]: {type(exc).__name__}: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "detail": "An unexpected server error occurred. Please try again or contact support.",
                "request_id": request_id,
            },
        )

    # ── Lightweight ping ─────────────────────────────────────────────────────
    @app.get("/api/v1/ping", tags=["System"])
    async def ping():
        return {"pong": True}

    # ── Health endpoints ─────────────────────────────────────────────────
    @app.get("/api/v1/health", tags=["System"])
    async def health_check():
        from datetime import datetime

        db_ok = True
        redis_ok = True
        try:
            from app.core.database import engine

            async with engine.connect() as conn:
                await conn.execute(__import__("sqlalchemy").text("SELECT 1"))
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
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    @app.get("/api/v1/health/ready", tags=["System"])
    async def readiness_check():
        return {"status": "ready"}

    return app


app = create_app()
