from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from crud.base import CRUDBase
from db.models import ChannelORM, VacancyORM
from schemas.vacancy import VacancyCreate, VacancyUpdate


class CRUDVacancy(CRUDBase[VacancyORM, VacancyCreate, VacancyUpdate]):
    async def get_channel_vacancies(
            self,
            db_session: AsyncSession,
            channel_id: UUID
    ) -> Sequence[VacancyORM]:
        """
        Retrieve all vacancies associated with a specific channel.

        Args:
            db_session (AsyncSession): The database session.
            channel_id (UUID): The UUID of the channel whose vacancies are to be retrieved.
        """
        result = await db_session.execute(
            select(self.model).where(self.model.channel_id == channel_id)
        )
        return result.scalars().all()

    async def get_user_vacancies(
            self,
            db_session: AsyncSession,
            user_id: UUID
    ) -> Sequence[VacancyORM]:
        """
        Retrieve all vacancies associated with a specific user.

        Args:
            db_session (AsyncSession): The database session.
            user_id (UUID): The UUID of the user whose vacancies are to be retrieved.
        """
        stmt = (
            select(self.model).filter(self.model.channel_id.in_(
                select(ChannelORM.id).filter(ChannelORM.user_id == user_id)
            ))
        )

        result = await db_session.execute(stmt)

        return result.scalars().all()


vacancy_crud = CRUDVacancy(VacancyORM)
