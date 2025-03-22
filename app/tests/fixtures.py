import logging
import uuid
from collections.abc import AsyncGenerator, Callable
from typing import Any

import pytest
import pytest_asyncio
from faker import Faker
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncConnection,
    AsyncTransaction,
    create_async_engine,
    AsyncEngine,
)

from core.config import settings
from core.security import hash_password
from crud.channel import channel_crud
from crud.user import user_crud
from crud.vacancy import vacancy_crud
from db import Base
from db.connect import get_session
from main import app
from schemas.channel import ChannelResponse, ChannelCreate
from schemas.user import UserResponse, UserCreate
from schemas.vacancy import VacancyCreate, VacancyResponse
from tests import utils

logger = logging.getLogger(__name__)


@pytest_asyncio.fixture(scope="session")
async def async_engine() -> AsyncGenerator[AsyncEngine, Any]:  # NOQA: UP043
    # Create a new async engine in the session scope
    t_engine = create_async_engine(settings.TEST_DATABASE_URI, echo=True)
    logger.info(f"Connected to database: {settings.TEST_DATABASE_URI}")

    # Create the database tables
    async with t_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield t_engine

    # Drop the database tables
    async with t_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    # Close and clean-up pooled connections for AsyncEngine created in session scope
    # https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#sqlalchemy.ext.asyncio.AsyncEngine.dispose
    await t_engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def connection(async_engine: AsyncEngine) -> AsyncGenerator[AsyncConnection, None]:  # NOQA: UP043
    """
    This fixture is used to create a connection to the database.
    The connection is created once per session and is shared across all tests.
    The connection is closed at the end of the session to free up resources.
    """
    async with async_engine.connect() as connection:
        yield connection


@pytest_asyncio.fixture()
async def transaction(
    connection: AsyncConnection,
) -> AsyncGenerator[AsyncTransaction, None]:  # NOQA: UP043
    """
    The transaction fixture is used to create a transaction.
    The transaction is created once per test and is shared across
    all test functions within the test.

    The transaction is rolled back at the end of the test to keep the database clean.
    """
    async with connection.begin() as transaction:
        yield transaction


@pytest_asyncio.fixture()
async def session(
    connection: AsyncConnection,  # NOQA: ARG001
    transaction: AsyncTransaction,
) -> AsyncGenerator[AsyncSession, None]:  # NOQA: UP043
    """
    The session fixture is used in tests to ensure data isolation.
    Within the overall transaction, each test runs in its own transaction,
    and once the test ends, the overall transaction is rolled back, rolling back all nested
    transactions and keeping the database clean.
    This setup ensures consistent and clean database state for testing purposes.
    """
    # TODO: I think we should use here the async session maker, like in the `get_session` function
    # async_session_maker = async_sessionmaker(
    #     bind=connection,
    #     class_=AsyncSession,
    #     expire_on_commit=False,
    #     autocommit=False,
    #     autoflush=False,
    # )

    async_session = AsyncSession(
        bind=connection,
        join_transaction_mode="create_savepoint",  # it will make connection.begin_nested()
    )
    # We aren't using context manager `async with async_session` here because we want
    # to roll back the transaction and close the session after the test
    yield async_session

    await transaction.rollback()
    await async_session.close()


@pytest_asyncio.fixture()
async def client(
    connection: AsyncConnection,
    transaction: AsyncTransaction,  # NOQA: ARG001
) -> AsyncGenerator[utils.AsyncClientFactory, Any]:
    """
    This is a factory for creating an HTTP AsyncClient class for testing the API.

    The session fixture is used to ensure data isolation.
    Within the overall transaction, each test runs in its own transaction,
    and once the test ends, the overall transaction will be rolled back, rolling back all nested
    transactions and keeping the database clean.
    """
    async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
        async_session = AsyncSession(
            bind=connection,
            join_transaction_mode="create_savepoint",
        )
        async with async_session:  # Close the session after the test
            yield async_session

    # Override the get_async_session dependency of the `app` with the test session
    app.dependency_overrides[get_session] = override_get_async_session

    client_factory = utils.AsyncClientFactory(app, str(settings.BASE_HOST))

    yield client_factory

    app.dependency_overrides.pop(get_session, None)


@pytest.fixture(scope="session")
def fake() -> Faker:
    fake = Faker()
    return fake


@pytest_asyncio.fixture(scope="package")
async def get_test_user_data(fake: Faker) -> dict:
    return UserCreate(
        email=fake.email(safe=True, domain="example.com"),
        password="secret",
        first_name="Test User",
        api_id="api_id",
        api_hash="api_hash",
    ).model_dump()


@pytest_asyncio.fixture()
async def user_factory(
    session: AsyncSession,
    fake: Faker,
) -> Callable:
    async def create_user(
        email: EmailStr | None = None,
        password: str | None = "password",  # NOQA: S107
        api_id: str | None = "api_id",
        api_hash: str | None = "api_hash",
    ) -> UserResponse | dict | None:
        """
        This fixture is used to create a user in the database.
        """
        hashed_password = hash_password(password)
        new_user = await user_crud.create(
            session,
            obj_in=UserCreate(
                email=email or fake.email(safe=True, domain="example.com"),
                password=hashed_password,
                api_id=api_id,
                api_hash=api_hash,
            ),
        )
        user_response = UserResponse.model_validate(new_user)
        return user_response.model_dump()

    return create_user


@pytest_asyncio.fixture()
async def channel_factory(
    session: AsyncSession,
    user_factory: Callable,
    fake: Faker,
) -> Callable:
    async def create_channel(user: UserResponse | None = None) -> ChannelResponse | dict | None:
        """
        This fixture is used to create a channel in the database.
        """
        user = user or await user_factory()

        new_channel = await channel_crud.create(
            session,
            obj_in=ChannelCreate(
                title=fake.sentence(),
                description=fake.text(),
                telegram_id=str(uuid.uuid4()),
                user_id=user['id'],
            ),
        )
        channel_response = ChannelResponse.model_validate(new_channel)
        return channel_response.model_dump()

    return create_channel


@pytest_asyncio.fixture()
async def vacancy_factory(
    session: AsyncSession,
    user_factory: Callable,
    channel_factory: Callable,
    fake: Faker,
) -> Callable:
    async def create_vacancy(
        user: UserResponse | None = None,
        channel: ChannelResponse | None = None
    ) -> dict:
        """
        This fixture is used to create a vacancy in the database.
        """
        channel = channel or await channel_factory(user=user or await user_factory())

        new_vacancy = await vacancy_crud.create(
            session,
            obj_in=VacancyCreate(
                message_id=str(uuid.uuid4()),
                content=fake.text(),
                contact=fake.email(),
                channel_id=channel['id'],
            ),
        )

        vacancy_response = VacancyResponse.model_validate(new_vacancy)
        return vacancy_response.model_dump()

    return create_vacancy


# TODO: Remove this code after end of the test
# @pytest_asyncio.fixture()
# async def auth_user_token(client: AsyncClient, user: dict | Any) -> str:
#     response = await client.post(
#         f"{settings.API_V1_STR}/auth/token",
#         data={"username": user["email"], "password": user["password"]},
#         headers={"Content-Type": "application/x-www-form-urlencoded"},
#     )
#     assert response.status_code == 200, response.text
#     return response.json()["data"]["access_token"]

# @pytest_asyncio.fixture
# async def auth_client(
#     client: AsyncClient,
#     user_email: str,
#     user_password: str,
# ) -> None:
#     """
#     This fixture is used to create an authenticated client for testing.
#     It takes the email and password of the user and returns an authenticated client.
#     """
#     client.auth = AsyncTokenAuth(user_email, user_password)

