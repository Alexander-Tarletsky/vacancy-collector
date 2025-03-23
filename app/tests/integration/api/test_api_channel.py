from collections.abc import Callable

import pytest
from faker import Faker
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from db import ChannelORM
from schemas.channel import ChannelCreate, ChannelUpdate

pytestmark = pytest.mark.asyncio(loop_scope="session")

TEST_PATH = f"{settings.API_V1_STR}/channels"


async def test_get_user_channel(
    client: Callable,
    user_factory: Callable,
    channel_factory: Callable,
    fake: Faker,
) -> None:
    email = fake.email(safe=True, domain="example.com")
    password = fake.password(length=8)

    user = await user_factory(email=email, password=password)
    channel = await channel_factory(user=user)

    async with await client(email, password) as auth_cl:
        response = await auth_cl.get(f"{TEST_PATH}/{channel['id']}")

    assert response.status_code == 200, response.text
    res_data = response.json()
    assert res_data["message"] == "Successfully fetched channel"
    assert res_data["data"]["id"] == str(channel["id"])
    assert res_data["data"]["telegram_id"] == str(channel["telegram_id"])


async def test_get_user_channels(
    client: Callable,
    user_factory: Callable,
    channel_factory: Callable,
    fake: Faker,
) -> None:
    email = fake.email(safe=True, domain="example.com")
    password = fake.password(length=8)
    user = await user_factory(email=email, password=password)

    await channel_factory(user=user)
    await channel_factory(user=user)

    async with await client(email, password) as auth_cl:
        response = await auth_cl.get(TEST_PATH)

    assert response.status_code == 200, response.text
    res_data = response.json()
    assert res_data["message"] == "Successfully fetched channels"
    assert len(res_data["data"]) == 2
    assert res_data["data"][0]["user_id"] == str(user["id"])
    assert res_data["data"][1]["user_id"] == str(user["id"])


async def test_create_channel(
    client: Callable,
    session: AsyncSession,
    user_factory: Callable,
    fake: Faker,
) -> None:
    email = fake.email(safe=True, domain="example.com")
    password = fake.password(length=8)

    user = await user_factory(email=email, password=password)
    channel_data = ChannelCreate(
        title=fake.sentence(),
        description=fake.text(),
        telegram_id=str(fake.uuid4()),
        user_id=user["id"],
    ).model_dump_json()

    async with await client(email, password) as auth_cl:
        response = await auth_cl.post(TEST_PATH, content=channel_data)

    assert response.status_code == 200, response.text
    response_data = response.json()
    assert response_data["status_code"] == 201

    res = await session.scalars(select(ChannelORM))
    channels = res.all()

    assert len(channels) == 1, "Channel not created in the database"
    assert channels[0].user_id == user["id"], "Channel user_id does not match"


async def test_update_channel(
    client: Callable,
    user_factory: Callable,
    channel_factory: Callable,
    fake: Faker,
) -> None:
    email = fake.email(safe=True, domain="example.com")
    password = fake.password(length=8)

    user = await user_factory(email=email, password=password)
    channel = await channel_factory(user=user)
    channel_update = ChannelUpdate(
        title="Updated Channel",
        description="Updated description",
    ).model_dump_json()

    async with await client(email, password) as auth_cl:
        response = await auth_cl.put(f"{TEST_PATH}/{channel['id']}", content=channel_update)

    assert response.status_code == 200, response.text
    res_data = response.json()
    assert res_data["message"] == "Successfully updated channel"
    assert res_data["data"]["id"] == str(channel["id"])
    assert res_data["data"]["title"] == "Updated Channel"
    assert res_data["data"]["description"] == "Updated description"


async def test_delete_channel(
    client: Callable,
    session: AsyncSession,
    user_factory: Callable,
    channel_factory: Callable,
    fake: Faker,
) -> None:
    email = fake.email(safe=True, domain="example.com")
    password = fake.password(length=8)

    user = await user_factory(email=email, password=password)
    channel = await channel_factory(user=user)

    async with await client(email, password) as auth_cl:
        response = await auth_cl.delete(f"{TEST_PATH}/{channel['id']}")

    assert response.status_code == 200, response.text
    res_data = response.json()
    assert res_data["status_code"] == 204
    assert res_data["message"] == "Successfully deleted channel"
    assert res_data["data"]["id"] == str(channel["id"])

    # Check if the channel is actually deleted from the database
    res = await session.scalars(select(ChannelORM))
    channels = res.all()

    assert len(channels) == 0, "Channel not deleted from the database"


async def test_get_non_user_channel(
    client: Callable,
    user_factory: Callable,
    channel_factory: Callable,
    fake: Faker,
) -> None:
    email = fake.email(safe=True, domain="example.com")
    password = fake.password(length=8)
    await user_factory(email=email, password=password)

    new_user = await user_factory(email=fake.email(), password=fake.password(length=8))
    channel = await channel_factory(user=new_user)

    # Attempt to access the channel with a different user
    async with await client(email, password) as auth_cl:
        response = await auth_cl.get(f"{TEST_PATH}/{channel['id']}")

    assert response.status_code == 403, response.text
    res_data = response.json()
    assert res_data["detail"] == "Access forbidden. You do not have access to this resource."


async def test_get_defunct_channel(
    client: Callable,
    user_factory: Callable,
    channel_factory: Callable,
    fake: Faker,
) -> None:
    email = fake.email(safe=True, domain="example.com")
    password = fake.password(length=8)
    user = await user_factory(email=email, password=password)
    await channel_factory(user=user)

    # Attempt to access a non-existent channel
    async with await client(email, password) as auth_cl:
        response = await auth_cl.get(f"{TEST_PATH}/{fake.uuid4()}")

    assert response.status_code == 404, response.text
