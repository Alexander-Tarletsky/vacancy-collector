from collections.abc import Callable

import pytest
from faker import Faker
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from db import VacancyORM
from schemas.vacancy import VacancyCreate, VacancyUpdate

pytestmark = pytest.mark.asyncio(loop_scope="session")

TEST_PATH = f"{settings.API_V1_STR}/vacancies"


async def test_get_user_vacancies(
    client: Callable,
    user_factory: Callable,
    channel_factory: Callable,
    vacancy_factory: Callable,
    fake: Faker,
) -> None:
    email = fake.email(safe=True, domain="example.com")
    password = fake.password(length=8)

    user = await user_factory(email=email, password=password)
    channel = await channel_factory(user=user)
    await vacancy_factory(user=user, channel=channel)
    await vacancy_factory(user=user, channel=channel)

    async with await client(email, password) as auth_cl:
        response = await auth_cl.get(f"{TEST_PATH}")

    assert response.status_code == 200, response.text
    res_data = response.json()
    assert res_data["message"] == "Successfully fetched vacancies"
    assert len(res_data["data"]) == 2


async def test_get_channel_vacancies(
    client: Callable,
    user_factory: Callable,
    channel_factory: Callable,
    vacancy_factory: Callable,
    fake: Faker,
) -> None:
    email = fake.email(safe=True, domain="example.com")
    password = fake.password(length=8)
    user_1 = await user_factory(email=email, password=password)
    user_2 = await user_factory(email="email_user2@test.com", password="pass_user2")

    channel_1 = await channel_factory(user=user_1)
    channel_2 = await channel_factory(user=user_2)

    vacancy_1_1 = await vacancy_factory(channel=channel_1)
    vacancy_1_2 = await vacancy_factory(channel=channel_1)
    vacancy_unreadable = await vacancy_factory(channel=channel_2)

    async with await client(email, password) as auth_cl:
        response = await auth_cl.get(f"{TEST_PATH}/channel/{channel_1['id']}")

    assert response.status_code == 200, response.text
    res_data = response.json()
    assert res_data["message"] == "Successfully fetched vacancies"
    assert len(res_data["data"]) == 2
    assert res_data["data"][0]["id"] == str(vacancy_1_1["id"])
    assert res_data["data"][1]["id"] == str(vacancy_1_2["id"])

    # Attempt to access the channel with a different user
    async with await client(email, password) as auth_cl:
        response = await auth_cl.get(f"{TEST_PATH}/channel/{channel_2['id']}")

    assert response.status_code == 403, response.text
    res_data = response.json()
    assert res_data["detail"] == "Access forbidden. You do not have access to this resource."

    # Re-authenticate client with user_2
    async with await client("email_user2@test.com", "pass_user2") as auth_cl:
        response = await auth_cl.get(f"{TEST_PATH}/channel/{channel_2['id']}")

    assert response.status_code == 200, response.text
    res_data = response.json()
    assert res_data["message"] == "Successfully fetched vacancies"
    assert len(res_data["data"]) == 1
    assert res_data["data"][0]["id"] == str(vacancy_unreadable["id"])


async def test_get_vacancy(
    client: Callable,
    user_factory: Callable,
    channel_factory: Callable,
    vacancy_factory: Callable,
    fake: Faker,
) -> None:
    email = fake.email(safe=True, domain="example.com")
    password = fake.password(length=8)
    user = await user_factory(email=email, password=password)
    channel = await channel_factory(user=user)
    vacancy = await vacancy_factory(user=user, channel=channel)

    async with await client(email, password) as auth_cl:
        response = await auth_cl.get(f"{TEST_PATH}/{vacancy['id']}")

    assert response.status_code == 200, response.text
    res_data = response.json()
    assert res_data["message"] == "Successfully fetched vacancy"
    assert res_data["data"]["id"] == str(vacancy["id"])


async def test_get_non_user_vacancy(
    client: Callable,
    user_factory: Callable,
    channel_factory: Callable,
    vacancy_factory: Callable,
    fake: Faker,
) -> None:
    email = fake.email(safe=True, domain="example.com")
    password = fake.password(length=8)
    user = await user_factory(email=email, password=password)
    channel = await channel_factory(user=user)
    await vacancy_factory(user=user, channel=channel)

    new_user = await user_factory(email=fake.email(), password=fake.password(length=8))
    new_channel = await channel_factory(user=new_user)
    new_vacancy = await vacancy_factory(channel=new_channel)

    # Attempt to access the vacancy with a different user
    async with await client(email, password) as auth_cl:
        response = await auth_cl.get(f"{TEST_PATH}/{new_vacancy['id']}")

    assert response.status_code == 403, response.text
    res_data = response.json()
    assert res_data["detail"] == "Access forbidden. You do not have access to this resource."


async def test_get_not_found_vacancy(
    client: Callable,
    user_factory: Callable,
    channel_factory: Callable,
    fake: Faker,
) -> None:
    email = fake.email(safe=True, domain="example.com")
    password = fake.password(length=8)
    user = await user_factory(email=email, password=password)
    await channel_factory(user=user)

    async with await client(email, password) as auth_cl:
        response = await auth_cl.get(f"{TEST_PATH}/{fake.uuid4()}")

    assert response.status_code == 404, response.text


async def test_create_vacancy(
    client: Callable,
    user_factory: Callable,
    channel_factory: Callable,
    session: AsyncSession,
    fake: Faker,
) -> None:
    email = fake.email(safe=True, domain="example.com")
    password = fake.password(length=8)
    user = await user_factory(email=email, password=password)
    channel = await channel_factory(user=user)
    vacancy_data = VacancyCreate(
        message_id=fake.uuid4(),
        content=fake.text(),
        contact=fake.email(),
        channel_id=channel["id"],
    ).model_dump_json()

    async with await client(email, password) as auth_cl:
        response = await auth_cl.post(f"{TEST_PATH}", content=vacancy_data)
    assert response.status_code == 200, response.text
    assert response.json()["status_code"] == 201, response.text

    # Check the database for the created vacancy
    res = await session.scalars(select(VacancyORM))
    vacancies = res.all()

    assert len(vacancies) == 1, "Vacancy not created in the database"
    assert vacancies[0].channel_id == channel["id"], "Vacancy channel_id does not match"


async def test_update_vacancy(
    client: Callable,
    user_factory: Callable,
    channel_factory: Callable,
    vacancy_factory: Callable,
    fake: Faker,
) -> None:
    email = fake.email(safe=True, domain="example.com")
    password = fake.password(length=8)
    user = await user_factory(email=email, password=password)
    channel = await channel_factory(user=user)
    vacancy = await vacancy_factory(user=user, channel=channel)

    async with await client(email, password) as auth_cl:
        response = await auth_cl.put(
            f"{TEST_PATH}/{vacancy['id']}",
            content=VacancyUpdate(
                content=fake.text(),
                contact=fake.email(),
                is_viewed=fake.boolean(),
            ).model_dump_json()
        )

    assert response.status_code == 200, response.text
    res_data = response.json()
    assert res_data["message"] == "Successfully updated vacancy"
    assert res_data["data"]["content"] == response.json()["data"]["content"]

    # Check with not existing vacancy
    async with await client(email, password) as auth_cl:
        response = await auth_cl.put(
            f"{TEST_PATH}/{fake.uuid4()}",
            content=VacancyUpdate(
                is_applied=fake.boolean(),
            ).model_dump_json()
        )

    assert response.status_code == 404, response.text


async def test_delete_vacancy(
    client: Callable,
    user_factory: Callable,
    channel_factory: Callable,
    vacancy_factory: Callable,
    fake: Faker,
) -> None:
    email = fake.email(safe=True, domain="example.com")
    password = fake.password(length=8)
    user = await user_factory(email=email, password=password)
    channel = await channel_factory(user=user)
    vacancy = await vacancy_factory(user=user, channel=channel)

    async with await client(email, password) as auth_cl:
        response = await auth_cl.delete(f"{TEST_PATH}/{vacancy['id']}")

    assert response.status_code == 200, response.text
    res_data = response.json()
    assert res_data["message"] == "Successfully deleted vacancy"
    assert res_data["data"]["id"] == str(vacancy["id"])

    # Check if the vacancy is not belonging to the user
    user_2 = await user_factory(email=fake.email(), password=fake.password(length=8))
    channel_2 = await channel_factory(user=user_2)
    vacancy_2 = await vacancy_factory(channel=channel_2)

    async with await client(email, password) as auth_cl:
        response = await auth_cl.delete(f"{TEST_PATH}/{vacancy_2['id']}")

    assert response.status_code == 403, response.text

    # Check with not existing vacancy
    async with await client(email, password) as auth_cl:
        response = await auth_cl.delete(f"{TEST_PATH}/{fake.uuid4()}")

    assert response.status_code == 404, response.text
