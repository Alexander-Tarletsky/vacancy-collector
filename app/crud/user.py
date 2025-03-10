from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from crud.base import CRUDBase
from db.models import UserORM
from schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[UserORM, UserCreate, UserUpdate]):
    async def get_by_email(self, db: AsyncSession, email: str) -> UserORM | None:
        """
        Retrieve a user record by email.

        Args:
            db (AsyncSession): The database session.
            email (str): The email address of the user to be retrieved.
        """
        # result = await db.execute(select(UserORM).filter(self.model.email == email))
        # return result.scalars().first()
        stmt = select(UserORM).options(selectinload(UserORM.channels)).where(UserORM.email == email)

        result = await db.scalars(stmt)
        return result.first()


user_crud = CRUDUser(UserORM)
