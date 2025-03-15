from collections.abc import Sequence
from typing import Any, Generic, TypeVar
from uuid import UUID

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Mapped

from db.base_model import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: type[ModelType]) -> None:
        """
        CRUD object with default async methods to Create, Read, Update, Delete (CRUD).
        Args:
            model (type[ModelType]): The SQLAlchemy model to use for CRUD operations.
        """
        self.model = model

    async def get(self, db_session: AsyncSession, obj_id: UUID) -> ModelType | None:
        """
        Retrieve a single record by its ID.

        Args:
            db_session (AsyncSession): The database session.
            obj_id (Any): The ID of the record to retrieve.
        """
        result = await db_session.execute(select(self.model).filter(self.model.id == obj_id))
        return result.scalars().first()

    async def get_or_404(self, db_session: AsyncSession, obj_id: UUID) -> ModelType:
        """Returns the object if found, otherwise raises HTTPException(404)."""
        obj = await self.get(db_session, obj_id)
        if not obj:
            raise HTTPException(status_code=404, detail=f"{self.model.__name__} not found")
        return obj

    async def get_multi(
            self,
            db_session: AsyncSession,
            offset: int = 0,
            limit: int = 1000,
    ) -> Sequence[ModelType]:
        """
        Retrieve multiple records with optional offset and limit.

        Args:
            db_session (AsyncSession): The database session.
            offset (int): The number of records to skip.
            limit (int): The maximum number of records to retrieve.
        """
        result = await db_session.execute(
            select(self.model).order_by(self.model.id).offset(offset).limit(limit)
        )
        return result.scalars().all()

    async def create(self, db_session: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Create a new record.

        Args:
            db_session (AsyncSession): The database session.
            obj_in (CreateSchemaType): The data to create the record with.
        """
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data)
        db_session.add(db_obj)
        await db_session.commit()
        await db_session.refresh(db_obj)
        return db_obj

    async def update(
            self,
            db_session: AsyncSession,
            *,
            db_obj: ModelType,
            obj_in: UpdateSchemaType | dict[str, Any]
    ) -> ModelType:
        """
        Update an existing record.

        Args:
            db_session (AsyncSession): The database session.
            db_obj (ModelType): The record to update.
            obj_in (Union[UpdateSchemaType, Dict[str, Any]]): The data to update the record with.
        """
        obj_data = db_obj.__dict__
        update_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)

        for field in update_data:
            if field in obj_data:
                setattr(db_obj, field, update_data[field])

        await db_session.commit()
        await db_session.refresh(db_obj)
        return db_obj

    async def remove(self, db_session: AsyncSession, *, obj_id: UUID) -> Mapped[UUID] | None:
        """
        Remove a record by its ID.

        Args:
            db_session (AsyncSession): The database session.
            obj_id (Any): The ID of the record to remove.
        """
        db_obj = await self.get_or_404(db_session, obj_id)
        await db_session.delete(db_obj)
        await db_session.commit()
        return db_obj.id
