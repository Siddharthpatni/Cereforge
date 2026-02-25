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
- [Architecture & Tech Stack](#architecture--tech-stack)
- [Features](#features)
- [System Integrity Updates](#system-integrity-updates)
- [Quick Start](#quick-start)
- [Running with Docker](#running-with-docker)
- [Manual Setup](#manual-setup)
- [API Documentation](#api-documentation)
- [Running Tests](#running-tests)
- [Contributing](#contributing)

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

## Architecture & Tech Stack

CereForge is built on a modern, decoupled architecture designed for high throughput and robust state management.

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.11, FastAPI, SQLAlchemy 2.0 (async), Alembic |
| **Database** | PostgreSQL 15 |
| **Cache** | Redis 7 |
| **Auth** | JWT (access + refresh tokens), bcrypt |
| **Frontend** | React 18, Vite, Tailwind CSS |
| **State** | Zustand (UI state & rehydration), React Router DOM, React Suspense |
| **AI** | Anthropic Claude (AI Mentor feature) |
| **Containers** | Docker, Docker Compose |
| **CI/CD** | GitHub Actions |

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

---

## System Integrity Updates

CereForge has undergone extensive infrastructural hardening to ensure stable CI/CD deployments and rock-solid React mount lifetimes:

### 1. Robust API Routing & Pytest Integrity
- **Community & Voting Routes mapped:** Both `community.router` and `vote_router` instances are precisely mounted into the `main.py` entrypoint, eliminating 404 endpoint misses during unit testing.
- **SQLAlchemy Safeguards:** The platform mitigates "fully NULL primary key" warnings by deliberately flushing transactions and hydrating newly committed objects prior to lazy-loading deeply connected relationships like User Profiles and Authors.
- **Dependency Upgrades:** Replaced deprecated `passlib` hashing with native `bcrypt` encoding, safeguarding future Python compatibility.

### 2. CI/CD Database Normalization
The GitHub Actions workflow reliably boots testing environments using decoupled configurations:
- Custom container execution flags (`--health-cmd "pg_isready -U cereforge"`) prevent Docker from falsely pinging PostgreSQL instances via the OS default `root` role.
- Dynamic `TEST_DATABASE_URL` injections ensure the Pytest suite ignores local SQLite fallbacks, integrating seamlessly with the ephemeral Postgres orchestration on CI.

### 3. Frontend React Suspense Boundaries
- The application guarantees zero blank-page crashes on delayed network states by wrapping `App.jsx` entrypoints within `React.Suspense`. 
- Graceful degradation through aesthetic `PageSkeleton` components provide a premium loading experience.
- The `authStore.js` integrates a Zustand-persistent `isInitializing` lock, preventing the UI DOM from ever painting protected elements until identity verification calls completely resolve.

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

## Running Test Suites

**Backend Testing Segment** (Reaches 100% Coverage Pass Rates)
```bash
cd backend
source venv/bin/activate

# Execute all tests targeting the FastApi core architecture
pytest tests/ -v

# Analyze branch and missing line test coverage
pytest tests/ -v --cov=app --cov-report=term-missing
```

**Frontend Rendering Checks**
```bash
cd frontend
npm run test -- --run
```

---

## Contributing

Contributions are welcome! Focus areas include:
- New challenge tasks and engineering content matrices.
- Optimizing React rendering chunks.

**Before submitting a PR:**
1. Open an issue first to discuss the change
2. Ensure the GitHub Actions CI Pipeline remains fully green!
3. All tests must pass: `pytest tests/` and `npm run test -- --run`

```bash
git clone https://github.com/your-username/Cereforge.git
git checkout -b feature/your-feature-name
git commit -m "feat: describe your change"
git push origin feature/your-feature-name
```

---

## License

MIT License — see [LICENSE](LICENSE) file for details.
