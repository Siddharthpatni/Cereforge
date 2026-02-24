"""Tests for leaderboard endpoint."""

import pytest
from tests.conftest import register_user, auth_headers


@pytest.mark.asyncio
async def test_leaderboard_returns_users(client):
    """GET /leaderboard returns 200 with at least 1 user."""
    data = await register_user(client, username="lb_user1")
    token = data["access_token"]
    resp = await client.get("/api/v1/leaderboard", headers=auth_headers(token))
    assert resp.status_code == 200
    body = resp.json()
    assert "items" in body
    assert len(body["items"]) >= 1


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
async def test_current_user_position(client):
    """Leaderboard response includes current_user_position."""
    data = await register_user(client, username="lb_position")
    token = data["access_token"]
    resp = await client.get("/api/v1/leaderboard", headers=auth_headers(token))
    body = resp.json()
    assert "current_user_position" in body
    assert isinstance(body["current_user_position"], int)
    assert body["current_user_position"] >= 1
