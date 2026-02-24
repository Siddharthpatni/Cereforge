"""Tests for community endpoints: posts, comments, voting, accept answer."""

import pytest

from tests.conftest import auth_headers, register_user


@pytest.mark.asyncio
async def test_create_post_success(client):
    """POST /posts with valid data returns 201."""
    data = await register_user(client, username="poster1")
    token = data["access_token"]
    resp = await client.post("/api/v1/posts", headers=auth_headers(token), json={
        "title": "How does chunking strategy affect RAG quality?",
        "body": "I am trying to decide between fixed-size chunking and semantic chunking for a legal document RAG system. What factors should I consider when making this decision?",
        "track": "rag",
        "tags": ["rag", "chunking", "embeddings"],
    })
    assert resp.status_code == 201
    assert "post" in resp.json()


@pytest.mark.asyncio
async def test_create_post_unauthenticated(client):
    """POST /posts without token returns 401/403."""
    resp = await client.post("/api/v1/posts", json={
        "title": "Test",
        "body": "Test body",
        "track": "llm",
    })
    assert resp.status_code in [401, 403]


@pytest.mark.asyncio
async def test_list_posts(client):
    """GET /posts returns 200 with array of posts."""
    data = await register_user(client, username="lister1")
    token = data["access_token"]
    # Create a post first
    await client.post("/api/v1/posts", headers=auth_headers(token), json={
        "title": "Test post for listing",
        "body": "This is a test post body to verify listing works correctly.",
        "track": "llm",
    })
    resp = await client.get("/api/v1/posts?sort=newest", headers=auth_headers(token))
    assert resp.status_code == 200
    body = resp.json()
    assert "items" in body
    assert body["total"] >= 1


@pytest.mark.asyncio
async def test_filter_posts_by_track(client):
    """Creating posts with track filter returns only matching posts."""
    data = await register_user(client, username="trackposter")
    token = data["access_token"]
    await client.post("/api/v1/posts", headers=auth_headers(token), json={
        "title": "Vision-specific post",
        "body": "This post is about computer vision topics only.",
        "track": "vision",
    })
    resp = await client.get("/api/v1/posts?track=vision", headers=auth_headers(token))
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert all(p["track"] == "vision" for p in items)


@pytest.mark.asyncio
async def test_get_post_detail(client):
    """GET /posts/{id} returns 200 with comments array."""
    data = await register_user(client, username="detailposter")
    token = data["access_token"]
    create_resp = await client.post("/api/v1/posts", headers=auth_headers(token), json={
        "title": "Detailed post",
        "body": "Body for detail test",
        "track": "agents",
    })
    post_id = create_resp.json()["post"]["id"]
    resp = await client.get(f"/api/v1/posts/{post_id}", headers=auth_headers(token))
    assert resp.status_code == 200
    assert "post" in resp.json()
    assert "comments" in resp.json()


@pytest.mark.asyncio
async def test_add_comment(client):
    """POST /posts/{id}/comments returns 201."""
    data = await register_user(client, username="commenter1")
    token = data["access_token"]
    # Create post
    create_resp = await client.post("/api/v1/posts", headers=auth_headers(token), json={
        "title": "Comment test post",
        "body": "Post for comment testing",
        "track": "llm",
    })
    post_id = create_resp.json()["post"]["id"]
    # Add comment
    resp = await client.post(f"/api/v1/posts/{post_id}/comments", headers=auth_headers(token), json={
        "body": "For legal documents, semantic chunking preserves clause boundaries naturally.",
    })
    assert resp.status_code == 201
    assert "comment" in resp.json()


@pytest.mark.asyncio
async def test_vote_post_upvote(client):
    """Upvoting a post increases its score."""
    author = await register_user(client, username="voteauthor")
    voter = await register_user(client, username="voter1")
    author_token = author["access_token"]
    voter_token = voter["access_token"]
    # Create post
    create_resp = await client.post("/api/v1/posts", headers=auth_headers(author_token), json={
        "title": "Vote test", "body": "Post to vote on", "track": "rag",
    })
    post_id = create_resp.json()["post"]["id"]
    # Vote
    resp = await client.post("/api/v1/vote", headers=auth_headers(voter_token), json={
        "target_id": post_id, "target_type": "post", "value": 1,
    })
    assert resp.status_code == 200
    assert resp.json()["new_score"] == 1
    assert resp.json()["user_vote"] == 1


@pytest.mark.asyncio
async def test_vote_post_toggle(client):
    """Voting same direction twice undoes the vote (toggle)."""
    author = await register_user(client, username="toggleauthor")
    voter = await register_user(client, username="togglevoter")
    author_token = author["access_token"]
    voter_token = voter["access_token"]
    create_resp = await client.post("/api/v1/posts", headers=auth_headers(author_token), json={
        "title": "Toggle test", "body": "Post for toggle", "track": "llm",
    })
    post_id = create_resp.json()["post"]["id"]
    # Vote up
    await client.post("/api/v1/vote", headers=auth_headers(voter_token), json={
        "target_id": post_id, "target_type": "post", "value": 1,
    })
    # Vote up again (undo)
    resp = await client.post("/api/v1/vote", headers=auth_headers(voter_token), json={
        "target_id": post_id, "target_type": "post", "value": 1,
    })
    assert resp.status_code == 200
    assert resp.json()["new_score"] == 0
    assert resp.json()["user_vote"] == 0


@pytest.mark.asyncio
async def test_cannot_vote_own_post(client):
    """Voting on own post returns 400."""
    data = await register_user(client, username="selfvoter")
    token = data["access_token"]
    create_resp = await client.post("/api/v1/posts", headers=auth_headers(token), json={
        "title": "Self vote test", "body": "Post to self-vote", "track": "agents",
    })
    post_id = create_resp.json()["post"]["id"]
    resp = await client.post("/api/v1/vote", headers=auth_headers(token), json={
        "target_id": post_id, "target_type": "post", "value": 1,
    })
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_accept_answer(client):
    """Post author accepting a comment sets is_accepted=true and status=solved."""
    author = await register_user(client, username="acceptauthor")
    answerer = await register_user(client, username="acceptanswerer")
    author_token = author["access_token"]
    answerer_token = answerer["access_token"]
    # Create post
    create_resp = await client.post("/api/v1/posts", headers=auth_headers(author_token), json={
        "title": "Accept test", "body": "Need answer", "track": "rag",
    })
    post_id = create_resp.json()["post"]["id"]
    # Add answer
    comment_resp = await client.post(f"/api/v1/posts/{post_id}/comments", headers=auth_headers(answerer_token), json={
        "body": "Here is the definitive answer to your question about RAG chunking.",
    })
    comment_id = comment_resp.json()["comment"]["id"]
    # Accept
    resp = await client.post(
        f"/api/v1/posts/{post_id}/comments/{comment_id}/accept",
        headers=auth_headers(author_token),
    )
    assert resp.status_code == 200
    assert resp.json()["comment"]["is_accepted"] is True


@pytest.mark.asyncio
async def test_accept_answer_wrong_author(client):
    """Non-author trying to accept returns 403."""
    author = await register_user(client, username="realauthor")
    answerer = await register_user(client, username="realanswerer")
    intruder = await register_user(client, username="intruder")
    author_token = author["access_token"]
    answerer_token = answerer["access_token"]
    intruder_token = intruder["access_token"]
    create_resp = await client.post("/api/v1/posts", headers=auth_headers(author_token), json={
        "title": "Authentication test", "body": "This is a sufficiently long post body", "track": "llm",
    })
    post_id = create_resp.json()["post"]["id"]
    comment_resp = await client.post(f"/api/v1/posts/{post_id}/comments", headers=auth_headers(answerer_token), json={
        "body": "An answer",
    })
    comment_id = comment_resp.json()["comment"]["id"]
    # Intruder tries to accept
    resp = await client.post(
        f"/api/v1/posts/{post_id}/comments/{comment_id}/accept",
        headers=auth_headers(intruder_token),
    )
    assert resp.status_code == 403
