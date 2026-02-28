import asyncio
import httpx
from uuid import uuid4

# Setup client directly with an existing token, or create a quick test here
async def test_comments():
    import uuid
    async with httpx.AsyncClient(base_url="http://localhost:8000/api/v1") as client:
        # Register fresh user
        test_user = f"testuser_{uuid.uuid4().hex[:6]}"
        reg_res = await client.post("/auth/register", json={
            "username": test_user,
            "email": f"{test_user}@example.com",
            "password": "securepassword",
            "skill_level": "advanced",
            "background": "Testing"
        })
        token = reg_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # create a post
        post_res = await client.post("/posts", json={"title": "Test Title", "body": "Test body text", "tags": []}, headers=headers)
        post_id = post_res.json()["post"]["id"]

        print(f"Created post {post_id}")

        # try to comment
        comment_res = await client.post(f"/posts/{post_id}/comments", json={"body": "Test comment", "parent_id": None}, headers=headers)
        print("Comment res:", comment_res.status_code)

        # get post details
        get_res = await client.get(f"/posts/{post_id}", headers=headers)
        print("GET Post res:", get_res.status_code, get_res.text)

if __name__ == "__main__":
    asyncio.run(test_comments())
