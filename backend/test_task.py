import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.models.task import Task
from app.core.config import settings

async def main():
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as db:
        result = await db.execute(select(Task).where(Task.slug == "llm-prompt-chain"))
        task = result.scalar_one_or_none()
        if not task:
            print("Task not found")
            return
        
        d = task.__dict__
        for k, v in d.items():
            if not k.startswith("_"):
                print(f"{k}: {type(v).__name__} = {repr(v)[:100]}")

asyncio.run(main())
