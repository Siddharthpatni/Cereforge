# 🧠 CereForge
### The AI & Autonomous Systems Learning Platform

> **Forge Your AI Mind.** Build real AI engineering skills through structured challenges,
> earn XP and badges, and get help from a community of engineers who've been exactly
> where you are.

[![CI](https://github.com/Siddharthpatni/Cereforge/actions/workflows/ci.yml/badge.svg)](https://github.com/Siddharthpatni/Cereforge/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/react-18-61dafb.svg)](https://react.dev/)

---

## 📋 Table of Contents

- [What is CereForge?](#what-is-cereforge)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Running with Docker](#running-with-docker)
- [Manual Setup](#manual-setup)
- [Environment Variables](#environment-variables)
- [API Documentation](#api-documentation)
- [Running Tests](#running-tests)
- [Project Structure](#project-structure)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

---

## What is CereForge?

CereForge is an open-source competitive learning platform built specifically for
AI & Autonomous Systems engineers. Think Kaggle meets Stack Overflow, focused exclusively
on the skills that matter in production AI:

- **LLM Engineering** — Prompt chains, fine-tuning, token optimization
- **RAG Pipelines** — Vector stores, chunking strategies, hallucination prevention
- **Computer Vision** — Object detection, multimodal systems, edge deployment
- **Autonomous Agents** — LangChain agents, multi-agent systems, LangGraph

Whether you have zero AI experience or you're already shipping production models,
CereForge has a path for you.

---

## Features

**🎯 Task System**
12 hands-on AI engineering challenges with increasing difficulty. Each task includes
plain-English explanations for beginners, technical deep-dives for experts, and a
Google Colab notebook for practical implementation.

**🏆 Gamification**
Earn XP and climb through 5 ranks (Trainee → CereForge Elite). Unlock 12 badges
with a cinematic reveal animation. A living leaderboard shows where you stand.

**💬 Community Q&A**
Stack Overflow-style discussion forum where engineers ask questions, share solutions,
and vote on the best answers. Accepted answers award bonus XP to both asker and answerer.

**🧠 AI Mentor**
Powered by Claude (Anthropic). Adapts its guidance to your skill level — plain English
analogies for beginners, precise technical language for engineers. Guides you toward
the answer without giving it away.

**🗺️ Learning Paths**
Three structured paths: Zero to AI (30 days, complete beginner), Production RAG Systems
(21 days, intermediate), and Autonomous AI Agents Masterclass (28 days, advanced).

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.11, FastAPI, SQLAlchemy 2.0 (async), Alembic |
| **Database** | PostgreSQL 15 |
| **Cache** | Redis 7 |
| **Auth** | JWT (access + refresh tokens), bcrypt |
| **Frontend** | React 18, Vite, Tailwind CSS |
| **State** | Zustand (UI), React Query (server state) |
| **Animations** | CSS Keyframes, requestAnimationFrame |
| **AI** | Anthropic Claude (AI Mentor feature) |
| **Containers** | Docker, Docker Compose |
| **CI/CD** | GitHub Actions |

---

## Quick Start

The fastest way to run CereForge locally:

```bash
# 1. Clone the repository
git clone https://github.com/Siddharthpatni/Cereforge.git
cd Cereforge

# 2. Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# 3. Start everything with Docker
docker compose up --build

# 4. In a new terminal, run database migrations and seed data
docker compose exec backend alembic upgrade head
docker compose exec backend python -m app.seeds.run_all

# 5. Open your browser
open http://localhost:5173
```

The API docs are available at http://localhost:8000/docs

---

## Running with Docker

**Prerequisites:** Docker 24+, Docker Compose v2+

```bash
# Start all services (postgres, redis, backend, frontend)
docker compose up --build -d

# View logs
docker compose logs -f backend
docker compose logs -f frontend

# Run database migrations
docker compose exec backend alembic upgrade head

# Seed initial data (tasks, badges, learning paths)
docker compose exec backend python -m app.seeds.run_all

# Stop all services
docker compose down

# Stop and remove all data (clean slate)
docker compose down -v
```

**Default ports:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- PostgreSQL: localhost:5432
- Redis: localhost:6379

---

## Manual Setup

### Backend

**Requirements:** Python 3.11+, PostgreSQL 15+, Redis 7+

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development/testing

# Set up environment
cp .env.example .env
# Edit .env with your database URL and secrets (see Environment Variables below)

# Run database migrations
alembic upgrade head

# Seed initial content
python -m app.seeds.run_all

# Start the development server
uvicorn app.main:app --reload --port 8000
```

The backend will be available at http://localhost:8000

### Frontend

**Requirements:** Node.js 18+

```bash
cd frontend

# Install dependencies
npm install

# Set up environment
cp .env.example .env
# Set VITE_API_BASE_URL=http://localhost:8000/api/v1

# Start development server
npm run dev
```

The frontend will be available at http://localhost:5173

---

## Environment Variables

### Backend (`backend/.env`)

```env
# Application
APP_NAME=CereForge
APP_ENV=development
APP_SECRET_KEY=your-64-char-random-secret-here
APP_PORT=8000
APP_CORS_ORIGINS=http://localhost:5173

# Database (PostgreSQL)
DATABASE_URL=postgresql+asyncpg://cereforge:password@localhost:5432/cereforge
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# Cache (Redis)
REDIS_URL=redis://localhost:6379/0

# Authentication
JWT_SECRET_KEY=your-other-64-char-random-secret-here
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440
JWT_REFRESH_TOKEN_EXPIRE_DAYS=30
JWT_ALGORITHM=HS256

# AI Features (Anthropic)
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Email (Optional — disables email verification if not set)
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
EMAILS_FROM_EMAIL=noreply@cereforge.io

# Monitoring (Optional)
SENTRY_DSN=
```

Generate secure keys with:
```bash
python -c "import secrets; print(secrets.token_hex(64))"
```

### Frontend (`frontend/.env`)

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_NAME=CereForge
```

---

## API Documentation

When the backend is running, full interactive API documentation is available:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Create a new account |
| POST | `/api/v1/auth/login` | Login, receive JWT tokens |
| GET | `/api/v1/auth/me` | Get current user profile |
| GET | `/api/v1/tasks` | Browse all challenges |
| GET | `/api/v1/tasks/{slug}` | Get challenge details |
| POST | `/api/v1/tasks/{slug}/submit` | Submit a solution |
| GET | `/api/v1/posts` | Browse community Q&A |
| POST | `/api/v1/posts` | Ask a question |
| POST | `/api/v1/vote` | Vote on posts and answers |
| GET | `/api/v1/leaderboard` | View rankings |
| GET | `/api/v1/dashboard` | Get personalized dashboard |
| GET | `/api/v1/health` | Health check |

All authenticated endpoints require: `Authorization: Bearer {your_access_token}`

---

## Running Tests

### Backend Tests

```bash
cd backend
source venv/bin/activate

# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ -v --cov=app --cov-report=term-missing

# Run specific test file
pytest tests/test_auth.py -v

# Run specific test
pytest tests/test_tasks.py::test_submit_task_success -v
```

Expected coverage: ≥ 75%

### Frontend Tests

```bash
cd frontend

# Run all tests (one-shot)
npm run test -- --run

# Run in watch mode (for development)
npm run test

# Run with coverage
npm run test -- --run --coverage
```

---

## Project Structure

```
cereforge/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/         ← All API route handlers
│   │   │   └── deps.py         ← Shared dependencies (get_db, get_current_user)
│   │   ├── core/
│   │   │   ├── config.py       ← App settings from environment
│   │   │   ├── security.py     ← JWT and password utilities
│   │   │   ├── database.py     ← Async database engine and sessions
│   │   │   └── redis.py        ← Redis client
│   │   ├── models/             ← SQLAlchemy ORM models
│   │   ├── schemas/            ← Pydantic request/response schemas
│   │   ├── services/           ← Business logic (badge engine, XP, notifications)
│   │   ├── seeds/              ← Database seed scripts (idempotent)
│   │   └── main.py             ← FastAPI application factory
│   ├── alembic/                ← Database migrations
│   ├── tests/                  ← Pytest test suite
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/         ← Reusable UI components
│   │   ├── pages/              ← Page-level components
│   │   ├── stores/             ← Zustand state stores
│   │   ├── api/                ← Axios API client
│   │   └── utils/              ← Helper functions
│   ├── Dockerfile
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── .env.example
├── .github/
│   └── workflows/
│       └── ci.yml              ← GitHub Actions CI pipeline
├── docker-compose.yml          ← Production-like local environment
├── docker-compose.dev.yml      ← Development with hot reload
└── README.md
```

---

## Deployment

### Backend (Render)

1. Create a new Web Service on [Render](https://render.com)
2. Connect your GitHub repository
3. Set root directory: `backend`
4. Build command: `pip install -r requirements.txt && alembic upgrade head && python -m app.seeds.run_all`
5. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Add all environment variables from `backend/.env.example`

### Frontend (Vercel)

```bash
npm i -g vercel
cd frontend
vercel --prod
```

Set environment variable: `VITE_API_BASE_URL=https://your-backend-url.com/api/v1`

### Frontend (Netlify)

1. Connect GitHub repo on [Netlify](https://netlify.com)
2. Base directory: `frontend`
3. Build command: `npm run build`
4. Publish directory: `dist`
5. Add `_redirects` file to public/: `/* /index.html 200`

### Database Hosting

Recommended options (all have generous free tiers):
- **[Supabase](https://supabase.com)** — PostgreSQL + extras, best free tier
- **[Railway](https://railway.app)** — Simple, includes PostgreSQL
- **[Neon](https://neon.tech)** — Serverless PostgreSQL, scales to zero

---

## Contributing

Contributions are welcome! The areas that make the biggest impact:

**High Priority**
- New task content (the most valuable contribution — more challenges = more engagement)
- New learning path modules with lesson content
- Bug fixes with reproduction steps

**Medium Priority**
- UI/UX improvements with before/after screenshots
- Performance optimizations with benchmarks
- New badge types and conditions

**Before submitting a PR:**
1. Open an issue first to discuss the change
2. All tests must pass: `pytest tests/` and `npm run test -- --run`
3. Linting must pass: `ruff check app/` and `npm run lint`
4. Add tests for any new functionality
5. Update documentation if you change API contracts

```bash
# Fork the repository, then:
git clone https://github.com/your-username/Cereforge.git
cd Cereforge
git checkout -b feature/your-feature-name
# ... make changes ...
git commit -m "feat: describe your change"
git push origin feature/your-feature-name
# Open a Pull Request on GitHub
```

---

## License

MIT License — see [LICENSE](LICENSE) file for details.

---

<div align="center">

Built with 🧠 by the CereForge community.

[Report a Bug](https://github.com/Siddharthpatni/Cereforge/issues) ·
[Request a Feature](https://github.com/Siddharthpatni/Cereforge/issues) ·
[Join the Discussion](https://github.com/Siddharthpatni/Cereforge/discussions)

</div>
