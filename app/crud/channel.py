from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from crud.base import CRUDBase
from db.models import ChannelORM, UserORM
from schemas.channel import ChannelCreate, ChannelUpdate


class CRUDChannel(CRUDBase[ChannelORM, ChannelCreate, ChannelUpdate]):
    async def get_user_channels(
        self,
        db_session: AsyncSession,
        user: UserORM,
        offset: int = 0,
        limit: int = 1000,
    ) -> Sequence[ChannelORM]:
        """
        Retrieve all channels associated with a specific user.

        Args:
            db_session (AsyncSession): The database session.
            user (UserORM): The user whose channels are to be retrieved.
            offset (int): The number of records to skip.
            limit (int): The maximum number of records to retrieve.
        """
        result = await db_session.execute(
            select(self.model)
            # .join(self.model.user)
            .where(self.model.user_id == user.id)
            .offset(offset)
            .limit(limit)
        )

        return result.scalars().all()

        # TODO: Perhaps we can use `return user.channels` instead


channel_crud = CRUDChannel(ChannelORM)
