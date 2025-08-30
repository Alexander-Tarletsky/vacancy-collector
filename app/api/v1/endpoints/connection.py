from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import current_user
from db import UserORM
from db.connect import get_session
from schemas.connection import TelegramConnectionCreate
from schemas.response import Response

router = APIRouter()


@router.post("", response_model=Response)
async def create(
    db_session: Annotated[AsyncSession, Depends(get_session)],
    user: Annotated[UserORM, Depends(current_user)],
    # telegram_service: Annotated[TelegramService, Depends()],
    *,
    connection_data: TelegramConnectionCreate,
) -> Response:
    pass