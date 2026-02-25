<div align="center">
  <img src="docs/screenshots/dashboard.png" alt="CereForge Dashboard" width="100%" />

  # 🧠 CereForge
  **The AI & Autonomous Systems Learning Platform**
  
  <p>
    > <b>Forge Your AI Mind.</b> Build real AI engineering skills through structured challenges,
    > earn XP and badges, and get help from a community of engineers who've been exactly
    > where you are.
  </p>

  [![CI](https://github.com/Siddharthpatni/Cereforge/actions/workflows/ci.yml/badge.svg)](https://github.com/Siddharthpatni/Cereforge/actions)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
  [![React 18](https://img.shields.io/badge/react-18-61dafb.svg)](https://react.dev/)

</div>

---

## ✨ Features & Interface

CereForge is not just another tutorial site. It's a gamified, hands-on proving ground tailored for modern **AI & Autonomous Systems**.

### 🔐 Seamless Authentication & Onboarding
Dive straight into your AI journey. Our intuitive onboarding customizes your learning path based on your existing skill level.

<div align="center">
  <img src="docs/screenshots/auth.png" alt="Auth Screen" width="800" />
</div>

### 🎯 Structured Task System
Tackle 12 progressive AI engineering challenges covering:
- **LLM Engineering** (Prompt chains, token optimization)
- **RAG Pipelines** (Vector stores, chunking, hallucination guardrails)
- **Computer Vision** (Multimodal systems, YOLO, object detection)
- **Autonomous Agents** (LangChain, LangGraph, Multi-Agent systems)

<div align="center">
  <img src="docs/screenshots/tasks.png" alt="Task Listing" width="800" />
</div>

### 💬 Vibrant Community
Ask questions, share solutions, and vote on the best answers. Our Stack Overflow-style forum encourages collaboration and rewards helpful contributors with bonus XP and badges like *Community Sage*.

<div align="center">
  <img src="docs/screenshots/post.png" alt="Community Post" width="800" />
</div>

---

## 🏗️ Architecture & Tech Stack

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

## � Quick Start

The fastest way to run CereForge locally:

```bash
# 1. Clone the repository
git clone https://github.com/Siddharthpatni/Cereforge.git
cd Cereforge

# 2. Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# 3. Start everything with Docker
docker compose up --build -d

# 4. In a new terminal, run database migrations and seed data
docker compose exec backend alembic upgrade head
docker compose exec backend python -m app.seeds.run_all

# 5. Open your browser
open http://localhost:5173
```

The API docs are available at `http://localhost:8000/docs`

---

## 🧪 Running Test Suites

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
npm run lint
npm run build
```

---

## 🤝 Contributing

Contributions are welcome! Focus areas include:
- New challenge tasks and engineering content matrices.
- Optimizing React rendering chunks.

**Before submitting a PR:**
1. Open an issue first to discuss the change
2. Ensure the GitHub Actions CI Pipeline remains fully green!
3. All tests must pass: `pytest tests/` and `npm run lint`

```bash
git clone https://github.com/your-username/Cereforge.git
git checkout -b feature/your-feature-name
git commit -m "feat: describe your change"
git push origin feature/your-feature-name
```

---

## 📄 License

MIT License — see [LICENSE](LICENSE) file for details.
