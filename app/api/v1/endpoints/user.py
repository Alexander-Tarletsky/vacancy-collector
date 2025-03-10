from typing import Annotated

from fastapi import APIRouter, Depends

from core.security import current_user
from schemas.user import UserResponse

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def get_current_user(
        user: Annotated[UserResponse, Depends(current_user)]
) -> UserResponse:
    return user