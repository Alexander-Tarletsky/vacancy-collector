from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.exceptions import AccessForbiddenException
from crud.base import CRUDBase
from db.models import ChannelORM, VacancyORM, UserORM
from schemas.vacancy import VacancyCreate, VacancyUpdate


class CRUDVacancy(CRUDBase[VacancyORM, VacancyCreate, VacancyUpdate]):
    async def get(self, db_session: AsyncSession, obj_id: UUID) -> VacancyORM | None:
        """
        Retrieve a single record by its ID.

        Args:
            db_session (AsyncSession): The database session.
            obj_id (Any): The ID of the record to retrieve.
        """
        result = await db_session.execute(
            select(VacancyORM)
            .options(selectinload(VacancyORM.channel))
            .where(VacancyORM.id == obj_id)
        )
        return result.scalars().first()

    async def get_channel_vacancies(
        self,
        db_session: AsyncSession,
        *,
        user: UserORM,
        channel_id: UUID,
        offset: int = 0,
        limit: int = 1000,
    ) -> Sequence[VacancyORM]:
        """
        Retrieve all vacancies associated with a specific channel.

        Args:
            db_session (AsyncSession): The database session.
            user (UserORM): The user whose vacancies are to be retrieved.
            channel_id (UUID): The UUID of the channel whose vacancies are to be retrieved.
            offset (int): The number of records to skip.
            limit (int): The maximum number of records to retrieve.
        """
        # Permission check
        if channel_id not in [channel.id for channel in user.channels]:
            raise AccessForbiddenException

        result = await db_session.execute(
            select(self.model)
            .where(self.model.channel_id == channel_id)
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_user_vacancies(
        self, db_session: AsyncSession, user_id: UUID, offset: int = 0, limit: int = 1000
    ) -> Sequence[VacancyORM]:
        """
        Retrieve all vacancies associated with a specific user.

        Args:
            db_session (AsyncSession): The database session.
            user_id (UUID): The UUID of the user whose vacancies are to be retrieved.
            offset (int): The number of records to skip.
            limit (int): The maximum number of records to retrieve.
        """
        stmt = select(self.model).where(
                self.model.channel_id.in_(
                    select(ChannelORM.id).where(ChannelORM.user_id == user_id)
                )
        ).offset(offset).limit(limit)

        result = await db_session.execute(stmt)

        return result.scalars().all()

    async def get_user_vacancies_ids(
        self, db_session: AsyncSession, user_id: UUID
    ) -> Sequence[UUID]:
        """
        Get all vacancy IDs for a specific user.
        This method filters vacancies through the associated channel.
        It uses `joinedload` to load the related channel eagerly.
        """
        subq = select(ChannelORM.id).where(ChannelORM.user_id == user_id)
        stmt = (
            select(self.model.id)
            .where(self.model.channel_id.in_(subq))
        )

        result = await db_session.execute(stmt)
        return result.scalars().all()

    async def get_vacancy_ids_by_channel_ids(
        self, db_session: AsyncSession, channel_ids: list[UUID]
    ) -> Sequence[UUID]:
        """Get all vacancies for a list of channel IDs."""
        stmt = (
            select(self.model.id)
            .where(self.model.channel_id.in_([str(channel_id) for channel_id in channel_ids]))
        )

        result = await db_session.execute(stmt)
        return result.scalars().all()


vacancy_crud = CRUDVacancy(VacancyORM)
