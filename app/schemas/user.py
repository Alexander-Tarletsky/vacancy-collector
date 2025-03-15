from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    first_name: str | None = Field(default=None)
    last_name: str | None = Field(default=None)
    email: EmailStr | None
    api_id: str | None
    api_hash: str | None
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    is_confirmed: bool = Field(default=True)


class UserSignUp(UserBase):
    password: str  # TODO: token!


class UserSignIn(BaseModel):
    email: EmailStr
    password: str


class UserCreate(UserBase):
    email: EmailStr
    password: str
    api_id: str
    api_hash: str


class UserUpdate(UserBase):
    pass


class UserUpdatePassword(UserBase):
    password: str


# Properties to return via API
class UserResponse(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
