#!/bin/bash

# ==============================================================================
# CereForge - Quick Start Demo Script
# ==============================================================================
# This script is designed for reviewers, professors, or anyone who wants to 
# instantly boot up the entire CereForge stack (Frontend, Backend, DB, Redis)
# without needing to manually configure environment variables or run migrations.
#
# Requirements: 
# - Docker Desktop installed and running
# - Git
# ==============================================================================

set -e

echo "🚀 Starting CereForge Quick Demo Setup..."

# 1. Setup Environment Variables automatically
echo "📝 Configuring environment variables..."
if [ ! -f backend/.env ]; then
    cp backend/.env.example backend/.env
    # Generate random secrets for local demo
    SECRET_APP=$(openssl rand -hex 32)
    SECRET_JWT=$(openssl rand -hex 32)
    
    # Replace the placeholder secrets in the backend .env (compatible with both GNU and BSD sed)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/APP_SECRET_KEY=.*/APP_SECRET_KEY=$SECRET_APP/" backend/.env
        sed -i '' "s/JWT_SECRET_KEY=.*/JWT_SECRET_KEY=$SECRET_JWT/" backend/.env
    else
        sed -i "s/APP_SECRET_KEY=.*/APP_SECRET_KEY=$SECRET_APP/" backend/.env
        sed -i "s/JWT_SECRET_KEY=.*/JWT_SECRET_KEY=$SECRET_JWT/" backend/.env
    fi
    echo "   ✅ Created backend/.env with secure local keys."
else
    echo "   ✅ backend/.env already exists."
fi

if [ ! -f frontend/.env ]; then
    cp frontend/.env.example frontend/.env
    echo "   ✅ Created frontend/.env."
else
    echo "   ✅ frontend/.env already exists."
fi

# 2. Start Docker Containers
echo "🐳 Building and starting Docker containers (this may take a few minutes on first run)..."
docker compose up --build -d

# 3. Wait for Database to be ready
echo "⏳ Waiting for PostgreSQL database to initialize..."
until docker compose exec db pg_isready -U cereforge > /dev/null 2>&1; do
  sleep 2
  echo "   ...still waiting for database..."
done
echo "   ✅ Database is ready!"

# Wait a few more seconds to ensure the backend app is fully booted and connected
sleep 5

# 4. Run Database Migrations
echo "🏗️  Running database migrations..."
docker compose exec backend alembic upgrade head
echo "   ✅ Migrations complete."

# 5. Seed the Database with Tasks and Learning Paths
echo "🌱 Seeding the database with AI tasks, users, and community posts..."
docker compose exec backend python -m app.seeds.run_all
echo "   ✅ Database seeded successfully."

echo ""
echo "====================================================================="
echo "🎉 SUCCESS! CereForge is now running locally on your machine."
echo "====================================================================="
echo ""
echo "🌐 Frontend (Web App):     http://localhost:5173"
echo "🔌 Backend API Docs:       http://localhost:8000/docs"
echo ""
echo "Test Accounts Available (Passwords are 'password123'):"
echo " - Admin:     admin@cereforge.io"
echo " - Beginner:  newuser@example.com"
echo " - Expert:    pro@example.com"
echo "====================================================================="
echo "To stop the application later, run:  docker compose down"
