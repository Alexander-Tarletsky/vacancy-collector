from collections.abc import Callable

import pytest
from faker import Faker
from httpx import AsyncClient

from core.config import settings
from schemas.user import UserCreate

# Marks all test coroutines in this module with the asyncio marker
pytestmark = pytest.mark.asyncio(loop_scope="session")

TEST_PATH = f"{settings.API_V1_STR}/auth"


async def test_register_success(client: AsyncClient, fake: Faker, get_test_user_data: dict) -> None:
    user = get_test_user_data

    # response = await client.post("/auth/register", json=user)
    response = await client.post(f"{TEST_PATH}/register", json=user)
    assert response.status_code == 201, response.text
    json_data = response.json()
    assert json_data["message"] == "Successfully registered"
    assert json_data["data"]["email"] == user["email"]


async def test_register_duplicate(client: AsyncClient, user_factory: Callable) -> None:
    email = "duplicate@example.com"
    await user_factory(email=email)

    # Attempt to register the same user again
    user = UserCreate(
        email=email,
        password="secret",
        api_id="api_id",
        api_hash="api_hash",
    ).model_dump()

    response = await client.post(f"{TEST_PATH}/register", json=user)
    assert response.status_code == 400, response.text
    json_data = response.json()
    assert json_data["detail"] == "User with this email already exists"


async def test_login_success(client: AsyncClient, user_factory: Callable) -> None:
    email = "login@example.com"
    password = "secret"
    await user_factory(email=email, password=password)

    form_data = {
        "username": email,
        "password": password
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = await client.post(f"{TEST_PATH}/token", data=form_data, headers=headers)
    assert response.status_code == 200, response.text
    token_data = response.json()["data"]
    assert token_data["access_token"]
    assert token_data["token_type"] == "Bearer"


async def test_login_fail(client: AsyncClient, user_factory: Callable) -> None:
    await user_factory(email="login@example.com", password="secret")
    form_data = {
        "username": "nonexistent@example.com",
        "password": "wrongpassword"
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    response = await client.post(f"{TEST_PATH}/token", data=form_data, headers=headers)
    assert response.status_code == 401, response.text
