import logging
from logging import Logger
from typing import Optional


DEFAULT_LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s - %(message)s"


def configure_logging(level: int = logging.INFO, fmt: str = DEFAULT_LOG_FORMAT) -> None:
    """Configure root logger with a standard formatter if it has no handlers."""
    root_logger = logging.getLogger()
    if root_logger.handlers:
        return
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(fmt))
    root_logger.addHandler(handler)
    root_logger.setLevel(level)


def get_logger(name: Optional[str] = None) -> Logger:
    configure_logging()
    return logging.getLogger(name)
