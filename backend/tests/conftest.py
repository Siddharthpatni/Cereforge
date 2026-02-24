"""Shared test fixtures for the CereForge test suite."""

import asyncio

# Use SQLite in-memory for tests (fast, no external DB needed)
# For integration tests requiring Postgres features, set TEST_DATABASE_URL env var
import os
import uuid
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.api.deps import get_db
from app.core.database import Base
from app.main import app
from app.models.badge import Badge
from app.models.task import Task

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "sqlite+aiosqlite:///./test.db"
)

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    """Create all tables at session start, drop at end."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def seed_test_data(setup_database):
    """Seed tasks and badges for tests."""
    async with TestSessionLocal() as db:
        # Seed 12 tasks
        tracks = ["llm", "rag", "vision", "agents"]
        difficulties = ["beginner", "intermediate", "expert"]
        for i in range(12):
            track = tracks[i % 4]
            difficulty = difficulties[i % 3]
            task = Task(
                slug=f"test-task-{track}-{i}",
                track=track,
                difficulty=difficulty,
                title=f"Test Task {track.upper()} #{i}",
                description=f"A comprehensive test task for {track} engineering that covers advanced concepts and practical implementation patterns." * 3,
                beginner_guide=f"Start by understanding what {track} means in the context of AI engineering. Think of it like building blocks." * 3,
                hint=f"Consider using the {track} approach with careful attention to edge cases and error handling patterns." * 2,
                xp_reward=[50, 150, 300][i % 3],
                display_order=i,
                colab_url=f"https://colab.research.google.com/drive/test-{track}-{i}",
            )
            db.add(task)

        # Assign known slugs for specific test cases
        await db.get(Task, None)  # will use slug-based queries instead

        # Seed 12 badges with proper JSON dicts compatible with badge_engine.py
        badge_data = [
            ("zero-to-ai", "Zero to AI", "🚀", "total_tasks", {"total_tasks": 1}, 25),
            ("prompt-whisperer", "Prompt Whisperer", "🧠", "track_count", {"track": "llm", "count": 1}, 25),
            ("chain-master", "Chain Master", "🔗", "track_count", {"track": "llm", "count": 3}, 75),
            ("memory-architect", "Memory Architect", "🗄️", "track_count", {"track": "rag", "count": 1}, 25),
            ("retrieval-expert", "Retrieval Expert", "📡", "track_count", {"track": "rag", "count": 3}, 75),
            ("vision-pioneer", "Vision Pioneer", "👁️", "track_count", {"track": "vision", "count": 1}, 25),
            ("perception-master", "Perception Master", "🔮", "track_count", {"track": "vision", "count": 3}, 75),
            ("agent-builder", "Agent Builder", "🤖", "track_count", {"track": "agents", "count": 1}, 25),
            ("autonomy-architect", "Autonomy Architect", "🌐", "track_count", {"track": "agents", "count": 3}, 75),
            ("full-stack-ai", "Full Stack AI", "🌐", "all_tracks", {}, 100),
            ("community-sage", "Community Sage", "💬", "accepted_answers", {"count": 1}, 50),
            ("cereforge-elite", "CereForge Elite", "👑", "total_tasks", {"total_tasks": 12}, 200),
        ]
        for idx, (slug, name, icon, ctype, cval, xp) in enumerate(badge_data):
            badge = Badge(
                slug=slug,
                name=name,
                icon=icon,
                condition_type=ctype,
                condition_value=cval,
                xp_bonus=xp,
                description=f"Awarded for: {ctype}",
                display_order=idx,
            )
            db.add(badge)

        await db.commit()


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP client for testing the FastAPI app."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"  # type: ignore
    ) as ac:
        yield ac


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Direct database session for test setup/teardown."""
    async with TestSessionLocal() as session:
        yield session


# ── Helper functions ──────────────────────────────────────────────────

async def register_user(
    client: AsyncClient,
    email: str | None = None,
    password: str = "TestPass123!",
    skill_level: str = "absolute_beginner",
    username: str | None = None,
) -> dict:
    """Register a user and return the full response dict."""
    email = email or f"test-{uuid.uuid4().hex[:8]}@example.com"
    username = username or f"user_{uuid.uuid4().hex[:8]}"
    response = await client.post("/api/v1/auth/register", json={
        "username": username,
        "email": email,
        "password": password,
        "skill_level": skill_level,
    })
    return response.json() if response.status_code == 201 else {"_response": response}


def auth_headers(token: str) -> dict:
    """Return Authorization header dict."""
    return {"Authorization": f"Bearer {token}"}
