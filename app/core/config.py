import pathlib
from typing import List, Union

from pydantic import AnyHttpUrl, EmailStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Project Directories
ROOT = pathlib.Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    DEBUG: bool = False
    FIRST_SUPERUSER: EmailStr = "root@root.com"
    FIRST_SUPERUSER_PW: str = "strongpassword"
    SALT: str= "a91349ae8f7"

    API_V1_STR: str = "/api/v1"
    JWT_SECRET: str = "TEST_SECRET_KEY"
    ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 3

    DB_HOST: str = "db"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_NAME: str = "vacancy_collector"
    # POSTGRES_USER: str = "postgres"
    # POSTGRES_PASSWORD: str = "postgres"
    # POSTGRES_DB: str = "vacancy_collector"

    @property
    def DATABASE_URL_ASYNC(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"  # NOQA

    TEST_DATABASE_URI: str | None = "postgresql+asyncpg://postgres:postgres@db:5432/test_db"

    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8000",
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    @field_validator("DEBUG", mode="before")
    def assemble_bool(cls, v: Union[str, bool, None]):
        return bool(v)


    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_file_encoding="utf-8",
    )

    # DATABASE_URI: Optional[PostgresDsn] = None
    #
    # @field_validator('DATABASE_URI', mode='before')
    # @classmethod
    # def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> str:
    #     if isinstance(v, str):
    #         return v
    #
    #     params = dict(scheme='postgresql+asyncpg',
    #                   user=values.get('POSTGRES_USER'),
    #                   password=values.get('POSTGRES_PASSWORD'),
    #                   host=values.get('POSTGRES_SERVER'),
    #                   path=f"/{values.get('POSTGRES_DB')}"
    #                   )
    #     return PostgresDsn.build(**params)


settings = Settings()
