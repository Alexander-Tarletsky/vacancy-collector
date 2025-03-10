from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str
    token_type: str = Field(default="bearer")


# class TokenData(BaseModel):
#     id: str | None = Field(default=None)
#     username: str | None = Field(default=None)
#     email: str | None = Field(default=None)
#     is_active: bool = Field(default=True)
#     is_superuser: bool = Field(default=False)
#     scopes: List[str] = Field(default=[])
