# from __future__ import annotations
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from db.base_model import Base, str_100, str_20, Varchar, str_1000
from db.mixins import UserRelationMixin


class UserORM(Base):
    __tablename__ = "users"

    first_name: Mapped[str_100]
    last_name: Mapped[str_100]
    email: Mapped[str_100] = mapped_column(unique=True)
    password: Mapped[str_20]
    api_id: Mapped[str]
    api_hash: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)
    is_confirmed: Mapped[bool] = mapped_column(default=False)

    # One-to-many relationship with Channel
    channels: Mapped[list["ChannelORM"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def __str__(self):
        return f"{self.__class__.__name__}({self.email})"

    def __repr__(self):
        return self.__str__()


class ChannelORM(UserRelationMixin, Base):
    __tablename__ = "channels"
    _user_back_populates = "channels"  # From UserRelationMixin
    # Relationship with User was defined in UserRelationMixin

    title: Mapped[str_100]
    description: Mapped[str_1000 | None]
    telegram_id: Mapped[str] = mapped_column(unique=True)
    is_active: Mapped[bool] = mapped_column(default=True)

    # One-to-many relationship with Vacancy
    vacancies: Mapped[list["VacancyORM"]] = relationship(
        back_populates="channel",
        cascade="all, delete-orphan"
    )

    def __str__(self):
        return f"{self.__class__.__name__}({self.title})"

    def __repr__(self):
        return self.__str__()


class VacancyORM(Base):
    __tablename__ = "vacancies"

    message_id: Mapped[str] = mapped_column(unique=True)
    content: Mapped[Varchar]
    contact: Mapped[str | None]
    is_viewed: Mapped[bool] = mapped_column(default=False)
    is_opportunity: Mapped[bool] = mapped_column(default=False)
    is_applied: Mapped[bool] = mapped_column(default=False)
    is_rejected: Mapped[bool] = mapped_column(default=False)

    # Relationship with Channel
    channel_id: Mapped[UUID] = mapped_column(ForeignKey("channels.id", ondelete="CASCADE"))
    channel: Mapped[ChannelORM] = relationship(back_populates="vacancies")

    def __str__(self):
        return f"{self.__class__.__name__}({self.id})"

    def __repr__(self):
        return self.__str__()
