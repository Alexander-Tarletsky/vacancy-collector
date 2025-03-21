import logging

from core.utils import MetaSingleton


class AppLogger(metaclass=MetaSingleton):
    _logger = None

    def __init__(self) -> None:
        self._logger = logging.getLogger(__name__)

    def get_logger(self) -> logging.Logger:
        return self._logger


# logging.basicConfig(
#     stream=sys.stdout,
#     level=logging.DEBUG if settings.log_level == "DEBUG" else logging.INFO
# )
