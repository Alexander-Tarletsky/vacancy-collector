from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import AccessForbiddenException
from crud.channel import channel_crud
from db.models import UserORM
from schemas import ChannelResponse, ChannelCreate, ChannelUpdate


class ChannelService:
    @classmethod
    async def get_user_channels(
            cls,
            db: AsyncSession,
            user: UserORM,
    ) -> list[ChannelResponse]:
        channels = await channel_crud.get_user_channels(db, user=user)
        return [ChannelResponse.model_validate(channel) for channel in channels]

    @classmethod
    async def get_by_id(
            cls,
            db: AsyncSession,
            user: UserORM,
            channel_id: UUID,
    ) -> ChannelResponse:
        channel = await channel_crud.get_or_404(db, id=channel_id)
        if channel.user_id != user.id:
            raise AccessForbiddenException

        return ChannelResponse.model_validate(channel)

    @classmethod
    async def create(
            cls,
            db: AsyncSession,
            user: UserORM,
            channel_data: ChannelCreate,
    ) -> ChannelResponse:
        new_channel = await channel_crud.create(
            db,
            obj_in=channel_data.model_copy(update={"user_id": user.id})
        )

        return ChannelResponse.model_validate(new_channel)

    @classmethod
    async def update_user_channel(
            cls,
            db: AsyncSession,
            channel_id: UUID,
            user: UserORM,
            channel_data: ChannelUpdate,
    ) -> ChannelResponse:
        channel = await channel_crud.get_or_404(db, id=channel_id)
        if channel.user_id != user.id:
            raise AccessForbiddenException

        update_channel = await channel_crud.update(db, db_obj=channel, obj_in=channel_data)
        return ChannelResponse.model_validate(update_channel)
    @classmethod
    async def delete_user_channel(
            cls,
            db: AsyncSession,
            user: UserORM,
            channel_id: UUID,
    ) -> UUID:
        channel = await channel_crud.get_or_404(db, id=channel_id)
        if channel.user_id != user.id:
            raise AccessForbiddenException

        await channel_crud.remove(db, id=channel_id)
        return channel_id
