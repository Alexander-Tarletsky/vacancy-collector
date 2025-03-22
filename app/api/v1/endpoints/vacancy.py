from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from core.exceptions import AccessForbiddenException
from core.security import current_user
from db.connect import get_session
from db.models import UserORM
from schemas.response import Response
from schemas.vacancy import VacancyCreate, VacancyUpdate, VacancyResponse
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
    vacancies = await vacancy_service.get_user_vacancies(db_session, user)
    vacancies_res = [VacancyResponse.model_validate(vacancy).model_dump() for vacancy in vacancies]

    return Response(
        status_code=status.HTTP_200_OK,
        message="Successfully fetched vacancies",
        data=vacancies_res,
    )


@router.get("/channel/{channel_id}", response_model=Response)
async def get_channel_vacancies(
    channel_id: UUID,
    db_session: Annotated[AsyncSession, Depends(get_session)],
    user: Annotated[UserORM, Depends(current_user)],
    vacancy_service: Annotated[VacancyService, Depends()],
) -> Response:
    """Retrieve all vacancies associated with a specific channel."""
    vacancies = await vacancy_service.get_channel_vacancies(db_session, user, channel_id)

    # Check permission to access the vacancies
    channel_ids = [channel.id for channel in user.channels]
    for vacancy in vacancies:
        if vacancy.channel_id not in channel_ids:
            raise AccessForbiddenException

    vacancies_res = [VacancyResponse.model_validate(vacancy).model_dump() for vacancy in vacancies]

    return Response(
        status_code=status.HTTP_200_OK,
        message="Successfully fetched vacancies",
        data=vacancies_res,
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

    # If the vacancy is not found, it will raise ResourceNotFoundException.
    # Otherwise, it will return the vacancy, that's mean that channel_id should not be empty.
    # If channel_ids is empty, we should raise AccessForbiddenException.

    # Check permission to access the vacancy
    # TODO: Perhaps we should move this logic to the service layer
    channel_ids = [channel.id for channel in user.channels]
    if vacancy.channel_id not in channel_ids:  # Assert channel_id is not empty
        raise AccessForbiddenException

    channel_vacancy = VacancyResponse.model_validate(vacancy)

    return Response(
        status_code=status.HTTP_200_OK,
        message="Successfully fetched vacancy",
        data=channel_vacancy.model_dump(),
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
    new_vacancy = await vacancy_service.create(db_session, user, vacancy_data)
    vacancy_response = VacancyResponse.model_validate(new_vacancy)

    return Response(
        status_code=status.HTTP_201_CREATED,
        message="Successfully created vacancy",
        data=vacancy_response.model_dump(),
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
    updated_channel = await vacancy_service.update_user_vacancy(
        db_session,
        user=user,
        vacancy_id=vacancy_id,
        vacancy_data=vacancy_data,
    )
    vacancy_response = VacancyResponse.model_validate(updated_channel)

    return Response(
        status_code=status.HTTP_200_OK,
        message="Successfully updated vacancy",
        data=vacancy_response.model_dump(),
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
    deleted_vacancy = await vacancy_service.delete_user_vacancy(db_session, user, vacancy_id)

    return Response(
        status_code=status.HTTP_200_OK,
        message="Successfully deleted vacancy",
        data={"id": str(deleted_vacancy)},
    )
