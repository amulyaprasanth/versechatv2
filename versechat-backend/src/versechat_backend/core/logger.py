# src/versechat_backend/core/logger.py

import logging
import sys


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

    logger.setLevel(logging.INFO)
    logger.propagate = False

    return logger
