import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


# Check if the test mode is enabled and the test database URL is set
if not settings.TEST_MODE or not settings.TEST_DATABASE_URI:
    raise ValueError(
        "Before running tests, you must set TEST_MODE and TEST_DATABASE_URI in settings."
    )

logger.info(f"Connected to database: {settings.TEST_DATABASE_URI}")

# We can also create a custom event loop fixture to override the default
# event loop (scope="session"), but this approach has aged out.
# https://docs.pytest.org/en/latest/asyncio.html#async-fixtures
# https://github.com/pytest-dev/pytest-asyncio/issues/38#issuecomment-1783557634


pytest_plugins = [
    "tests.fixtures",
]
