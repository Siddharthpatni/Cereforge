import asyncio

from sqlalchemy import text

from app.core.database import async_session_factory


async def wipe_database():
    print("🧹 Wiping all test data from Cereforge...")
    tables = [
        "notifications",
        "comments",
        "votes",
        "post_bookmarks",
        "posts",
        "path_enrollments",
        "user_badges",
        "task_submissions",
        "users",
    ]

    async with async_session_factory() as db:
        for table in tables:
            print(f"   - Truncating {table}...")
            # Use CASCADE to handle foreign key dependencies
            await db.execute(text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE;"))

        await db.commit()
    print("✅ Database wiped successfully!")


if __name__ == "__main__":
    asyncio.run(wipe_database())
