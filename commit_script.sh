#!/bin/bash
git config --global user.name "Siddharth Patni"
git config --global user.email "siddharthpatni@example.com"

git reset HEAD

git add backend/app/main.py backend/app/api/routes/community.py backend/app/api/routes/__init__.py
git commit -m "refactor(api): include community and vote routers in main.py"

git add backend/app/api/routes/auth.py
git commit -m "fix(auth): execute user db refresh before returning token payloads to fix SAWarning"

git add backend/app/core/security.py
git commit -m "refactor(security): replace deprecated passlib with native bcrypt for hashing"

git add backend/tests/conftest.py
git commit -m "test: replace custom asyncio event_loop with anyio plugin configuration"

git add .github/workflows/ci.yml
git commit -m "ci: append specific user flag to postgres healthcheck and wire TEST_DATABASE_URL"

git add backend/app/models/
git commit -m "build(python): apply Optional typehints across models for python 3.9 compatibility"

git add backend/app/schemas/
git commit -m "build(python): refactor schemas to suppress python 3.9 union operator evaluation crashes"

git add backend/app/core/config.py backend/app/api/deps.py backend/app/core/database.py backend/app/core/redis.py
git commit -m "refactor(core): utilize __future__ annotations for cross-version hinting"

git add backend/app/api/routes/ backend/app/services/ backend/app/workers/ backend/app/__init__.py backend/app/api/__init__.py backend/app/seeds/
git commit -m "refactor(services): inject global annotations context"

git add backend/fix_annotations.py backend/fix_models.py backend/fix_utc.py
git commit -m "chore(scripts): add AST modification utilities for syntax down-leveling"

git add backend/test.db backend/tests/
git commit -m "test: align integration tests with structural endpoint modifications"

git add frontend/src/components/ui/PageSkeleton.jsx frontend/src/App.jsx
git commit -m "feat(ui): build PageSkeleton fallback and wrap App routing tree in React Suspense"

git add frontend/src/stores/authStore.js
git commit -m "fix(auth): implement isInitializing mount lock in Auth Zustand Store to prevent render crashing"

git add README.md
git commit -m "docs: completely rewrite professional README.md with architecture overview"

# Just in case there are trailing files left behind:
git add .
git commit -m "chore: formatting and miscellaneous environment updates"

git push
