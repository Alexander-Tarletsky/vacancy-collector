from collections.abc import Callable

import pytest
from faker.proxy import Faker

from core.config import settings

pytestmark = pytest.mark.asyncio(loop_scope="session")
TEST_PATH = settings.API_V1_STR


async def test_me_rout(client: Callable, fake: Faker, user_factory: Callable) -> None:  # NOQA: ARG001
    email = "login@example.com"
    password = "secret"
    await user_factory(email=email, password=password)

    # Create a new user
    async with await client(email, password) as auth_cl:
        response = await auth_cl.get(f"{TEST_PATH}/users/me")

    assert response.status_code == 200, response.text
    me_data = response.json()["data"]
    assert me_data["email"] == email
