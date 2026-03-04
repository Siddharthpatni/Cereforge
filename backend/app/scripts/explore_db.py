import asyncio

import asyncpg

from app.core.config import settings


async def explore():
    # Parse asyncpg URL (remove the +asyncpg if present, though settings.DATABASE_URL usually is fine)
    url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")

    try:
        conn = await asyncpg.connect(url)
        print(f"--- Database Exploration: {settings.APP_NAME} ---")
        print(f"Status: Connected to {url.split('@')[1]}")
        print("-" * 40)

        # Get tables
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)

        print(f"{'Table':<25} | {'Rows':<10}")
        print("-" * 40)

        for record in sorted(tables, key=lambda x: x["table_name"]):
            table = record["table_name"]
            count = await conn.fetchval(f"SELECT COUNT(*) FROM {table}")
            print(f"{table:<25} | {count:<10}")

        print("\n--- User Credentials Dump ---")
        print(f"{'ID':<38} | {'Username':<15} | {'Password Hash (First 20)'}")
        print("-" * 80)

        users = await conn.fetch("SELECT id, username, email, password_hash FROM users")
        for u in users:
            phash = u["password_hash"][:20] + "..." if u["password_hash"] else "None"
            print(f"{str(u['id']):<38} | {u['username']:<15} | {u['email']:<25} | {phash}")

        print("-" * 80)
        await conn.close()

    except Exception as e:
        print(f"Error connecting to database: {e}")


if __name__ == "__main__":
    asyncio.run(explore())
