from fastapi import HTTPException
from starlette import status


class BaseCustomException(Exception):
    pass


class BaseHTTPException(HTTPException):
    def __init__(self, status_code: int, detail: str, **kwargs) -> None:
        super().__init__(status_code=status_code, detail=detail, **kwargs)


class AuthException(BaseHTTPException):
    def __init__(self, msg: str | None = None) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=msg or "Could not validate credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )


class UserAlreadyExistsException(BaseHTTPException):
    def __init__(self, msg: str | None = None) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=msg or "User with this email already exists.",
        )


class UserNotFoundException(BaseHTTPException):
    def __init__(self, msg: str | None = None) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=msg or "User not found",
        )


class ResourceNotFoundException(BaseHTTPException):
    def __init__(self, msg: str | None = None) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=msg or "Resource not found",
        )


class InactiveUserException(BaseHTTPException):
    def __init__(self, msg: str | None = None) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=msg or "Inactive user.",
            headers={"WWW-Authenticate": "Bearer"},
        )


class UnconfirmedUserException(BaseHTTPException):
    def __init__(self, msg: str | None = None) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=msg or "User is not verified. Check your email or request a new confirmation email.",  # NOQA
            headers={"WWW-Authenticate": "Bearer"},
        )


class AccessForbiddenException(BaseHTTPException):
    def __init__(self, msg: str | None = None) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=msg or "Access forbidden. You do not have access to this resource.",
            headers={"WWW-Authenticate": "Bearer"},
        )
