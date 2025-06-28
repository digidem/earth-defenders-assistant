# /utils/logger.py
import sys
from pathlib import Path
from loguru import logger

# Remove default handler to avoid duplicate logs
logger.remove()

# Define log format with structured data
LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "<level>{message}</level>"
)

# Define structured format for JSON logging in production
JSON_FORMAT = {
    "time": "{time:YYYY-MM-DD HH:mm:ss.SSS}",
    "level": "{level}",
    "name": "{name}",
    "function": "{function}",
    "line": "{line}",
    "message": "{message}",
    "extra": "{extra}",
}


def setup_logger(log_level: str = "INFO", log_file: str = "api.log") -> None:
    """
    Configure structured logging with proper levels and formatting.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file
    """
    # Create logs directory if it doesn't exist
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Console handler with colored output
    logger.add(
        sys.stdout,
        format=LOG_FORMAT,
        level=log_level,
        colorize=True,
        backtrace=True,
        diagnose=True,
    )

    # File handler with rotation and compression
    logger.add(
        log_file,
        format=LOG_FORMAT,
        level=log_level,
        rotation="100 MB",
        retention="30 days",
        compression="zip",
        backtrace=True,
        diagnose=True,
    )

    # Error file handler for critical errors
    error_log_path = (
        log_path.parent / f"{log_path.stem}_errors{log_path.suffix}"
    )
    logger.add(
        str(error_log_path),
        format=LOG_FORMAT,
        level="ERROR",
        rotation="50 MB",
        retention="90 days",
        compression="zip",
        backtrace=True,
        diagnose=True,
    )


# Initialize logger with default settings
setup_logger()
