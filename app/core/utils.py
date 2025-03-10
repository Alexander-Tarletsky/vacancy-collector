from pathlib import Path
from threading import Lock

from db.connect import async_engine


async def get_db_version() -> str:
    async with async_engine.connect() as conn:
        version = await conn.scalar('SELECT version()')
        return version


async def is_template_exists(template_folder: str, template_name: str) -> bool:
    template = Path(f"{template_folder}/{template_name}")
    if template.is_file():
        return True
    return False


class MetaSingleton(type):
    """
    There is a thread-safe implementation of Singleton.
    """
    _instances = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]
