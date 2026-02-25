"""Run all seeders — invoke with: python -m app.seeds.run_all"""

from __future__ import annotations

import asyncio

from app.core.database import async_session_factory
from app.seeds.badges_seed import seed_badges
from app.seeds.community_seed import seed_community
from app.seeds.paths_seed import seed_paths
from app.seeds.tasks_seed import seed_tasks


async def run_all_seeds():
    print("🌱 Starting CereForge seed process...")
    async with async_session_factory() as db:
        await seed_tasks(db)
        await seed_badges(db)
        await seed_paths(db)
        await seed_community(db)
    print("✅ All seeds completed successfully!")


if __name__ == "__main__":
    asyncio.run(run_all_seeds())
