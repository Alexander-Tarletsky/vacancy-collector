from datetime import datetime, timedelta, UTC
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.exceptions import AuthException, InactiveUserException, UnconfirmedUserException
from crud.user import user_crud
from db.connect import get_session
from db.models import UserORM

SECRET_KEY = settings.JWT_SECRET
ALGORITHM = settings.ALGORITHM  # "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def authenticate_user(
    email: str,
    password: str,
    db_session: Annotated[AsyncSession, Depends(get_session)],
) -> UserORM | bool:
    user = await user_crud.get_by_email(db_session, email)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


async def current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db_session: Annotated[AsyncSession, Depends(get_session)],
) -> UserORM:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise AuthException
    except JWTError as exc:
        raise AuthException from exc

    user = await user_crud.get_by_email(db_session, email)

    if user is None:
        raise AuthException
    if not user.is_active:
        raise InactiveUserException
    if not user.is_confirmed:
        raise UnconfirmedUserException

    return user
