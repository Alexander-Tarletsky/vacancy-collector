from datetime import datetime
from typing import Annotated
from uuid import UUID, uuid4

from sqlalchemy import BIGINT, String, DateTime, Uuid
from sqlalchemy import Boolean
from sqlalchemy.dialects.postgresql import VARCHAR
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func

str_20 = Annotated[str, 20]
str_100 = Annotated[str, 100]
str_200 = Annotated[str, 200]
str_1000 = Annotated[str, 1000]
type Varchar = str


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    type_annotation_map = {
        int: BIGINT,
        # datetime: TIMESTAMP(timezone=True),
        datetime: DateTime(timezone=True),
        str: String,
        str_20: String(20),
        str_100: String(100),
        str_200: String(200),
        str_1000: String(1000),
        Varchar: VARCHAR,
        UUID: Uuid,
        bool: Boolean,
    }

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        index=True,
        doc='Time of creation',
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        doc='Time of last modification',
        server_default=func.now(),
        onupdate=func.now(),
    )
