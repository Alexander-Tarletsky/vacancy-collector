import logging
from typing import AsyncGenerator, Any, Generator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import event
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.orm import Session, SessionTransaction

from core.exceptions import BaseCustomException
from db import Base
from db.connect import get_session
from main import app
from tests.conftest import sync_engine, async_engine

logger = logging.getLogger(__name__)


# @pytest.fixture(scope="session")
# async def start_db():
#     async with async_engine.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)
#         await conn.run_sync(Base.metadata.create_all)
#     await async_engine.dispose()


# @pytest_asyncio.fixture(scope='session', autouse=True)
# async def setup_test_db():
#     # setup and teardown of database tables
#     async with async_engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#     yield
#     async with async_engine.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)


# @pytest_asyncio.fixture(scope='function')
# async def db() -> AsyncSession:
#     # yield a database session used by test functions
#     async with AsyncSessionLocal() as session:
#         yield session


@pytest.fixture(scope="session", autouse=True)
def setup_test_db() -> Generator:
    # Setup and teardown of database tables
    # We aren't using the async engine here because we are going it only once per session
    with sync_engine.begin():
        Base.metadata.drop_all(sync_engine)
        Base.metadata.create_all(sync_engine)
        yield
        Base.metadata.drop_all(sync_engine)


@pytest_asyncio.fixture(autouse=True)
async def session() -> AsyncGenerator:
    """
    The code snippet involves an async engine connection and nested transactions. The session
    fixture is used in tests to ensure data isolation. Each test runs in its own transaction,
    and once the test ends, the transaction rolls back, keeping the database clean.

    Nested transactions are important for operations like DDL changes, and
    the "after_transaction_end" event listener ensures a savepoint remains active throughout,
    re-initiating nested transactions when necessary. This setup ensures consistent and clean
    database state for testing purposes.

    More info:
    https://github.com/sqlalchemy/sqlalchemy/issues/5811#issuecomment-756269881/.
    """

    async with async_engine.connect() as conn:
        await conn.begin()  # begin a main transaction
        await conn.begin_nested()  # begin a nested transaction

        async_session_factory = async_sessionmaker(
            bind=async_engine,
            class_=AsyncSession,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        )

        async_session = async_session_factory()

        # The `after_transaction_end` event listener ensures a savepoint remains active throughout
        # re-initiating nested transactions when necessary.
        @event.listens_for(async_session.sync_session, "after_transaction_end")
        def end_savepoint(_session: Session, _transaction: SessionTransaction) -> None:
            if conn.closed:
                return

            if not conn.in_nested_transaction():
                if conn.sync_connection:
                    conn.sync_connection.begin_nested()

        def get_test_session() -> Generator:
            """Dependency override to return the test session."""
            try:
                yield async_session_factory()
            except SQLAlchemyError as e:
                logger.error(f"Error getting database session: {e}")
                raise
            except BaseCustomException as e:
                logger.error(f"Unhandled exception: {e}")
                raise

        # Override the get_session dependency of the `app` with the test session
        app.dependency_overrides[get_session] = get_test_session

        yield async_session

        await async_session.close()
        await conn.rollback()


@pytest_asyncio.fixture(scope="session")
async def client(start_db) -> AsyncGenerator[AsyncClient, Any]:

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test/v1",
        headers={"Content-Type": "application/json"},
    ) as test_client:
        yield test_client