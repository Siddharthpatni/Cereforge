# CereForge — Complete Knowledge Guide

**Document type**: Engineering knowledge guide  
**Audience**: Anyone who wants to understand and rebuild this system from scratch — no AI, no shortcuts.  
**Version**: March 2026

---

## Preface

This document maps the intellectual territory you need to cover to understand CereForge. It is not a tutorial — it is a precise description of what each file does, what concepts it requires, and what you'd need to learn to write it yourself.

The project is a web platform for AI engineering education. Users solve design problems, submit written solutions, receive automated feedback, earn XP and badges, and participate in a community Q&A forum. The backend is Python/FastAPI, the database is PostgreSQL, the queue is Celery/Redis, and the frontend is React/Vite.

---

## Part I — Project File Structure (Annotated)

### Repository Root

```
Cereforge/
├── README.md                    # What the project is and how to run it locally
├── CHANGELOG.md                 # Human-maintained log of meaningful changes
├── LICENSE                      # MIT
├── docker-compose.yml           # Orchestrates all services for local dev
├── docker-compose.dev.yml       # Dev overrides (hot-reload mounts)
├── start_demo.sh                # Shell script: starts all services in sequence
├── docs/
│   ├── ARCHITECTURE.md          # System design decisions explained
│   ├── PROD_SETUP.md            # Step-by-step deployment guide (Supabase/Render/Vercel)
│   ├── KNOWLEDGE_GUIDE.md       # This file
│   └── CereForge_Research_Note.md  # Research proposal for LLM evaluation problem
├── .github/
│   └── workflows/ci.yml         # GitHub Actions: runs lint, tests, build on every push
├── backend/                     # Python FastAPI application
└── frontend/                    # React/Vite application
```

### Backend: `backend/`

```
backend/
├── Dockerfile                   # Two-stage build: builder copies deps, production stage copies app
├── requirements.txt             # All Python dependencies pinned to exact versions
├── pyproject.toml               # Ruff (linter/formatter) config and pytest config
├── alembic.ini                  # Alembic database migration configuration
├── alembic/
│   └── versions/                # One .py file per migration, each describing a schema change
├── .env                         # Local environment variables (NOT committed to git)
├── .env.example                 # Template showing required env vars (committed)
└── app/
    ├── main.py                  # Application factory: creates FastAPI app, mounts middleware and routers
    ├── core/
    │   ├── config.py            # Pydantic Settings: reads env vars, validates types, exposes as properties
    │   ├── database.py          # SQLAlchemy async engine and session factory
    │   ├── security.py          # JWT creation and verification functions
    │   └── redis.py             # Redis connection singleton
    ├── models/
    │   ├── __init__.py          # Imports all models so Alembic can detect them for migrations
    │   ├── user.py              # User table: id, username, email, password hash, xp, is_admin, etc.
    │   ├── task.py              # Task and TaskResource tables
    │   ├── submission.py        # TaskSubmission: which user submitted which task, xp_earned, score
    │   ├── post.py              # Community post (question)
    │   ├── comment.py           # Comment and Vote tables
    │   ├── badge.py             # Badge definition and UserBadge (many-to-many junction)
    │   ├── notification.py      # In-app notification per user
    │   ├── learning_path.py     # LearningPath, Module, Lesson, Enrollment tables
    │   └── otp.py               # One-time password for password reset flow
    ├── schemas/
    │   ├── user.py              # Pydantic: UserCreate, UserResponse, UserProfile shapes
    │   ├── task.py              # Pydantic: TaskResponse, SubmitRequest, SubmitResponse
    │   ├── post.py              # Pydantic: PostCreate, PostResponse, CommentResponse
    │   └── common.py            # Pydantic: LeaderboardEntry, BadgeResponse, NotificationResponse
    ├── api/
    │   ├── deps.py              # Dependency functions: get_db, get_current_user, get_current_admin
    │   └── routes/
    │       ├── auth.py          # POST /auth/register, /auth/login, /auth/refresh, /auth/logout, GET /auth/me
    │       ├── tasks.py         # GET /tasks, GET /tasks/{slug}, POST /tasks/{slug}/submit
    │       ├── community.py     # CRUD for posts, comments; voting; AI community analysis
    │       ├── leaderboard.py   # GET /leaderboard with pagination and timeframe filter
    │       ├── badges.py        # GET /badges (user's earned badges + all available)
    │       ├── dashboard.py     # GET /dashboard (personalised: next task, stats, recent activity)
    │       ├── users.py         # GET/PATCH /users/me, GET /users/{id}/profile
    │       ├── admin.py         # Admin-only endpoints: user management, XP overrides, bans
    │       ├── notifications.py # GET /notifications, PATCH /notifications/read-all, PATCH /{id}/read
    │       └── learning_paths.py # GET /paths, GET /paths/{slug}
    ├── services/
    │   ├── task_evaluator.py    # Calls Gemini API to score a submission against a rubric
    │   ├── ai_mentor.py         # Streams Gemini guidance for a specific task/question
    │   ├── badge_engine.py      # Checks all badge conditions for a user, awards newly earned ones
    │   ├── xp_service.py        # Atomic XP update, rank calculation from XP
    │   ├── notification.py      # Creates in-app notification records
    │   └── ai_detector.py       # Placeholder: flags suspicious submissions (not fully implemented)
    ├── workers/
    │   └── tasks.py             # Celery task definitions: check_badges_background, send_email_background
    ├── seeds/
    │   ├── run_all.py           # Entry point: runs all seeders in dependency order
    │   ├── tasks_seed.py        # Inserts 24 challenge tasks across 4 tracks
    │   ├── badges_seed.py       # Inserts 23 badge definitions
    │   ├── paths_seed.py        # Inserts 5 learning paths with modules and lessons
    │   └── community_seed.py    # Inserts sample posts for a non-empty community on first run
    └── scripts/
        ├── explore_db.py        # Debug script: prints table names and row counts
        └── wipe_db.py           # Danger: deletes all user data (keeps schema intact)
```

### Frontend: `frontend/src/`

```
frontend/src/
├── main.jsx                     # Entry point: renders <App /> into #root DOM node
├── App.jsx                      # Route definitions: public routes, protected routes with auth guard
├── index.css                    # Global styles: CSS variables, dark theme, scrollbar overrides
├── App.css                      # App-level layout styles
├── animations.css               # Keyframe animations (badge unlock, XP counter, cinematic runner)
├── api/
│   └── client.js                # Axios instance with base URL, request interceptor (attaches JWT),
│                                #   response interceptor (handles 401 → token refresh, logs 500s)
├── stores/
│   ├── authStore.js             # Zustand store: accessToken, refreshToken, user, setTokens, logout
│   └── uiStore.js               # Zustand store: toast notifications, modal state
├── pages/
│   ├── Auth.jsx                 # Login and register tabs, form state, calls /auth/login or /auth/register
│   ├── Dashboard.jsx            # User home: shows XP, rank, next recommended task, recent badges
│   ├── Tasks.jsx                # Task list with track/difficulty filter, completion ring in header
│   ├── TaskDetail.jsx           # Single task: description, resources, submission editor, AI mentor panel
│   ├── Leaderboard.jsx          # Global rankings with All/Month/Week tabs
│   ├── Community.jsx            # Post list with filters: track, tag, difficulty
│   ├── PostDetail.jsx           # Single post with answer editor, voting, AI analysis button
│   ├── Profile.jsx              # User profile: avatar, rank badge, bio, stats, earned badges
│   ├── Paths.jsx                # Learning paths list
│   ├── PathDetail.jsx           # Single path: modules, lessons, enrollment progress
│   ├── Admin.jsx                # Admin portal: user management, overview stats, moderation actions
│   ├── ForgotPassword.jsx       # 3-step: email entry → OTP input → new password
│   ├── WeeklyTasks.jsx          # Weekly challenge view
│   └── NotFound.jsx             # 404 page
├── components/
│   ├── layout/
│   │   ├── Layout.jsx           # Wraps every protected page: Sidebar + Navbar + main content area
│   │   ├── Navbar.jsx           # Top bar: search, notification bell, user info, logout
│   │   └── Sidebar.jsx          # Left nav: links to all pages, collapsible on mobile
│   ├── ui/
│   │   ├── Button.jsx           # Reusable button with variant props (primary, ghost, danger)
│   │   ├── Card.jsx             # Generic card container component
│   │   ├── Badge.jsx            # Small status pill (difficulty, track, rank tier)
│   │   ├── Modal.jsx            # Overlay modal with backdrop click to close
│   │   ├── BenchmarkModal.jsx   # Post-submission modal: shows evaluation score and feedback
│   │   ├── ToastContainer.jsx   # Renders toast notifications from uiStore
│   │   ├── ErrorBoundary.jsx    # Catches React render errors, shows fallback UI
│   │   ├── FullPageLoader.jsx   # Spinner for initial auth check / data loading
│   │   └── PageSkeleton.jsx     # Skeleton loading placeholder
│   ├── tasks/
│   │   └── AIMentorPanel.jsx    # Streaming AI guidance panel in TaskDetail, uses EventSource
│   └── signature/
│       ├── CinematicRunner.jsx  # Animated badge unlock sequence (played after earning a badge)
│       ├── XPCounter.jsx        # Animated XP increment counter
│       ├── PipelineBuilder.jsx  # Interactive diagram component for RAG/agent pipeline tasks
│       └── MarkdownRenderer.jsx # Renders markdown submission editor output with syntax highlighting
└── utils/
    └── cn.js                    # classnames utility — merges CSS class strings conditionally
```

---

## Part II — Key Code Patterns (With Actual Code from the Project)

### 2.1 FastAPI Dependency Injection

The `Depends()` pattern is central to FastAPI. It avoids repeating code in every route by declaring shared logic as a dependency. The database session and the current user are injected this way.

From `backend/app/api/deps.py`:

```python
async def get_db():
    async with async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
```

Then in any route handler:

```python
@router.get("/tasks")
async def list_tasks(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    ...
```

**Why it works**: FastAPI sees `Depends(get_db)` and calls `get_db()` before calling your route function. It handles the `yield` — code before `yield` runs on request, code after `yield` runs on response or error. This is Python's context manager pattern applied to HTTP.

**What you need to learn**: Python generators (`yield`), context managers (`with` / `__enter__` / `__exit__`), and then how FastAPI uses them via `Depends`.

---

### 2.2 Async Database Queries

Every database query follows this pattern:

```python
# Select one row
result = await db.execute(select(User).where(User.id == user_id))
user = result.scalar_one_or_none()

# Select multiple rows
result = await db.execute(
    select(Task)
    .where(Task.is_active)
    .order_by(Task.display_order)
)
tasks = result.scalars().all()

# Atomic counter update (safe for concurrent requests)
await db.execute(
    update(User)
    .where(User.id == user_id)
    .values(xp=User.xp + amount)
    .returning(User.xp)
)
```

**The key distinction**: `result.scalar_one_or_none()` returns a single ORM object or `None`. `result.scalars().all()` returns a list. `result.all()` returns a list of Row tuples (useful for aggregates and joins).

**What you need to learn**: SQLAlchemy 2.0 Core — `select()`, `update()`, `insert()`, `join()`, `func.count()`, `group_by()`, `.where()`. The ORM-level `.query()` API from SQLAlchemy 1.x is not used here.

---

### 2.3 JWT Creation and Verification

From `backend/app/core/security.py`:

```python
def create_access_token(user_id: str, email: str) -> str:
    expire = datetime.now(UTC) + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": user_id,         # "subject" — standard JWT claim
        "email": email,
        "type": "access",
        "exp": expire,
        "iat": datetime.now(UTC),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def get_user_id_from_token(token: str, token_type: str) -> str | None:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("type") != token_type:
            return None
        return payload.get("sub")
    except JWTError:
        return None
```

**What this means**: A JWT is created by encoding a dict (the "claims") signed with `JWT_SECRET_KEY`. Any service that knows the secret can verify the token without a database lookup. The `exp` field is checked automatically by `jwt.decode` — expired tokens raise a `JWTError`.

**What you need to learn**: What claims are standard in JWTs (`sub`, `iat`, `exp`, `aud`), why `HS256` is symmetric, and what happens if your JWT secret key is leaked (hint: you have to rotate it and invalidate all existing tokens).

---

### 2.4 Pydantic Schemas vs SQLAlchemy Models

These are two separate things that often confuse beginners:

**SQLAlchemy Model** (in `models/user.py`) — describes the database table:

```python
class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    xp: Mapped[int] = mapped_column(Integer, default=0)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
```

**Pydantic Schema** (in `schemas/user.py`) — describes what the API accepts and returns:

```python
class UserResponse(BaseModel):
    id: UUID
    username: str
    email: str
    xp: int
    # NOTE: password_hash is NOT here — deliberately excluded from API responses

    model_config = ConfigDict(from_attributes=True)  # allows creating from ORM object
```

The `model_config = ConfigDict(from_attributes=True)` line is critical — it allows you to do `UserResponse.model_validate(user_orm_object)` and Pydantic will read the attributes from the ORM model.

**Why separate?** The database model can have fields you never want to expose (like `password_hash`). The API schema is the contract with the client. Keeping them separate means your ORM can change without necessarily changing your API.

---

### 2.5 Celery Background Tasks

When a task submission arrives, the route handler triggers a background job and returns immediately:

```python
# In routes/tasks.py — inside the submit route
check_badges_background.delay(str(current_user.id))

# Return 200 to the user right now, don't wait for badge check
return {"status": "submitted", "xp_earned": xp_earned}
```

The Celery task itself (`workers/tasks.py`) runs in a separate process:

```python
@celery_app.task
def check_badges_background(user_id: str):
    import asyncio
    from app.services.badge_engine import check_and_award_badges
    from app.core.database import async_session_factory

    async def _run():
        async with async_session_factory() as db:
            await check_and_award_badges(db, UUID(user_id))
            await db.commit()

    asyncio.run(_run())
```

**Note the pattern**: Celery tasks are synchronous functions. To do async database work inside them, `asyncio.run()` creates a new event loop for the duration of the task. This is necessary because the Celery worker is a separate process from the FastAPI server and has no shared event loop.

---

### 2.6 SSE Streaming (AI Mentor)

From `backend/app/services/ai_mentor.py` — returns an async generator:

```python
async def stream_mentor_guidance(task, user_message, skill_level):
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    
    async for chunk in await client.aio.models.generate_content_stream(...):
        if chunk.text:
            yield f"data: {json.dumps({'content': chunk.text})}\n\n"
```

In the route (`community.py`):

```python
return StreamingResponse(
    stream_mentor_guidance(task, message, user.skill_level),
    media_type="text/event-stream",
    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
)
```

On the frontend (`AIMentorPanel.jsx`):

```javascript
const eventSource = new EventSource(`${API_URL}/ai-mentor/guidance?...`);
eventSource.onmessage = (e) => {
    const data = JSON.parse(e.data);
    setResponse(prev => prev + data.content);  // append each chunk
};
```

**What you need to understand**: The server holds a long-lived HTTP connection open and sends `data: ...\n\n` chunks as they arrive. The browser's native `EventSource` handles reconnection. This is fundamentally different from a normal JSON response — the connection stays open until the generator is exhausted.

---

### 2.7 Zustand Store (Frontend State)

From `frontend/src/stores/authStore.js`:

```javascript
import { create } from "zustand";
import { persist } from "zustand/middleware";

export const useAuthStore = create(
    persist(
        (set) => ({
            accessToken: null,
            refreshToken: null,
            user: null,

            setTokens: (access, refresh) =>
                set({ accessToken: access, refreshToken: refresh }),

            setUser: (user) => set({ user }),

            logout: () =>
                set({ accessToken: null, refreshToken: null, user: null }),
        }),
        {
            name: "cereforge-auth",        // key in localStorage
            partialize: (state) => ({      // only persist tokens, not user object
                accessToken: state.accessToken,
                refreshToken: state.refreshToken,
            }),
        }
    )
);
```

**What this does**: `create()` creates a store. `persist()` wraps it so the tokens survive browser refresh (stored in localStorage). Any component can call `useAuthStore(state => state.user)` to subscribe to the user object — when it changes, the component re-renders.

**Why not Redux?** Redux requires actions, reducers, and a separate dispatch mechanism. Zustand does the same thing in ~30 lines. For an app this size, the additional structure of Redux adds complexity without benefit.

---

### 2.8 React Query (Server State)

From `frontend/src/pages/Tasks.jsx`:

```javascript
const { data: tasksData, isLoading, isError, refetch } = useQuery({
    queryKey: ["tasks", { track, difficulty }],
    queryFn: () => apiClient.get("/tasks", { params: { track, difficulty } }).then(r => r.data),
    staleTime: 60_000,   // treat as fresh for 60 seconds — don't refetch immediately
});
```

After a mutation (e.g., submitting a solution):

```javascript
const mutation = useMutation({
    mutationFn: (data) => apiClient.post(`/tasks/${slug}/submit`, data),
    onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ["tasks"] });  // marks cache stale → refetches
        queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
});
```

**The mental model**: React Query maintains a cache keyed by `queryKey`. `useQuery` reads from the cache and fetches if stale. `invalidateQueries` marks cache entries as stale after a mutation — triggering a background refetch. You never manually update state after an API call; you just invalidate the relevant queries.

---

### 2.9 The Badge Engine — Condition Checking

The badge engine in `backend/app/services/badge_engine.py` iterates over badge definitions and checks each condition. Each badge in the database has a `condition_type` string and a `condition_value` JSON object:

```json
{
  "condition_type": "track_count",
  "condition_value": {"track": "llm", "count": 5}
}
```

The engine evaluates it:

```python
if ctype == "track_count":
    track = str(cval.get("track", ""))
    count = int(cval.get("count", 0))
    return track_counts.get(track, 0) >= count
```

This pattern — storing condition logic as structured data in the database, not as hardcoded rules — is called a **rules engine**. It lets you add new badges by inserting a row, not by deploying code.

**The trade-off**: Flexible, data-driven conditions are harder to debug than explicit Python conditions. The `condition_type` values must be documented and the engine updated each time a new condition type is needed.

---

## Part III — Database Schema Design Decisions

### Why UUID primary keys, not auto-increment integers?

```python
id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
```

Auto-increment integers reveal information: if your user ID is 47, a competitor can guess there are ~47 users. UUIDs are random. They are also safe across distributed systems — you can generate an ID in Python before inserting, without a database round-trip.

**Trade-off**: UUIDs are larger (16 bytes vs 4 bytes), and sequential row inserts fragment the B-tree index. For this application scale, this doesn't matter.

### Why separate `is_active` and `is_admin` flags on User?

```python
is_active: Mapped[bool] = mapped_column(Boolean, default=True)
is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
```

`is_active = False` is the "soft ban" mechanism. It deactivates the account without deleting the user's data. Deleting the row would cascade and remove all posts, submissions, and badges — collateral damage the admin didn't intend.

### Why a junction table for badges?

```python
class UserBadge(Base):
    __tablename__ = "user_badges"
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    badge_id: Mapped[UUID] = mapped_column(ForeignKey("badges.id"))
    earned_at: Mapped[datetime] = mapped_column(default=utcnow)
```

Because a user can earn many badges, and many users can earn the same badge. This is a many-to-many relationship. The junction table is the standard relational way to model it. Querying "which badges has user X earned" becomes `SELECT badge_id FROM user_badges WHERE user_id = X`.

---

## Part IV — What to Read, In Order

| Topic | Resource |
|---|---|
| Python fundamentals | Work through all of [docs.python.org/3/tutorial](https://docs.python.org/3/tutorial/) |
| Python async/await | [docs.python.org/3/library/asyncio](https://docs.python.org/3/library/asyncio.html) — coroutines, tasks, event loop |
| HTTP fundamentals | MDN: HTTP — methods, status codes, headers, cookies, CORS |
| SQL | *Learning SQL* by Alan Beaulieu — ch. 1–10 |
| PostgreSQL | PostgreSQL docs — focus on transactions, indexes, `EXPLAIN ANALYZE` |
| FastAPI | [fastapi.tiangolo.com](https://fastapi.tiangolo.com) — the full tutorial incl. dependency injection |
| Pydantic v2 | [docs.pydantic.dev](https://docs.pydantic.dev/) — validators, model config, computed fields |
| SQLAlchemy 2.0 | [docs.sqlalchemy.org](https://docs.sqlalchemy.org) — 2.0 Core expression language, async sessions |
| Alembic | [alembic.sqlalchemy.org](https://alembic.sqlalchemy.org) — autogenerate, upgrade, downgrade |
| JWTs | [jwt.io/introduction](https://jwt.io/introduction) → RFC 7519 |
| bcrypt | Any explainer on password hashing — understand salts and why MD5 is wrong |
| React | [react.dev](https://react.dev) — hooks, component lifecycle, state |
| React Router v6 | [reactrouter.com/docs](https://reactrouter.com/docs) — especially `Outlet`, loaders |
| Zustand | [docs.pmnd.rs/zustand](https://docs.pmnd.rs/zustand/getting-started/introduction) |
| TanStack Query | [tanstack.com/query/latest/docs](https://tanstack.com/query/latest/docs/framework/react/overview) |
| Axios | [axios-http.com/docs](https://axios-http.com/docs/intro) — interceptors are the important part |
| Celery | [docs.celeryq.dev](https://docs.celeryq.dev) — Guide: Tasks and Next Steps |
| Redis | First 3 chapters of *Redis in Action* by Josiah Carlson |
| Docker | Docker "Get Started" + Compose docs |
| LLM evaluation | Zheng et al. (2023) MT-Bench; Shahul et al. (2023) RAGAS |

---

## Part V — How I Would Rebuild This (The Right Order)

**Step 1: Database schema**

Write `models.py` and the first Alembic migration before any route. Every other decision depends on the data model. The order of things:

1. Sketch the entities on paper: User, Task, Submission, Post, Comment, Badge, UserBadge, Notification.
2. For each entity, list the fields and their types.
3. Draw the foreign key relationships (User → Submission, Task → Submission, etc.).
4. Write SQLAlchemy models. Run `alembic revision --autogenerate` to create the migration.
5. Run `alembic upgrade head`. Connect to PostgreSQL with psql and verify the tables exist.

**Step 2: Auth**

Write `POST /auth/register` and `POST /auth/login` before anything else. Test with `curl`:

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "email": "test@test.com", "password": "Password123!"}'
```

If it returns a 201 and a JWT, auth is working. All other endpoints depend on auth.

**Step 3: One feature, end-to-end**

Task list → task detail → task submission → XP awarded. No badges, no AI, no email, no Celery. Call `award_xp` synchronously in the route handler for now. Get the whole thing working with tests before adding the next layer.

**Step 4: Add Celery for expensive work**

Once task submission works synchronously, move the badge checking and XP award into Celery workers. The route handler becomes faster; the work happens in the background.

**Step 5: Add the AI evaluator**

Only once the submission flow is stable. The evaluator is the most brittle part of the system — LLM APIs fail, responses are inconsistent, latency is high. Make everything else solid first.

**Step 6: Frontend**

Start with `Auth.jsx`. Get login and register working. Then `Dashboard.jsx`. Then `Tasks.jsx` + `TaskDetail.jsx`. Build the API calls first, then the UI around them. If you try to build UI and API simultaneously, you will spend most of your time debugging mismatched assumptions.

---

## Part VI — Known Gaps and Open Problems

| Problem | Status | What's needed to solve it |
|---|---|---|
| LLM evaluator inconsistency | Unsolved | Rubric calibration against human raters; measure Cohen's kappa |
| AI detector (`ai_detector.py`) | Placeholder | Needs a real implementation; current version always returns False |
| Streak tracking | `# TODO` in badge_engine.py | Requires a streaks table and a daily job to check/update |
| XSS in community posts | Partially mitigated | User-submitted HTML needs sanitization before rendering |
| Email sending | Optional | SMTP is configured but most deployments won't set it up |

---

*This document reflects CereForge as of March 2026.*
