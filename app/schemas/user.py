from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from schemas.channel import ChannelResponse
from schemas.connection import TelegramConnectionResponse


class UserBase(BaseModel):
    first_name: str | None = Field(default=None)
    last_name: str | None = Field(default=None)
    phone: str | None = Field(default=None)
    email: EmailStr | None
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    is_confirmed: bool = Field(default=True)


# class UserSignUp(UserBase):
#     phone: str
#     email: EmailStr
#     password: str


class UserSignIn(BaseModel):
    email: EmailStr
    password: str


class UserCreate(UserBase):
    phone: str
    email: EmailStr
    password: str


class UserUpdate(UserBase):
    pass


class UserUpdatePassword(UserBase):
    password: str


# Properties to return via API
class UserResponse(UserBase):
    id: UUID
    channels: list[ChannelResponse] | None = Field(default=None)
    telegram_connection_id: UUID | None = Field(default=None)
    telegram_connection: TelegramConnectionResponse | None = Field(default=None)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
