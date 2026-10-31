import json

from versechat_backend.core.logger import get_logger

logger = get_logger()


def load_json(path: str):
    """Loads json file and returns a python dictionary"""
    try:
        with open(path, "rb") as f:
            content = json.load(f)

        return content
    except FileNotFoundError:
        logger.exception(f"File not found at {path}")
        raise
    except json.JSONDecodeError:
        logger.exception("Couldn't decode Json")
        raise
