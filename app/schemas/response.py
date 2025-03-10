from pydantic import BaseModel


class Response(BaseModel):
    status_code: int
    message: str
    data: list | dict | None = None
