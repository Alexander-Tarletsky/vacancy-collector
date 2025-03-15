from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from crud.base import CRUDBase
from db.models import UserORM
from schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[UserORM, UserCreate, UserUpdate]):
    async def get_by_email(self, db_session: AsyncSession, email: str) -> UserORM | None:
        """
        Retrieve a user record by email.

        Args:
            db_session (AsyncSession): The database session.
            email (str): The email address of the user to be retrieved.
        """
        stmt = select(UserORM).options(selectinload(UserORM.channels)).where(UserORM.email == email)

        result = await db_session.scalars(stmt)
        return result.first()

    # Another variant
    # result = await db_session.execute(select(UserORM).filter(self.model.email == email))  # NOQA
    # return result.scalars().first()  # NOQA


user_crud = CRUDUser(UserORM)
