import asyncio
from sqlalchemy import select
from app.core.database import async_session_factory
from app.models.post import Post

async def test_delete():
    async with async_session_factory() as db:
        post_id = "9f686cc8-d063-4ba7-9f55-676c8cecbc96"
        result = await db.execute(select(Post).where(Post.id == post_id))
        post = result.scalar_one_or_none()
        if not post:
            print("Post not found in DB")
            return
        
        post.is_deleted = True
        try:
            await db.flush()
            await db.commit()
            print("Deleted successfully")
        except Exception as e:
            print(f"Exception during delete: {e}")

if __name__ == "__main__":
    asyncio.run(test_delete())
