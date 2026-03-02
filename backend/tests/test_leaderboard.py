"""Tests for leaderboard endpoint."""

from __future__ import annotations


import pytest

from tests.conftest import auth_headers, register_user


@pytest.mark.asyncio
async def test_leaderboard_returns_users(client):
    """GET /leaderboard returns 200 with at least 1 user and pagination fields."""
    data = await register_user(client, username="lb_user1")
    token = data["access_token"]
    resp = await client.get("/api/v1/leaderboard", headers=auth_headers(token))
    assert resp.status_code == 200
    body = resp.json()
    assert "items" in body
    assert len(body["items"]) >= 1
    # New pagination fields
    assert "total" in body
    assert "pages" in body
    assert body["total"] >= 1


@pytest.mark.asyncio
async def test_leaderboard_sorted_by_xp(client):
    """Leaderboard is sorted by XP descending."""
    data = await register_user(client, username="lb_sorted")
    token = data["access_token"]
    resp = await client.get("/api/v1/leaderboard", headers=auth_headers(token))
    items = resp.json()["items"]
    xp_values = [item["xp"] for item in items]
    assert xp_values == sorted(xp_values, reverse=True)


@pytest.mark.asyncio
async def test_current_user_rank(client):
    """Leaderboard response includes current_user_rank with rank, total_xp, tasks_completed."""
    data = await register_user(client, username="lb_rank_check")
    token = data["access_token"]
    resp = await client.get("/api/v1/leaderboard", headers=auth_headers(token))
    body = resp.json()
    assert "current_user_rank" in body
    rank_info = body["current_user_rank"]
    assert "rank" in rank_info
    assert "total_xp" in rank_info
    assert "tasks_completed" in rank_info
    assert isinstance(rank_info["rank"], int)
    assert rank_info["rank"] >= 1
