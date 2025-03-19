from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ChannelBase(BaseModel):
    title: str
    description: str | None
    telegram_id: str
    is_active: bool = Field(default=True)
    user_id: UUID


class ChannelCreate(ChannelBase):
    pass


class ChannelUpdate(BaseModel):
    title: str | None
    description: str | None
    is_active: bool = Field(default=True)


class ChannelResponse(ChannelBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    # user_id: UUID

    model_config = ConfigDict(from_attributes=True)
