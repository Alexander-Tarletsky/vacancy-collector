from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from core.security import current_user
from db.connect import get_session
from db.models import UserORM
from schemas.channel import ChannelCreate, ChannelUpdate, ChannelResponse
from schemas.response import Response
from services.channel import ChannelService

router = APIRouter()


@router.get("/{channel_id}", response_model=Response)
async def get_user_channel(
    channel_id: UUID,
    db_session: Annotated[AsyncSession, Depends(get_session)],
    user: Annotated[UserORM, Depends(current_user)],
    channel_service: Annotated[ChannelService, Depends()],
) -> Response:
    """
    Retrieve a specific channel by ID.

    Args:
        channel_id (UUID): The ID of the channel to retrieve.
        db_session (AsyncSession): The database session.
        user (UserORM): The current user.
        channel_service (ChannelService): The channel service.
    """
    channel = await channel_service.get_by_id(db_session, user, channel_id)
    channel_response = ChannelResponse.model_validate(channel)

    return Response(
        status_code=status.HTTP_200_OK,
        message="Successfully fetched channel",
        data=channel_response.model_dump(),
    )


@router.get("", response_model=Response)
async def get_user_channels(
    db_session: Annotated[AsyncSession, Depends(get_session)],
    user: Annotated[UserORM, Depends(current_user)],
    channel_service: Annotated[ChannelService, Depends()],
) -> Response:
    """
    Retrieve all channels associated with the current user.

    Args:
        db_session (AsyncSession): The database session.
        user (UserORM): The current user.
        channel_service (ChannelService): The channel service.
    """
    channels = await channel_service.get_user_channels(db_session, user)
    channels_res = [ChannelResponse.model_validate(channel).model_dump() for channel in channels]

    return Response(
        status_code=status.HTTP_200_OK,
        message="Successfully fetched channels",
        data=channels_res,
    )


@router.post("", response_model=Response)
async def create(
    db_session: Annotated[AsyncSession, Depends(get_session)],
    user: Annotated[UserORM, Depends(current_user)],
    channel_service: Annotated[ChannelService, Depends()],
    *,
    channel_data: ChannelCreate,
) -> Response:
    """
    Create a new channel for the current user.

    Args:
        db_session (AsyncSession): The database session.
        user (UserORM): The current user.
        channel_service (ChannelService): The channel service.
        channel_data (ChannelCreate): The channel data.
    """
    new_channel = await channel_service.create(db_session, user, channel_data)
    channel_response = ChannelResponse.model_validate(new_channel)

    return Response(
        status_code=status.HTTP_201_CREATED,
        message="Successfully created channel",
        data=channel_response.model_dump(),
    )


@router.put("/{channel_id}", response_model=Response)
async def update_channel(
    channel_id: UUID,
    channel_data: ChannelUpdate,
    user: Annotated[UserORM, Depends(current_user)],
    db_session: Annotated[AsyncSession, Depends(get_session)],
    channel_service: Annotated[ChannelService, Depends()],
) -> Response:
    """
    Update a channel by ID.

    Args:
        channel_id (UUID): The ID of the channel to update.
        channel_data (ChannelUpdate): The updated channel data.
        user (UserORM): The current user.
        db_session (AsyncSession): The database session.
        channel_service (ChannelService): The channel service.
    """
    updated_channel = await channel_service.update_user_channel(
        db_session, channel_id, user, channel_data
    )
    channel_response = ChannelResponse.model_validate(updated_channel)

    return Response(
        status_code=status.HTTP_200_OK,
        message="Successfully updated channel",
        data=channel_response.model_dump(),
    )


@router.delete("/{channel_id}", response_model=Response)
async def delete_channel(
    channel_id: UUID,
    user: Annotated[UserORM, Depends(current_user)],
    db_session: Annotated[AsyncSession, Depends(get_session)],
    channel_service: Annotated[ChannelService, Depends()],
) -> Response:
    """
    Delete a channel by ID.

    Args:
        channel_id (UUID): The ID of the channel to delete.
        user (UserORM): The current user.
        db_session (AsyncSession): The database session.
        channel_service (ChannelService): The channel service.
    """
    deleted_channel = await channel_service.delete_user_channel(db_session, user, channel_id)


    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
        message="Successfully deleted channel",
        data={"id": str(deleted_channel)},
    )
