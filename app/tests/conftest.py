from typing import Any, AsyncGenerator

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from core.config import settings
from main import app

TEST_DB_URI = str(settings.TEST_DATABASE_URI)

sync_engine = create_engine(TEST_DB_URI.replace("+asyncpg", ""), echo=True)
async_engine = create_async_engine(TEST_DB_URI, echo=True)

AsyncSessionFactory = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    # autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
async def client(start_db) -> AsyncGenerator[AsyncClient, Any]:

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test/v1",
        headers={"Content-Type": "application/json"},
    ) as test_client:
        yield test_client


# @pytest.fixture(autouse=True, scope="module")
# async def initialize_db():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#     yield
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)


# @pytest.fixture
# async def async_client():
#     async with AsyncClient(app=app, base_url="http://test") as client:
#         yield client

pytest_plugins = [
    "tests.fixtures",
]
