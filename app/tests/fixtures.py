import logging
import uuid
from collections.abc import AsyncGenerator, Callable
from typing import Any

import pytest
import pytest_asyncio
from faker import Faker
from httpx import AsyncClient, ASGITransport
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
from db import Base
from db.connect import get_session
from main import app
from schemas.channel import ChannelResponse, ChannelCreate
from schemas.user import UserResponse, UserCreate

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
    async_session = AsyncSession(
        bind=connection,
        join_transaction_mode="create_savepoint",  # it will make connection.begin_nested()
    )
    # TODO: Perhaps we could use the async_session as a context manager (async with async_session:)
    yield async_session

    await transaction.rollback()
    await async_session.close()


@pytest_asyncio.fixture()
async def client(
    connection: AsyncConnection,
    transaction: AsyncTransaction,
) -> AsyncGenerator[AsyncClient, None]:  # NOQA: UP043
    async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:  # NOQA: UP043
        """
        The client fixture is used to create an HTTP client for testing the API.
        The client is created once per test and is shared across all test functions within the test.
        The client is closed at the end of the test to free up resources.

        The session fixture is used to ensure data isolation.
        Within the overall transaction, each test runs in its own transaction,
        and once the test ends, the overall transaction is rolled back, rolling back all nested
        transactions and keeping the database clean.
        """
        async_session = AsyncSession(
            bind=connection,
            join_transaction_mode="create_savepoint",
        )
        async with async_session:  # Close the session after the test
            yield async_session

    # Override the get_async_session dependency of the `app` with the test session
    app.dependency_overrides[get_session] = override_get_async_session

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url=str(settings.BASE_HOST),
        headers={"Content-Type": "application/json"},
    ) as test_client:
        test_client.headers.update({"Host": "127.0.0.1"})
        yield test_client

    # Remove the override
    app.dependency_overrides.pop(get_session, None)

    # TODO: Perhaps we could rollback the transaction here as well (await transaction.rollback())


@pytest.fixture(scope="session")
def fake() -> Faker:
    fake = Faker()
    return fake


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
                user_id=user.id,
            ),
        )
        channel_response = ChannelResponse.model_validate(new_channel)
        return channel_response.model_dump()

    return create_channel


@pytest_asyncio.fixture(scope="package")
async def get_test_user_data(fake) -> dict:
    return UserCreate(
        email=fake.email(safe=True, domain="example.com"),
        password="secret",
        first_name="Test User",
        api_id="api_id",
        api_hash="api_hash",
    ).model_dump()
