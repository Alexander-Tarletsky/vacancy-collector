import logging
from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)

from core.config import settings
from core.exceptions import BaseCustomException

logger = logging.getLogger(__name__)

async_engine = create_async_engine(settings.DATABASE_URI, echo=settings.DB_ECHO)

# Creating an async session maker for creating AsyncSession instances
AsyncSessionFactory = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession | Any, Any]:
    async with AsyncSessionFactory() as session:
        logger.debug(f"Async Engine Pool Status: {async_engine.pool.status()}")
        try:
            yield session
        except SQLAlchemyError as e:
            logger.error(f"Error getting database session: {e}")
            raise
        except BaseCustomException as e:
            logger.error(f"Unhandled exception: {e}")
            raise
