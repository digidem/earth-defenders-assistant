# /utils/logger.py
from loguru import logger


def setup_logging():
    logger.add("api.log", rotation="500 MB")
