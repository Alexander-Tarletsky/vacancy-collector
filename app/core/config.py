import logging
import pathlib

from dotenv import load_dotenv
from pydantic import AnyHttpUrl, EmailStr, field_validator, PostgresDsn
from pydantic_core.core_schema import ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict

# https://github.com/pydantic/pydantic/issues/1368
# https://docs.pydantic.dev/usage/settings/#dotenv-env-support
load_dotenv()

logger = logging.getLogger(__name__)

# Project Directories
BASE_ROOT = pathlib.Path(__file__).resolve().parent.parent
STATIC_ROOT = BASE_ROOT / "static"
TEMPLATES_ROOT = BASE_ROOT / "templates"


class Settings(BaseSettings):
    DEBUG: bool = False
    PYTHONASYNCIODEBUG: bool = False

    TEST_MODE: bool = False

    ENVIRONMENT: str = "development"
    IS_PRODUCTION: bool = False
    IS_DEVELOPMENT: bool = True
    IS_LOCAL: bool = False

    LOG_LEVEL: str = "INFO"

    @field_validator("ENVIRONMENT", mode="before")
    def set_environment(cls, value: str) -> str:  # NOQA: N805
        if value not in ("development", "production", "local"):
            raise ValueError("Invalid environment")
        return value

    @field_validator("IS_PRODUCTION", mode="before")
    def set_is_production(cls, value: bool, info: ValidationInfo) -> bool:  # NOQA: N805
        return info.data.get("ENVIRONMENT") == "production"

    @field_validator("IS_DEVELOPMENT", mode="before")
    def set_is_development(cls, value: bool, info: ValidationInfo) -> bool:  # NOQA: N805
        return info.data.get("ENVIRONMENT") == "development"

    @field_validator("IS_LOCAL", mode="before")
    def set_is_local(cls, value: bool, info: ValidationInfo) -> bool:  # NOQA: N805
        return info.data.get("ENVIRONMENT") == "local"

    FIRST_SUPERUSER: EmailStr = "root@root.com"
    FIRST_SUPERUSER_PW: str = "strongpassword"
    SALT: str = "a91349ae8f7"

    JWT_SECRET: str = "JWT_SECRET"  # NOQA: S105
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 3

    BASE_HOST: AnyHttpUrl = "http://localhost:8000"
    API_V1_STR: str = "/api/v1"

    DB_HOST: str = "db"
    DB_PORT: int = 5432
    DB_USER: str = "db_user"
    DB_PASSWORD: str = "db_password"  # NOQA: S105
    DB_NAME: str = "vacancy_collector"
    DB_ECHO: bool | None = None
    DATABASE_URI: PostgresDsn | str | None = None

    TEST_DB_HOST: str = "test_db"
    TEST_DB_PORT: int = 5433
    TEST_DB_USER: str = "test_db_user"
    TEST_DB_PASSWORD: str = "test_db_password"  # NOQA: S105
    TEST_DB_NAME: str = "test_vacancy_collector"
    TEST_DATABASE_URI: PostgresDsn | str | None = None

    @field_validator("DATABASE_URI", mode="before")
    def assemble_db_uri(cls, value: str | None, info: ValidationInfo) -> str:  # NOQA: N805
        if isinstance(value, str):
            # There is assumed that if you set the DB URL yourself, then this is your responsibility
            logger.info(f"DATABASE_URI is: {value}")
            return value

        host = info.data.get("IS_LOCAL") and "127.0.0.1" or info.data.get("DB_HOST")

        value = PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=info.data.get("DB_USER"),
            password=info.data.get("DB_PASSWORD"),
            host=host,
            port=info.data.get("DB_PORT"),
            path=info.data.get("DB_NAME"),
        ).unicode_string()
        logger.info(f"DATABASE_URI is assembled: {value}")

        return value

    @field_validator("TEST_DATABASE_URI", mode="before")
    def assemble_test_db_uri(cls, value: str | None, info: ValidationInfo) -> str:  # NOQA: N805
        if isinstance(value, str):
            # There is assumed that if you set the DB URL yourself, then this is your responsibility
            logger.info(f"TEST_DATABASE_URI is: {value}")
            return value

        if info.data.get("TEST_MODE"):
            if not info.data.get("TEST_DB_PASSWORD"):
                raise ValueError("Before running tests, you must set TEST_DB_PASSWORD in settings.")

        value = PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=info.data.get("TEST_DB_USER"),
            password=info.data.get("TEST_DB_PASSWORD"),
            host=info.data.get("TEST_DB_HOST"),
            port=info.data.get("TEST_DB_PORT"),
            path=info.data.get("TEST_DB_NAME"),
        ).unicode_string()

        logger.info(f"TEST_DATABASE_URI is assembled: {value}")

        return value

    @field_validator("DB_ECHO", mode="before")
    def assemble_db_echo(cls, value: str | int | bool | None, info: ValidationInfo) -> bool:  # NOQA: N805
        if isinstance(value, str | int | bool):
            return bool(value)

        if info.data.get("DEBUG") or info.data.get("TEST_MODE"):
            return True

        return False

    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = [
        "http://localhost",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:3000",
        "http://localhost:3000",
        "http://localhost:8000",
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str] | str:  # NOQA: N805
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list | str):
            return v
        raise ValueError(v)

    @field_validator("DEBUG", "TEST_MODE", "PYTHONASYNCIODEBUG", mode="before")
    def assemble_bool(cls, value: str | int | bool | None) -> bool:  # NOQA: N805
        return bool(value)

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file="./.env",
        env_file_encoding="utf-8",
    )


settings = Settings()
