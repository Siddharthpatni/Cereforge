# NeuralForge

An open-source, Kaggle-inspired competitive learning platform for Artificial Intelligence and Machine Learning engineers. NeuralForge gamifies the AI learning experience with structured paths, daily challenges, peer review, and automated mentor feedback.

![NeuralForge UI](/frontend/public/vite.svg) {/* Placeholder for actual hero image */}

## Features

- **Gamified Progression**: Earn XP and rank up from *Initiate* to *Archmage* by completing ML tasks.
- **Badge Engine**: Unlock achievements for specific milestones (e.g., First LLM deployment, 5-day streaks).
- **Curriculum Paths**: Structured sequences of modules leading from beginner concepts to advanced Agents and RAG.
- **Interactive Community**: Share solutions, upvote helpful answers, and mark comments as accepted solutions (StackOverflow style).
- **AI Mentor Integration**: Hooked into Anthropic's Claude API to provide intelligent code hints, beginner guides, and automated forum summaries.
- **Beautiful UI**: Built with React, TailwindCSS, glassmorphism, and Framer Motion for cinematic badge reveals.

## Architecture

NeuralForge is built cleanly separated into a robust async backend and a reactive frontend:

- **Backend Component**: `FastAPI` + `SQLAlchemy 2.0` + `PostgreSQL` + `Redis` + `Celery`.
  - Asynchronous database interactions via `asyncpg`.
  - Background task processing for email sending and complex badge computation.
  - JWT-based authentication system.
- **Frontend Component**: `React 18` + `Vite` + `Zustand` + `TailwindCSS` + `React Router v6`.
  - Complete custom design system.
  - Real-time animated XP counters and cinematic modals.
  - Interceptors for automatic access token refreshing.

## Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) & Docker Compose
- Node.js 18+ (if running frontend outside container)
- Python 3.11+ (if running backend outside container)

### Running with Docker (Recommended)

The easiest way to get NeuralForge running locally is via Docker Compose.

1. Clone the repository:
   ```bash
   git clone https://github.com/Siddharthpatni/Cereforge.git
   cd Cereforge
   ```

2. Configure environment variables. 
   Copy the `backend/.env.example` to `backend/.env` and update values if necessary (especially `ANTHROPIC_API_KEY` if you want AI mentor features):
   ```bash
   cp backend/.env.example backend/.env
   ```

3. Start all services:
   ```bash
   docker compose up --build -d
   ```

4. **Initialize DB & Seed Data**: In a separate terminal, run the Alembic migrations and the seeder script to populate tasks, badges, and learning paths:
   ```bash
   docker exec -it neuralforge_api alembic upgrade head
   docker exec -it neuralforge_api python -m app.seeds.run_all
   ```

5. **Access the application**:
   - Web Platform: `http://localhost:5173`
   - API Docs (Swagger): `http://localhost:8000/docs`

### Running Locally (Without Docker)

#### Backend Setup

1. Open `backend/` directory.
2. Create virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in your local Postgres/Redis credentials.
4. Run migrations: `alembic upgrade head`
5. Seed database: `python -m app.seeds.run_all`
6. Start dev server: `uvicorn app.main:app --reload`

#### Frontend Setup

1. Open `frontend/` directory.
2. Install dependencies: `npm install`
3. Start dev server: `npm run dev`

## API Documentation

The backend exposes an interactive OpenAPI (Swagger) interface. When the backend is running, navigate to `/docs` (e.g., `http://localhost:8000/docs`) to explore all available endpoints, required parameters, and models.

## Development & CI/CD

This project includes a `.github/workflows/ci.yml` pipeline that triggers on pulls and pushes to `main`. It automatically:
- Provisions isolated PostgreSQL & Redis containers
- Runs `flake8` and `black` linting on backend
- Executes all `pytest` suites
- Verifies frontend builds correctly without errors

## Contact

Siddharth Patni - [@siddharthpatni]
