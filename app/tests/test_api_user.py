import pytest
from httpx import AsyncClient
from app.db.models import UserORM


@pytest.mark.asyncio
async def test_register_user(async_client: AsyncClient):
    response = await async_client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "securepassword"
    })
    assert response.status_code == 201
    assert response.json()["message"] == "Successfully registered user"


@pytest.mark.asyncio
async def test_login_user(async_client: AsyncClient):
    response = await async_client.post("/auth/login", data={
        "username": "test@example.com",
        "password": "securepassword"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()["data"]


@pytest.mark.asyncio
async def test_login_invalid_credentials(async_client: AsyncClient):
    response = await async_client.post("/auth/login", data={
        "username": "wrong@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    assert response.json()["message"] == "Invalid credentials"


@pytest.mark.asyncio
async def test_login_inactive_user(async_client: AsyncClient, test_db_session):
    inactive_user = UserORM(email="inactive@example.com", password_hash="hashed", is_active=False)
    test_db_session.add(inactive_user)
    await test_db_session.commit()

    response = await async_client.post("/auth/login", data={
        "username": "inactive@example.com",
        "password": "securepassword"
    })
    assert response.status_code == 403
    assert response.json()["message"] == "User is inactive"
