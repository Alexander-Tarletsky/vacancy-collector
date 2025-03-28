import logging

from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from app.db.connect import AsyncSessionFactory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
def init() -> None:
    try:
        db_session = AsyncSessionFactory()
        # Try to create session to check if DB is awake
        db_session.execute("SELECT 1")
    except Exception as e:
        logger.error(e)
        raise e


def main() -> None:
    logger.info("Initializing service")
    init()
    logger.info("Service finished initializing")


# import subprocess
# import sys
# from alembic.config import Config
# from alembic import command
# from app.core.config import ROOT
#
# alembic_cfg = Config(ROOT.parent / "alembic.ini")
#
# subprocess.run([sys.executable, "./app/backend_pre_start.py"])
# command.upgrade(alembic_cfg, "head")
# subprocess.run([sys.executable, "./app/initial_data.py"])


if __name__ == "__main__":
    main()
