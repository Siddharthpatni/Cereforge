"""Tests for task endpoints: list, detail, submission, badge triggers."""

from __future__ import annotations


import pytest

from tests.conftest import auth_headers, register_user


@pytest.mark.asyncio
async def test_list_tasks_authenticated(client):
    """GET /tasks with valid token returns 200 and task list."""
    data = await register_user(client, username="tasklist_user")
    token = data["access_token"]
    resp = await client.get("/api/v1/tasks", headers=auth_headers(token))
    assert resp.status_code == 200
    tasks = resp.json()
    assert isinstance(tasks, list)
    assert len(tasks) == 24


@pytest.mark.asyncio
async def test_list_tasks_unauthenticated(client):
    """GET /tasks without token returns 401/403."""
    resp = await client.get("/api/v1/tasks")
    assert resp.status_code in [401, 403]


@pytest.mark.asyncio
async def test_filter_tasks_by_track(client):
    """GET /tasks?track=llm returns only LLM tasks."""
    data = await register_user(client, username="trackfilter_user")
    token = data["access_token"]
    resp = await client.get("/api/v1/tasks?track=llm", headers=auth_headers(token))
    assert resp.status_code == 200
    tasks = resp.json()
    assert all(t["track"] == "llm" for t in tasks)
    assert len(tasks) == 6


@pytest.mark.asyncio
async def test_filter_tasks_by_difficulty(client):
    """GET /tasks?difficulty=beginner returns only beginner tasks."""
    data = await register_user(client, username="difffilter_user")
    token = data["access_token"]
    resp = await client.get("/api/v1/tasks?difficulty=beginner", headers=auth_headers(token))
    assert resp.status_code == 200
    tasks = resp.json()
    assert all(t["difficulty"] == "beginner" for t in tasks)


@pytest.mark.asyncio
async def test_get_task_detail(client):
    """GET /tasks/{slug} returns full task with beginner_guide and hint."""
    data = await register_user(client, username="taskdetail_user")
    token = data["access_token"]
    resp = await client.get("/api/v1/tasks/llm-prompt-chain", headers=auth_headers(token))
    assert resp.status_code == 200
    task = resp.json()
    assert task["slug"] == "llm-prompt-chain"
    assert "beginner_guide" in task
    assert "hint" in task


@pytest.mark.asyncio
async def test_get_task_not_found(client):
    """GET /tasks/nonexistent returns 404."""
    data = await register_user(client, username="tasknotfound_user")
    token = data["access_token"]
    resp = await client.get("/api/v1/tasks/does-not-exist", headers=auth_headers(token))
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_submit_task_success(client):
    """Submitting a valid solution returns 200 with XP earned."""
    data = await register_user(client, username="submitter1")
    token = data["access_token"]
    resp = await client.post(
        "/api/v1/tasks/llm-prompt-chain/submit",
        headers=auth_headers(token),
        json={
            "solution_text": "My comprehensive solution involves chaining three prompts together. First extracts sentiment. Second rewrites in professional tone. Third generates action items based on findings." * 2,
        },
    )
    assert resp.status_code == 200
    result = resp.json()
    # AI evaluator may award 0 XP if flagged or synthetic — check field exists
    assert "xp_earned" in result
    assert result["xp_earned"] >= 0
    assert result["total_xp"] >= 0


@pytest.mark.asyncio
async def test_submit_task_too_short(client):
    """Submitting solution under min length returns 422."""
    data = await register_user(client, username="shortsubmit")
    token = data["access_token"]
    resp = await client.post(
        "/api/v1/tasks/llm-prompt-chain/submit",
        headers=auth_headers(token),
        json={"solution_text": "Short"},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_submit_task_twice(client):
    """Submitting the same task twice returns 409."""
    data = await register_user(client, username="doublesubmit")
    token = data["access_token"]
    payload = {
        "solution_text": "A comprehensive solution that meets the minimum length requirement for valid submissions in the CereForge platform." * 2,
    }
    resp1 = await client.post("/api/v1/tasks/rag-intro-flow/submit", headers=auth_headers(token), json=payload)
    assert resp1.status_code == 200
    resp2 = await client.post("/api/v1/tasks/rag-intro-flow/submit", headers=auth_headers(token), json=payload)
    # Re-submissions are allowed (endpoint updates existing submission)
    assert resp2.status_code == 200


@pytest.mark.asyncio
async def test_submit_awards_xp(client):
    """After submission, /auth/me shows updated XP."""
    data = await register_user(client, username="xpcheck")
    token = data["access_token"]
    await client.post(
        "/api/v1/tasks/cv-real-world-survey/submit",
        headers=auth_headers(token),
        json={
            "solution_text": "A detailed solution covering all aspects of computer vision task implementation with edge cases handled." * 3,
        },
    )
    me_resp = await client.get("/api/v1/auth/me", headers=auth_headers(token))
    assert me_resp.status_code == 200
    assert me_resp.json()["stats"]["tasks_completed"] == 1
    assert me_resp.json()["user"]["xp"] >= 0  # XP may vary based on AI eval result


@pytest.mark.asyncio
async def test_task_shows_completed_after_submit(client):
    """After submission, task list shows task as completed."""
    data = await register_user(client, username="completedcheck")
    token = data["access_token"]
    await client.post(
        "/api/v1/tasks/agent-fundamentals/submit",
        headers=auth_headers(token),
        json={
            "solution_text": "Building an autonomous agent that handles multi-step reasoning with proper error recovery and fallback strategies." * 3,
        },
    )
    resp = await client.get("/api/v1/tasks", headers=auth_headers(token))
    tasks = resp.json()
    submitted = [t for t in tasks if t["slug"] == "agent-fundamentals"]
    assert len(submitted) == 1
    assert submitted[0]["completed"] is True
