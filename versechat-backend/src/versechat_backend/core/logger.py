# src/versechat_backend/core/logger.py
import logging
import os
import sys
from logging.handlers import RotatingFileHandler

os.makedirs("logs", exist_ok=True)

file_handler = RotatingFileHandler(
    filename="logs/app.log",
    mode="a",
    maxBytes=5 * 1024 * 1024,
    backupCount=5,
    encoding="utf-8",
)


def get_logger() -> logging.Logger:
    """Return a logger configured to write to stdout."""
    logger = logging.getLogger(__name__)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.addHandler(file_handler)

    logger.setLevel(logging.INFO)
    logger.propagate = False

    return logger
