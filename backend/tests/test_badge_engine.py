"""Tests for the badge engine: badge awards on task completion."""

from __future__ import annotations


import pytest

from tests.conftest import auth_headers, register_user

SOLUTION_TEXT = "A comprehensive detailed solution that demonstrates understanding of the underlying concepts, covers edge cases, and provides a complete implementation with error handling and testing." * 2


async def submit_task(client, token: str, slug: str):
    """Helper to submit a task."""
    return await client.post(
        f"/api/v1/tasks/{slug}/submit",
        headers=auth_headers(token),
        json={"solution_text": SOLUTION_TEXT},
    )


@pytest.mark.asyncio
async def test_first_task_awards_zero_to_ai(client):
    """Absolute beginner submitting first task gets 'zero-to-ai' badge."""
    data = await register_user(client, username="badge_first", skill_level="absolute_beginner")
    token = data["access_token"]
    resp = await submit_task(client, token, "test-task-llm-0")
    assert resp.status_code == 200
    result = resp.json()
    badge_slugs = [b["slug"] for b in result.get("newly_earned_badges", [])]
    assert "zero-to-ai" in badge_slugs


@pytest.mark.asyncio
async def test_llm_task_awards_prompt_whisperer(client):
    """Submitting an LLM task awards 'prompt-whisperer' badge."""
    data = await register_user(client, username="badge_llm", skill_level="some_python")
    token = data["access_token"]
    resp = await submit_task(client, token, "test-task-llm-0")
    assert resp.status_code == 200
    result = resp.json()
    badge_slugs = [b["slug"] for b in result.get("newly_earned_badges", [])]
    assert "prompt-whisperer" in badge_slugs


@pytest.mark.asyncio
async def test_all_llm_tasks_awards_chain_master(client):
    """Completing all 3 LLM tasks awards 'chain-master' badge."""
    data = await register_user(client, username="badge_chain")
    token = data["access_token"]
    # LLM tasks are at indices 0, 4, 8
    await submit_task(client, token, "test-task-llm-0")
    await submit_task(client, token, "test-task-llm-4")
    resp = await submit_task(client, token, "test-task-llm-8")
    assert resp.status_code == 200
    result = resp.json()
    badge_slugs = [b["slug"] for b in result.get("newly_earned_badges", [])]
    assert "chain-master" in badge_slugs


@pytest.mark.asyncio
async def test_one_per_track_awards_full_stack_ai(client):
    """Completing one task per track awards 'full-stack-ai' badge."""
    data = await register_user(client, username="badge_fullstack")
    token = data["access_token"]
    await submit_task(client, token, "test-task-llm-0")
    await submit_task(client, token, "test-task-rag-1")
    await submit_task(client, token, "test-task-vision-2")
    resp = await submit_task(client, token, "test-task-agents-3")
    assert resp.status_code == 200
    result = resp.json()
    badge_slugs = [b["slug"] for b in result.get("newly_earned_badges", [])]
    assert "full-stack-ai" in badge_slugs


@pytest.mark.asyncio
async def test_badge_awarded_once(client):
    """A badge is only awarded once even if conditions are re-met."""
    data = await register_user(client, username="badge_once")
    token = data["access_token"]
    # Submit first LLM task — gets zero-to-ai
    resp1 = await submit_task(client, token, "test-task-llm-0")
    badges1 = [b["slug"] for b in resp1.json().get("newly_earned_badges", [])]
    assert "zero-to-ai" in badges1

    # Submit second task — zero-to-ai should NOT appear again
    resp2 = await submit_task(client, token, "test-task-rag-1")
    badges2 = [b["slug"] for b in resp2.json().get("newly_earned_badges", [])]
    assert "zero-to-ai" not in badges2
