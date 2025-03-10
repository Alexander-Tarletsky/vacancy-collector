from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import AuthException, UserAlreadyExistsException
from core.security import authenticate_user, create_access_token, hash_password
from crud.user import user_crud
from db.connect import get_session
from schemas.response import Response
from schemas.token import Token
from schemas.user import UserResponse, UserCreate

router = APIRouter()


@router.post("/register", response_model=Response, status_code=201)
async def register(
        user_data: UserCreate,
        db: Annotated[AsyncSession, Depends(get_session)]
) -> Response:
    """
    Register a new user.

    Args:
        user_data (UserCreate): User data.
        db (AsyncSession): Database session.
    """
    # Check if the email is already taken
    existing_user = await user_crud.get_by_email(db, user_data.email)
    if existing_user:
        raise UserAlreadyExistsException

    # Hash the password before saving
    hashed_password = hash_password(user_data.password)

    # Create a new user
    new_user = await user_crud.create(
        db,
        obj_in=user_data.model_copy(update={"password": hashed_password})
    )

    return Response(
        status_code=201,
        message="Successfully registered",
        data=UserResponse.model_validate(new_user)
    )


@router.post("/token", response_model=Response)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Response:
    """
    OAuth2 compatible token login, get an access token for future requests.

    Args:
        form_data (OAuth2PasswordRequestForm): Form data with username and password.
    """
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise AuthException

    access_token = Token(
        access_token=create_access_token(data={"sub": user.email}),
        token_type="bearer"
    )

    return Response(
        status_code=200,
        message="Successfully logged in",
        data=access_token
    )
