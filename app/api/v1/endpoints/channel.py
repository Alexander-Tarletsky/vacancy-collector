from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from core.security import current_user
from db.connect import get_session
from db.models import UserORM
from schemas.channel import ChannelCreate, ChannelUpdate
from schemas.response import Response
from services.channel import ChannelService

router = APIRouter()


@router.get("/{channel_id}", response_model=Response)
async def get_user_channel(
        channel_id: UUID,
        db: Annotated[AsyncSession, Depends(get_session)],
        user: Annotated[UserORM, Depends(current_user)],
        channel_service: Annotated[ChannelService, Depends()],
) -> Response:
    """
    Retrieve a specific channel by ID.

    Args:
        channel_id (UUID): The ID of the channel to retrieve.
        db (AsyncSession): The database session.
        user (UserORM): The current user.
        channel_service (ChannelService): The channel service.
    """
    channel = await channel_service.get_by_id(db, user, channel_id)

    return Response(
        status_code=status.HTTP_200_OK,
        message="Successfully fetched channel",
        data=channel
    )


@router.get("", response_model=Response)
async def get_user_channels(
        db: Annotated[AsyncSession, Depends(get_session)],
        user: Annotated[UserORM, Depends(current_user)],
        channel_service: Annotated[ChannelService, Depends()],
) -> Response:
    """
    Retrieve all channels associated with the current user.

    Args:
        db (AsyncSession): The database session.
        user (UserORM): The current user.
        channel_service (ChannelService): The channel service.
    """
    return Response(
        status_code=status.HTTP_200_OK,
        message="Successfully fetched channels",
        data=await channel_service.get_user_channels(db, user)
    )


@router.post("", response_model=Response)
async def create(
        db: Annotated[AsyncSession, Depends(get_session)],
        user: Annotated[UserORM, Depends(current_user)],
        channel_service: Annotated[ChannelService, Depends()],
        *,
        channel_data: ChannelCreate,
) -> Response:
    """
    Create a new channel for the current user.

    Args:
        db (AsyncSession): The database session.
        user (UserORM): The current user.
        channel_service (ChannelService): The channel service.
        channel_data (ChannelCreate): The channel data.
    """
    return Response(
        status_code=status.HTTP_201_CREATED,
        message="Successfully created channel",
        data=await channel_service.create(db, user, channel_data)
    )


@router.put("/{channel_id}", response_model=Response)
async def update_channel(
        channel_id: UUID,
        channel_data: ChannelUpdate,
        user: Annotated[UserORM, Depends(current_user)],
        db: Annotated[AsyncSession, Depends(get_session)],
        channel_service: Annotated[ChannelService, Depends()],
):
    """
    Update a channel by ID.

    Args:
        channel_id (UUID): The ID of the channel to update.
        channel_data (ChannelUpdate): The updated channel data.
        user (UserORM): The current user.
        db (AsyncSession): The database session.
        channel_service (ChannelService): The channel service.
    """
    return Response(
        status_code=status.HTTP_200_OK,
        message="Successfully updated channel",
        data=await channel_service.update_user_channel(db, channel_id, user, channel_data)
    )


@router.delete("/{channel_id}", response_model=Response)
async def delete_channel(
        channel_id: UUID,
        user: Annotated[UserORM, Depends(current_user)],
        db: Annotated[AsyncSession, Depends(get_session)],
        channel_service: Annotated[ChannelService, Depends()],
):
    """
    Delete a channel by ID.

    Args:
        channel_id (UUID): The ID of the channel to delete.
        user (UserORM): The current user.
        db (AsyncSession): The database session.
        channel_service (ChannelService): The channel service.
    """
    return Response(
        status_code=status.HTTP_200_OK,
        message="Successfully deleted channel",
        data=await channel_service.delete_user_channel(db, user, channel_id)
    )
