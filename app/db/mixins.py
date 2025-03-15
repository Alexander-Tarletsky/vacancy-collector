from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import declared_attr, Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from db.models import UserORM


class UserRelationMixin:
    _user_id_unique: bool | None = None
    _user_id_nullable: bool = False
    _user_back_populates: str | None = None

    @declared_attr
    def user_id(cls) -> Mapped[UUID]:  # NOQA: N805
        return mapped_column(
            ForeignKey("users.id", ondelete="CASCADE"),
            unique=cls._user_id_unique,
            nullable=cls._user_id_nullable,
        )

    @declared_attr
    def user(cls) -> Mapped["UserORM"]:  # NOQA: N805
        return relationship(
            "UserORM",
            back_populates=cls._user_back_populates,
        )
