# Production Setup Guide — CereForge

Follow these steps to deploy CereForge to production.

## 1. Prerequisites
- GitHub repository with the latest code pushed.
- Accounts on: [Supabase](https://supabase.com/), [Upstash](https://upstash.com/), [Render](https://render.com/), [Vercel](https://vercel.com/).

## 2. Database (Supabase)
1. Create a new project on Supabase.
2. Go to **Project Settings** > **Database**.
3. Copy the **Connection string** (URI). Note: Ensure it looks like `postgres://user:pass@host:port/db`.
4. Keep this for the Backend setup.

## 3. Redis (Upstash)
1. Create a new Redis database on Upstash (Serverless).
2. Copy the **URL** (looks like `redis://default:pass@host:port`).

## 4. Backend (Render)
1. Create a new **Web Service** on Render.
2. Connect your CereForge GitHub repository.
3. **Environment Settings**:
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. **Environment Variables**:
   - `APP_ENV`: `production`
   - `DATABASE_URL`: [Your Supabase URI]
   - `REDIS_URL`: [Your Upstash URL]
   - `APP_SECRET_KEY`: [Generate a random string, e.g., `openssl rand -hex 32`]
   - `JWT_SECRET_KEY`: [Generate a 64-char hex string, e.g., `python -c "import secrets; print(secrets.token_hex(64))"`]
   - `APP_CORS_ORIGINS`: [Your Vercel URL, e.g., `https://cereforge.vercel.app`] (You'll update this after the Frontend is live).

## 5. Frontend (Vercel)
1. Create a new project on Vercel.
2. Connect your GitHub repository.
3. **Project Settings**:
   - **Root Directory**: `frontend`
   - **Framework Preset**: `Vite`
4. **Environment Variables**:
   - `VITE_API_BASE_URL`: [Your Render Backend URL]/api/v1 (e.g., `https://cereforge-api.onrender.com/api/v1`)
5. Deploy and copy your Vercel URL.

## 6. Final Sync
1. Go back to your **Render** settings and update the `APP_CORS_ORIGINS` with your new Vercel URL.
2. Visit your Vercel URL and verify you can Register/Login.
