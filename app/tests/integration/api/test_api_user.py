from collections.abc import Callable

import pytest
from faker.proxy import Faker
from httpx import AsyncClient

from core.config import settings

pytestmark = pytest.mark.asyncio(loop_scope="session")
TEST_PATH = settings.API_V1_STR


async def test_me_rout(client: AsyncClient, fake: Faker, user_factory: Callable) -> None:  # NOQA: ARG001
    email = "login@example.com"
    password = "secret"
    await user_factory(email=email, password=password)

    form_data = {"username": email, "password": password}

    response = await client.post(
        f"{TEST_PATH}/auth/token",
        data=form_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200, response.text
    token_data = response.json()["data"]
    assert token_data["access_token"]
    assert token_data["token_type"] == "Bearer"

    me_response = await client.get(
        f"{TEST_PATH}/users/me", headers={"Authorization": f"Bearer {token_data['access_token']}"}
    )
    assert me_response.status_code == 200, me_response.text
    me_data = me_response.json()["data"]
    assert me_data["email"] == email
