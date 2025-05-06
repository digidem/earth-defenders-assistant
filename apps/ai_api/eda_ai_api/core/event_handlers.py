from typing import Callable
from fastapi import FastAPI
from loguru import logger

# Import VectorMemory to access the cleanup method
from eda_ai_api.utils.vector_memory import VectorMemory


async def _startup_message(app: FastAPI) -> None:
    logger.info(f"Application '{app.title}' version {app.version} started successfully.")
    # Add the cleanup call here
    try:
        logger.info("Attempting to run document cleanup on startup...")
        memory = VectorMemory() # Initialize VectorMemory
        removed_count = await memory.cleanup_expired_documents()
        if removed_count > 0:
            logger.info(f"Successfully removed {removed_count} expired documents during startup.")
        else:
            logger.info("No expired documents found or removed during startup cleanup.")
    except Exception as e:
        logger.error(f"Error during startup document cleanup: {str(e)}", exc_info=True)


def _shutdown_message(app: FastAPI) -> None:
    logger.info(f"Application '{app.title}' version {app.version} shutting down...")


def start_app_handler(app: FastAPI) -> Callable:
    async def startup() -> None: # Make the inner function async
        await _startup_message(app) # Await the async function

    return startup


def stop_app_handler(app: FastAPI) -> Callable:
    def shutdown() -> None:
        _shutdown_message(app)

    return shutdown
