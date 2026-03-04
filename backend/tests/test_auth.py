"""Tests for authentication endpoints: register, login, refresh, /me."""

from __future__ import annotations


import pytest

from tests.conftest import auth_headers, register_user


@pytest.mark.asyncio
async def test_register_success(client):
    """Register with valid data returns 201 with token and user."""
    resp = await client.post("/api/v1/auth/register", json={
        "username": "newuser1",
        "email": "new1@example.com",
        "password": "SecurePass123!",
        "skill_level": "absolute_beginner",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["username"] == "newuser1"
    assert data["user"]["email"] == "new1@example.com"
    assert "password_hash" not in str(data)
    assert "welcome_message" in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    """Registering twice with the same email returns 409."""
    await client.post("/api/v1/auth/register", json={
        "username": "dupuser1",
        "email": "dup@example.com",
        "password": "SecurePass123!",
        "skill_level": "some_python",
    })
    resp = await client.post("/api/v1/auth/register", json={
        "username": "dupuser2",
        "email": "dup@example.com",
        "password": "SecurePass123!",
        "skill_level": "some_python",
    })
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_register_duplicate_username(client):
    """Registering twice with the same username returns 409."""
    await client.post("/api/v1/auth/register", json={
        "username": "sameuser",
        "email": "same1@example.com",
        "password": "SecurePass123!",
        "skill_level": "ml_familiar",
    })
    resp = await client.post("/api/v1/auth/register", json={
        "username": "sameuser",
        "email": "same2@example.com",
        "password": "SecurePass123!",
        "skill_level": "ml_familiar",
    })
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_register_invalid_email(client):
    """Registering with invalid email returns 422."""
    resp = await client.post("/api/v1/auth/register", json={
        "username": "badmail",
        "email": "notanemail",
        "password": "SecurePass123!",
        "skill_level": "absolute_beginner",
    })
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_register_short_password(client):
    """Registering with password under 8 chars returns 422."""
    resp = await client.post("/api/v1/auth/register", json={
        "username": "shortpw",
        "email": "shortpw@example.com",
        "password": "abc",
        "skill_level": "absolute_beginner",
    })
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_register_username_with_spaces(client):
    """Username with spaces should return 422 (pattern validation)."""
    resp = await client.post("/api/v1/auth/register", json={
        "username": "test user",
        "email": "spaces@example.com",
        "password": "SecurePass123!",
        "skill_level": "absolute_beginner",
    })
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_login_success(client):
    """Login with correct credentials returns 200 with tokens."""
    await register_user(client, email="login@example.com", password="LoginPass123!", username="loginuser")
    resp = await client.post("/api/v1/auth/login", json={
        "email_or_username": "login@example.com",
        "password": "LoginPass123!",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["email"] == "login@example.com"


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    """Login with wrong password returns 401, not 500."""
    await register_user(client, email="wrongpw@example.com", password="RightPass123!", username="wrongpwuser")
    resp = await client.post("/api/v1/auth/login", json={
        "email_or_username": "wrongpw@example.com",
        "password": "WrongPassword1!",
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(client):
    """Login with email that doesn't exist returns 401."""
    resp = await client.post("/api/v1/auth/login", json={
        "email_or_username": "nobody@example.com",
        "password": "Whatever123!",
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_me_authenticated(client):
    """GET /auth/me with valid token returns 200 and user object."""
    data = await register_user(client, username="meuser")
    token = data["access_token"]
    resp = await client.get("/api/v1/users/me", headers=auth_headers(token))
    assert resp.status_code == 200
    me = resp.json()
    assert me["user"]["username"] == "meuser"
    assert "rank" in me
    assert "badges" in me
    assert "stats" in me


@pytest.mark.asyncio
async def test_get_me_unauthenticated(client):
    """GET /auth/me without token returns 401/403."""
    resp = await client.get("/api/v1/users/me")
    assert resp.status_code in [401, 403]


@pytest.mark.asyncio
async def test_refresh_token(client):
    """Using refresh_token to get new access_token returns 200."""
    data = await register_user(client, username="refreshuser")
    refresh = data["refresh_token"]
    resp = await client.post("/api/v1/auth/refresh", json={
        "refresh_token": refresh,
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()


@pytest.mark.asyncio
async def test_password_never_returned(client):
    """Verify password_hash never appears in any auth response."""
    # Register
    reg_resp = await client.post("/api/v1/auth/register", json={
        "username": "nopwhash",
        "email": "nopwhash@example.com",
        "password": "SecurePass123!",
        "skill_level": "advanced",
    })
    assert "password_hash" not in reg_resp.text
    assert "hashed_password" not in reg_resp.text

    token = reg_resp.json()["access_token"]

    # Login
    login_resp = await client.post("/api/v1/auth/login", json={
        "email_or_username": "nopwhash@example.com",
        "password": "SecurePass123!",
    })
    assert "password_hash" not in login_resp.text

    # /me
    me_resp = await client.get("/api/v1/users/me", headers=auth_headers(token))
    assert "password_hash" not in me_resp.text
