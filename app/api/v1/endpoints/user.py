from typing import Annotated

from fastapi import APIRouter, Depends

from core.security import current_user
from schemas.response import Response
from schemas.user import UserResponse

router = APIRouter()


@router.get("/me", response_model=Response)
async def get_current_user(user: Annotated[UserResponse, Depends(current_user)]) -> Response:
    user_response = UserResponse.model_validate(user)
    return Response(
        status_code=200,
        message="User details",
        data=user_response.model_dump(),
    )
