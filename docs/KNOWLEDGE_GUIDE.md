# CereForge — What You Need to Know to Build This Yourself

**Document type**: Engineering knowledge guide  
**Audience**: Anyone who wants to understand and rebuild this system from scratch — no AI, no shortcuts.

---

## Preface

This document is not a tutorial. It is a map of the intellectual territory you need to cover. A thesis chapter on the same system would reference each of these areas in depth. Here, I aim to be precise about *what matters* and *why it matters in this context*, so you can go read the right things rather than reading everything.

The project is a web platform for AI engineering education. Users solve design problems, submit written solutions, receive automated feedback, earn XP and badges, and participate in a community forum. The system is built on a Python async backend, a PostgreSQL database, a Redis-backed task queue, and a React frontend. Understanding *why* these choices were made is as important as understanding *how* they work.

---

## Part I — The Conceptual Foundation

### 1.1 What the System Actually Does

CereForge is a structured learning environment that separates itself from tutorial platforms by focusing on *evaluation of reasoning*, not execution of predefined steps. Users submit their architectural decisions — for example, how they would design a RAG pipeline to handle conflicting retrieval results — and the system scores their reasoning across multiple dimensions.

The core intellectual claim is that learning AI engineering requires decision-making under constraint, which tutorial platforms do not provide. The evaluation mechanism is therefore the most important and least solved part of the system.

### 1.2 The Evaluation Problem (Know This First)

The most technically interesting component of CereForge is the automated evaluator in `backend/app/services/task_evaluator.py`. It uses an LLM (currently Google Gemini) to score open-ended submissions against a multi-dimensional rubric.

The fundamental problem: **LLM-as-judge evaluation is inconsistent.** Two identical submissions may receive different scores if the temperature is non-zero, if the rubric is ambiguously worded, or if the model's context window is partially occupied by different token sequences. This is documented extensively in:

- Zheng et al., 2023 — *Judging LLM-as-a-Judge with MT-Bench*
- Shahul et al., 2023 — *RAGAS: Automated Evaluation of RAG frameworks*

Before building this system, you need to understand *inter-rater reliability* (Cohen's kappa, Krippendorff's alpha) and *rubric calibration* well enough to design evaluation criteria that minimize judge variance. This is the part I have not fully solved. Section 8 of the research note in `docs/CereForge_Research_Note.md` describes this honestly.

---

## Part II — The Technical Stack

### 2.1 Backend: FastAPI + SQLAlchemy (Async)

Why FastAPI over Flask or Django REST Framework? Two reasons:

1. **Async-first design.** The platform streams AI responses via Server-Sent Events. This requires non-blocking I/O throughout the request/response cycle. FastAPI is built on Starlette, which is genuinely async. Django is not, and Flask's async support is retrofitted.

2. **Automatic schema validation.** FastAPI uses Pydantic models for both request validation and response serialization. You define a schema once; the framework enforces it at the boundary and generates OpenAPI documentation automatically. This reduces the surface area for bugs at API boundaries.

**What you need to learn:**

- Python's `asyncio` event loop — particularly the difference between `async def`, `await`, `asyncio.gather`, and why you cannot block the event loop with synchronous calls.
- [FastAPI documentation](https://fastapi.tiangolo.com/) — focus on dependency injection (the `Depends()` pattern), lifespan events, and exception handlers.
- Pydantic v2 — validators, model inheritance, `model_config`, computed fields.

**The database layer:**

SQLAlchemy 2.0 with its async session is conceptually different from ORM usage most tutorials demonstrate. You will not find `.query()`. Instead:

```python
result = await db.execute(select(User).where(User.id == user_id))
user = result.scalar_one_or_none()
```

Every DB operation is an explicit query builder expression, awaited through an `AsyncSession`. This is intentional — it forces you to think about what SQL you are actually writing.

**What you need to learn:**

- SQLAlchemy 2.0 Core API (not the 1.x query API) — `select()`, `insert()`, `update()`, `join()`, `.where()`, `.returning()`.
- PostgreSQL fundamentals: indexes, `SERIAL` vs `UUID` primary keys, transactional semantics (`COMMIT`, `ROLLBACK`), `asyncpg` as the Python driver.
- Alembic for schema migrations — understand the difference between a migration and a seed, and why you need both separately.

---

### 2.2 Authentication: JWT + Refresh Token Rotation

CereForge uses a dual-token authentication model: a short-lived **access token** (24 hrs) and a longer-lived **refresh token** (30 days). This is not unique to this project, but understanding why this is the standard requires understanding what JWTs actually are.

A JWT is a base64-encoded JSON object signed with a secret key. The server does not store it — it trusts any token it can verify against its own secret key. The implication is that a stolen access token cannot be revoked without implementing a token blocklist (which removes the statelessness benefit). The short expiry is the compromise.

Refresh token rotation: every time you use the refresh token to generate a new access token, you also issue a new refresh token. If someone steals the refresh token and uses it, the original also becomes invalid, which lets you detect the compromise.

**What you need to learn:**

- RFC 7519 (JWT spec) — at least the structure of the header, payload, and signature.
- `python-jose` for signing/verifying tokens in Python.
- The difference between `HS256` (symmetric, single secret key) and `RS256` (asymmetric, public/private key pair). For this project, HS256 is sufficient. For a multi-service architecture, you'd want RS256.
- Password hashing: bcrypt and why you never store plaintext passwords or MD5 hashes.

---

### 2.3 Background Task Queue: Celery + Redis

When a user submits a task solution, several expensive operations need to happen: running the LLM evaluation, checking badge conditions, awarding XP, and sending a notification. These cannot happen synchronously within the HTTP request/response cycle without exceeding timeout limits and degrading the user experience.

Celery solves this by moving the work to background workers. Redis is the message broker — it holds the task queue. The web server enqueues a job (`task_evaluator.delay(user_id, submission_id)`) and responds immediately. A separate Celery worker process picks up the job and executes it independently.

**What you need to learn:**

- The producer-consumer pattern and message queues conceptually.
- Redis data structures (lists, pub/sub, sorted sets) — Celery uses Redis as a message broker but Redis has many other uses (rate limiting, caching, real-time features).
- Celery documentation: focus on `@celery_app.task`, task routing, and retry logic for transient failures.
- The subtle bug: Celery workers run in separate processes. They need their own database sessions, their own event loops (if async), and cannot share in-memory state with the main FastAPI process.

---

### 2.4 Frontend: React + Vite + Zustand + React Query

The frontend is a Single Page Application. The interesting architectural choices:

**State management: Zustand instead of Redux.** Redux is powerful but verbose for an application this size. Zustand provides a simple store with minimal boilerplate. The `useAuthStore` in `frontend/src/stores/authStore.js` manages the authentication state (tokens, user profile). If you understand the `useState` hook, Zustand is the next natural step.

**Server state: TanStack Query (React Query).** There is a distinction between *client state* (which tab is selected, whether a modal is open) and *server state* (data fetched from the API). React Query manages server state: caching, refetching on window focus, invalidation after mutations. Without it, you'd write this plumbing manually in `useEffect` hooks, and you'd get it wrong in edge cases.

**What you need to learn:**

- React fundamentals: component lifecycle, hooks (`useState`, `useEffect`, `useContext`, `useRef`), the mental model of declarative rendering.
- React Router v6 — especially nested routes and the `Outlet` pattern.
- `fetch` and then Axios — understand HTTP fundamentals (methods, status codes, headers) before abstracting over them.
- Zustand — read the documentation in one sitting, it is short.
- React Query (TanStack Query) — understand `useQuery` and `useMutation`, then the caching and invalidation model.

---

### 2.5 The XP and Badge System

The gamification layer is in `backend/app/services/xp_service.py` and `backend/app/services/badge_engine.py`.

XP is simple: a flat integer per user, updated atomically with `UPDATE users SET xp = xp + $1 WHERE id = $2`. The rank is computed from the current XP at read time, not stored. This avoids the consistency problem of a stored rank that drifts out of sync with XP.

Badge conditions are evaluated by iterating over all badge definitions and checking each condition against the user's current state (submission counts, accepted answers, XP). This is a brute-force approach — O(badges × conditions). It works at this scale (23 badges). At much larger scale you would need a rules engine or event-driven evaluation.

**The key learning**: atomic database updates for counters (`UPDATE SET xp = xp + :amount`) versus optimistic locking. Understand *read-modify-write* race conditions. If two submissions arrive simultaneously and you do `user.xp = user.xp + 50` in Python and then save, one of them will be lost. The SQL `UPDATE ... SET xp = xp + 50` is atomic and avoids this.

---

### 2.6 Real-time Features: Server-Sent Events

The AI Mentor streams responses rather than returning them all at once. This uses Server-Sent Events (SSE), not WebSockets. The difference matters:

- **SSE** is unidirectional (server → client), text-based, and works over standard HTTP. The browser's native `EventSource` API handles reconnection.
- **WebSockets** are bidirectional and require a persistent connection upgrade.

For streaming LLM output where the client only needs to receive data, SSE is simpler and sufficient.

**What you need to learn:**

- The SSE protocol (it is simple: `data: <content>\n\n` over a kept-alive HTTP connection).
- Python's `StreamingResponse` in FastAPI / Starlette.
- The `async for chunk in stream` pattern when consuming a streaming LLM API response.

---

## Part III — Things That Look Simple But Are Not

### 3.1 Database Connection Pooling

The application uses `pool_size=5, max_overflow=0` in production. This is not arbitrary. Managed PostgreSQL services (Supabase, Railway, Neon) impose hard limits on concurrent connections. A pool of 20 + 10 overflow looks fine locally but will exhaust the connection limit of a free-tier managed database immediately.

The general principle: connection pool size should be configured based on the database server's limit, not the application's ideal throughput. Formula: `max_connections / number_of_app_instances`.

### 3.2 Migration Management

The project uses Alembic for schema migrations. The common mistake is mixing migrations with seed data. Migrations describe schema changes (adding a column, creating a table). Seeds describe initial data (inserting badges, tasks). These must be separate and idempotent — running seeds twice should not create duplicate records.

### 3.3 CORS

Cross-Origin Resource Sharing fails silently from the developer's perspective — the browser blocks the request before it reaches your JavaScript error handler. When deploying frontend and backend on different domains (Vercel + Render), you must explicitly list the frontend's origin in `APP_CORS_ORIGINS`. The middleware is configured in `app/main.py`.

### 3.4 Security: What This Project Does and Does Not Do

What this project handles correctly:
- Password hashing (bcrypt).
- JWT expiry and refresh rotation.
- Basic rate limiting via `slowapi`.
- Security headers (CSP, X-Frame-Options) via middleware.

What this project does not fully handle:
- Input sanitization for the community forum (XSS risk if user-supplied HTML is rendered).
- CSRF protection (generally not needed for API-only backends with JWT, but worth understanding).
- Audit logging (who changed what, when).

---

## Part IV — What to Read, In Order

This is not an exhaustive list. It is ordered by dependency — later items require the earlier ones.

| Topic | Resource |
|---|---|
| Python async/await | [Python docs: asyncio](https://docs.python.org/3/library/asyncio.html) — read the coroutines and tasks section |
| HTTP fundamentals | MDN Web Docs: HTTP — methods, status codes, headers, cookies |
| SQL | *Learning SQL* by Alan Beaulieu — chapters 1–10 cover everything needed |
| PostgreSQL | PostgreSQL official documentation — focus on transactions, indexes, EXPLAIN |
| FastAPI | [fastapi.tiangolo.com](https://fastapi.tiangolo.com/) — the entire tutorial, not just the quickstart |
| SQLAlchemy 2.0 | [SQLAlchemy 2.0 Migration Guide](https://docs.sqlalchemy.org/en/20/changelog/migration_20.html) |
| JWTs | [jwt.io/introduction](https://jwt.io/introduction) — then read RFC 7519 |
| React | [react.dev](https://react.dev) — the new official docs, not W3Schools |
| TanStack Query | [tanstack.com/query/latest/docs](https://tanstack.com/query/latest/docs/framework/react/overview) |
| Celery | [docs.celeryq.dev](https://docs.celeryq.dev/) — Getting Started + Guide: Tasks |
| Redis | *Redis in Action* by Josiah Carlson — chapters 1–3 |
| Docker & Docker Compose | Docker official "Get Started" guide |
| LLM evaluation | Zheng et al. (2023) MT-Bench paper; Shahul et al. (2023) RAGAS paper |

---

## Part V — How I Would Rebuild This, Without AI

If I were to rebuild CereForge from scratch today, I would do it in this order:

1. **Database schema first.** Write `models.py` and Alembic migrations before any route. Getting the data model right is the hardest part and the most expensive to change later.

2. **Auth routes second.** Register and login, returning a JWT. Test with `curl` before writing any frontend. This forces you to understand the request/response cycle at the protocol level.

3. **One feature end-to-end.** Task list → task detail → task submission → XP awarded. No badges, no AI, no community. Just one vertical slice, fully working, with tests.

4. **Layer complexity incrementally.** Add Celery when you have a slow synchronous operation that needs to go async. Add Redis when you need caching or a queue. Add the AI evaluator when the basic submission flow is solid.

5. **Frontend last.** Build the API contract first. A well-defined API lets the frontend be written independently. If you build frontend and backend simultaneously without a contract, you will spend most of your time debugging mismatched assumptions.

The instinct is to build everything at once. The discipline is to build one thing well, verify it, and then add the next layer.

---

*This document describes the system as of March 2026. The evaluation component (Section I.2) remains the primary open research problem.*
