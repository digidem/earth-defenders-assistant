# /utils/logger.py
from loguru import logger


def setup_logger() -> None:
    logger.add("api.log", rotation="500 MB")
