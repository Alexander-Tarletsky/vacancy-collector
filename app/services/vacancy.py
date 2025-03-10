from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import AccessForbiddenException
from crud.vacancy import vacancy_crud
from db.models import UserORM
from schemas import VacancyResponse, VacancyCreate, VacancyUpdate


class VacancyService:
    @classmethod
    async def get_user_vacancies(cls, db: AsyncSession, user: UserORM) -> list[VacancyResponse]:
        vacancies = await vacancy_crud.get_user_vacancies(db, user_id=user.id)
        return [VacancyResponse.model_validate(vacancy) for vacancy in vacancies]

    @classmethod
    async def get_channel_vacancies(
            cls,
            db: AsyncSession,
            user: UserORM,
            channel_id: UUID,
    ) -> list[VacancyResponse]:
        vacancies = await vacancy_crud.get_channel_vacancies(db, channel_id=channel_id)
        return [VacancyResponse.model_validate(vacancy) for vacancy in vacancies]

    @classmethod
    async def get_by_id(
            cls,
            db: AsyncSession,
            user: UserORM,
            vacancy_id: UUID,
    ) -> VacancyResponse:
        vacancy = await vacancy_crud.get_or_404(db, id=vacancy_id)
        if vacancy.channel.user_id != user.id:
            raise AccessForbiddenException
        return VacancyResponse.model_validate(vacancy)

    @classmethod
    async def create(
            cls,
            db: AsyncSession,
            user: UserORM,
            vacancy_data: VacancyCreate,
            channel_id: UUID,
    ) -> VacancyResponse:
        new_vacancy = await vacancy_crud.create(db, obj_in=vacancy_data)
        return VacancyResponse.model_validate(new_vacancy)

    @classmethod
    async def update_user_vacancy(
            cls,
            db: AsyncSession,
            user: UserORM,
            vacancy_id: UUID,
            vacancy_data: VacancyUpdate,
    ) -> VacancyResponse:
        vacancy = await vacancy_crud.get_or_404(db, id=vacancy_id)
        if vacancy.channel.user_id != user.id:
            raise AccessForbiddenException

        updated_vacancy = await vacancy_crud.update(db, db_obj=vacancy, obj_in=vacancy_data)
        return VacancyResponse.model_validate(updated_vacancy)

    @classmethod
    async def delete_user_vacancy(
            cls,
            db: AsyncSession,
            user: UserORM,
            vacancy_id: UUID,
    ) -> UUID:
        vacancy = await vacancy_crud.get_or_404(db, id=vacancy_id)
        if vacancy.channel.user_id != user.id:
            raise AccessForbiddenException

        await vacancy_crud.remove(db, id=vacancy_id)
        return vacancy_id
