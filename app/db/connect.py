import logging
from typing import Any, AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)

from core.config import settings
from core.exceptions import BaseCustomException

logger = logging.getLogger(__name__)


# Sync engine (if needed for synchronous operations)
sync_engine = create_engine(url=settings.DATABASE_URL_SYNC, echo=True)

# Async engine for asynchronous DB operations
async_engine = create_async_engine(settings.DATABASE_URL_ASYNC, echo=True)

# Creating an async session maker for creating AsyncSession instances
AsyncSessionFactory = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    autocommit=False,
    # autoflush=False,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession | Any, Any]:
    async with AsyncSessionFactory() as session:
        # logger.debug(f"ASYNC Pool: {engine.pool.status()}")
        try:
            yield session
        except SQLAlchemyError as e:
            logger.error(f"Error getting database session: {e}")
            raise
        except BaseCustomException as e:
            logger.error(f"Unhandled exception: {e}")
            raise


# Alternative way
# app/services/database.py
# Base = declarative_base()

# class DatabaseSessionManager:
#     def __init__(self):
#         self._engine: AsyncEngine | None = None
#         self._sessionmaker: async_sessionmaker | None = None
#
#     def init(self, host: str):
#         self._engine = create_async_engine(host)
#         self._sessionmaker = async_sessionmaker(
#             bind=self._engine,
#             autocommit=False,
#             expire_on_commit=False,
#         )
#
#     async def close(self):
#         if self._engine is None:
#             raise Exception("DatabaseSessionManager is not initialized")
#         await self._engine.dispose()
#         self._engine = None
#         self._sessionmaker = None
#
#     @contextlib.asynccontextmanager
#     async def connect(self) -> AsyncIterator[AsyncConnection]:
#         if self._engine is None:
#             raise Exception("DatabaseSessionManager is not initialized")
#
#         async with self._engine.connect() as connection:
#             try:
#                 yield connection
#             except Exception:
#                 await connection.rollback()
#                 raise
#
#     @contextlib.asynccontextmanager
#     async def session(self) -> AsyncIterator[AsyncSession]:
#         if self._sessionmaker is None:
#             raise Exception("DatabaseSessionManager is not initialized")
#
#         session = self._sessionmaker()
#         try:
#             yield session
#         except Exception:
#             await session.rollback()
#             raise
#         finally:
#             await session.close()

    # # Used for testing
    # async def create_all(self, connection: AsyncConnection):
    #     await connection.run_sync(Base.metadata.create_all)
    #
    # async def drop_all(self, connection: AsyncConnection):
    #     await connection.run_sync(Base.metadata.drop_all)

# sessionmanager = DatabaseSessionManager()
