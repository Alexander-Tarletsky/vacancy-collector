from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from schemas.user import UserResponse


class TelegramConnectionBase(BaseModel):
    session_data: str | None = Field(default="")
    is_active: bool = Field(default=True)


class TelegramConnectionCreate(TelegramConnectionBase):
    pass


class TelegramConnectionUpdate(TelegramConnectionBase):
    pass


class TelegramConnectionResponse(TelegramConnectionBase):
    id: UUID
    user_id: UUID
    user: UserResponse
    tfa_password: str | None = None  # Optional 2FA password
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)