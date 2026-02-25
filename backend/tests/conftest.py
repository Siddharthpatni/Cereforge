from __future__ import annotations

import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)

from app.main import app
from app.core.config import settings
from app.core.database import Base
from app.api.deps import get_db
from app.seeds.tasks_seed import seed_tasks
from app.seeds.badges_seed import seed_badges

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the whole session."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

# ── Test database engine ──────────────────────────────────────────────────
# Uses the same DATABASE_URL from settings but appended with _test
# This keeps tests isolated from development data
TEST_DB_URL = str(settings.DATABASE_URL).replace(
    "5433/cereforge", "5433/cereforge_test"
).replace("5432/cereforge", "5432/cereforge_test")

from sqlalchemy.pool import NullPool
test_engine = create_async_engine(
    TEST_DB_URL,
    echo=False,
    poolclass=NullPool,
)

TestSessionFactory = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=True,
)

# ── Create and tear down schema once per test session ────────────────────
@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    # Seed reference data (tasks and badges) once
    async with TestSessionFactory() as session:
        await seed_tasks(session)
        await seed_badges(session)
        await session.commit()
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()

# ── One fresh session per test, rolled back after ────────────────────────
@pytest_asyncio.fixture(scope="function")
async def db_session():
    """
    Each test gets its own transaction that is rolled back at the end.
    This means:
      - Tests never see each other's data
      - No cleanup needed between tests
      - No "another operation is in progress" conflicts
    """
    async with test_engine.connect() as conn:
        await conn.begin()
        session = AsyncSession(
            bind=conn,
            expire_on_commit=False,
            autocommit=False,
            autoflush=True,
        )
        yield session
        await session.close()
        await conn.rollback()

# ── HTTP client with db override ─────────────────────────────────────────
@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession):
    """
    HTTP client that uses the test db_session for every request.
    The app's get_db dependency is overridden so every route handler
    receives the same session that the test is using.
    """
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()

# ── Helper functions ──────────────────────────────────────────────────────
async def register_user(
    client: AsyncClient,
    username: str = "testuser",
    email: str | None = None,
    password: str = "TestPass123!",
    skill_level: str = "absolute_beginner",
) -> dict:
    """Register a user and return the response data including access_token."""
    if email is None:
        import uuid
        email = f"test-{uuid.uuid4().hex[:8]}@example.com"
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password,
            "skill_level": skill_level,
        },
    )
    assert resp.status_code == 201, (
        f"Registration failed: {resp.status_code} {resp.text}"
    )
    return resp.json()

def auth_headers(token: str) -> dict:
    """Return Authorization headers for a given token."""
    return {"Authorization": f"Bearer {token}"}
