import asyncio
import threading
import typing

import httpx
from httpx import AsyncClient

from core.config import settings
from main import app


class AsyncTokenAuth(httpx.Auth):
    """
    It's inspired by:
        https://github.com/encode/httpx/issues/1176
        https://github.com/encode/httpx/pull/1217
    Docs:
        https://www.python-httpx.org/advanced/authentication/#custom-authentication-schemes

    Describes an API Token requests authentication. Based on httpx `Auht` class.
    """

    def __init__(self, email: str, password: str) -> None:
        self._lock = threading.RLock()
        self._async_lock = asyncio.Lock()
        self._token = None
        self._email = email
        self._password = password

    # To get token we should send POST request with username and password
    async def _async_get_token(self) -> str:
        async with self._async_lock:
            if not self._token:  # TODO: We need to add logic to refresh token
                async with httpx.AsyncClient(
                    transport=httpx.ASGITransport(app=app),
                    base_url=str(settings.BASE_HOST),
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                ) as client:
                    auth_response = await client.post(
                        f"{settings.API_V1_STR}/auth/token",
                        data={"username": self._email, "password": self._password},
                    )
                assert auth_response.status_code == 200, auth_response.text
                self._token = auth_response.json()["data"]["access_token"]

        return self._token

    def sync_auth_flow(
        self, request: httpx.Request
    ) -> typing.Generator[httpx.Request, httpx.Response, None]:
        raise RuntimeError("Cannot use a sync authentication class with httpx.AsyncClient")

    async def async_auth_flow(
        self, request: httpx.Request
    ) -> typing.AsyncGenerator[httpx.Request, httpx.Response]:
        token = await self._async_get_token()
        request.headers["Authorization"] = f"Bearer {token}"
        yield request


class AsyncClientFactory:
    """
    Factory for creating a httpx.AsyncClient with authentication support.
    This class is used to create an async client for testing purposes.
    """

    def __init__(self, main_app: typing.Callable, base_url: str) -> None:
        self.app = main_app
        self.base_url = base_url

    # TODO: I'm not sure about this method, but it works
    async def __call__(self, email: str | None = None, password: str | None = None) -> AsyncClient:
        """
        Creates a httpx.AsyncClient with authentication support.

        Args:
            email (str | None): The email address for authentication.
            password (str | None): The password for authentication.
        """
        auth = AsyncTokenAuth(email, password) if email and password else None
        return httpx.AsyncClient(
            transport=httpx.ASGITransport(app=self.app),
            base_url=self.base_url,
            headers={"Content-Type": "application/json"},
            auth=auth,
        )
