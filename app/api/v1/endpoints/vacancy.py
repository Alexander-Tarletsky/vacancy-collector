from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from core.security import current_user
from db.connect import get_session
from db.models import UserORM
from schemas.response import Response
from schemas.vacancy import VacancyCreate, VacancyUpdate
from services.vacancy import VacancyService

router = APIRouter()


@router.get("", response_model=Response)
async def get_user_vacancies(
        db_session: Annotated[AsyncSession, Depends(get_session)],
        user: Annotated[UserORM, Depends(current_user)],
        vacancy_service: Annotated[VacancyService, Depends()],
) -> Response:
    """
    Retrieve all vacancies associated with the current user.
    """
    return Response(
        status_code=status.HTTP_200_OK,
        message="Successfully fetched vacancies",
        data=await vacancy_service.get_user_vacancies(db_session, user)
    )


@router.get("/channel/{channel_id}", response_model=Response)
async def get_channel_vacancies(
        channel_id: UUID,
        db_session: Annotated[AsyncSession, Depends(get_session)],
        user: Annotated[UserORM, Depends(current_user)],
        vacancy_service: Annotated[VacancyService, Depends()],
) -> Response:
    """
    Retrieve all vacancies associated with a specific channel.
    """
    return Response(
        status_code=status.HTTP_200_OK,
        message="Successfully fetched vacancies",
        data=await vacancy_service.get_channel_vacancies(db_session, user, channel_id)
    )


@router.get("/{vacancy_id}", response_model=Response)
async def get_vacancy(
        vacancy_id: UUID,
        db_session: Annotated[AsyncSession, Depends(get_session)],
        user: Annotated[UserORM, Depends(current_user)],
        vacancy_service: Annotated[VacancyService, Depends()],
) -> Response:
    """
    Retrieve a specific vacancy by ID.
    """
    vacancy = await vacancy_service.get_by_id(db_session, user, vacancy_id)
    return Response(
        status_code=status.HTTP_200_OK,
        message="Successfully fetched vacancy",
        data=vacancy
    )


@router.post("", response_model=Response)
async def create_vacancy(
        vacancy_data: VacancyCreate,
        db_session: Annotated[AsyncSession, Depends(get_session)],
        user: Annotated[UserORM, Depends(current_user)],
        vacancy_service: Annotated[VacancyService, Depends()],
) -> Response:
    """
    Create a new vacancy.
    """
    return Response(
        status_code=status.HTTP_201_CREATED,
        message="Successfully created vacancy",
        data=await vacancy_service.create(db_session, user, vacancy_data)
    )


@router.put("/{vacancy_id}", response_model=Response)
async def update_vacancy(
        vacancy_id: UUID,
        vacancy_data: VacancyUpdate,
        db_session: Annotated[AsyncSession, Depends(get_session)],
        user: Annotated[UserORM, Depends(current_user)],
        vacancy_service: Annotated[VacancyService, Depends()],
) -> Response:
    """
    Update a vacancy by ID.
    """
    return Response(
        status_code=status.HTTP_200_OK,
        message="Successfully updated vacancy",
        data=await vacancy_service.update_user_vacancy(db_session, user, vacancy_id, vacancy_data)
    )


@router.delete("/{vacancy_id}", response_model=Response)
async def delete_vacancy(
        vacancy_id: UUID,
        db_session: Annotated[AsyncSession, Depends(get_session)],
        user: Annotated[UserORM, Depends(current_user)],
        vacancy_service: Annotated[VacancyService, Depends()],
) -> Response:
    """
    Delete a vacancy by ID.
    """
    return Response(
        status_code=status.HTTP_200_OK,
        message="Successfully deleted vacancy",
        data=await vacancy_service.delete_user_vacancy(db_session, user, vacancy_id)
    )
