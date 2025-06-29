from eda_config import ConfigLoader
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from eda_ai_api.api.routes.router import api_router
from eda_ai_api.core.config import API_PREFIX, APP_NAME, APP_VERSION
from eda_ai_api.core.event_handlers import start_app_handler, stop_app_handler
from eda_ai_api.utils.logger import setup_logger
from eda_ai_api.utils.error_handler import (
    handle_aiapi_exception,
    handle_validation_error,
    handle_generic_exception,
)
from eda_ai_api.utils.exceptions import AIAPIException

config = ConfigLoader.get_config()

# Setup logger with config-based level - this will only configure once due to the flag
log_level = "DEBUG" if config.services.ai_api.debug else "INFO"
setup_logger(log_level=log_level)

# Import logger after setup to ensure it's configured
from loguru import logger

logger.info(f"Starting {APP_NAME} v{APP_VERSION} with log level: {log_level}")


def get_app() -> FastAPI:
    """Create and configure FastAPI application with middleware and error handling"""

    fast_app = FastAPI(
        title=APP_NAME,
        version=APP_VERSION,
        debug=config.services.ai_api.debug,
        contact={
            "name": "Earth Defenders Assistant Team",
            "email": "support@earthdefenders.ai",
        },
        license_info={
            "name": "MIT License",
        },
        docs_url="/docs" if config.services.ai_api.debug else None,
        redoc_url="/redoc" if config.services.ai_api.debug else None,
    )

    # Add CORS middleware
    fast_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add request ID middleware
    @fast_app.middleware("http")
    async def add_request_id(request: Request, call_next):
        """Add request ID to headers for tracking"""
        import uuid

        request_id = str(uuid.uuid4())
        request.headers.__dict__["_list"].append(
            (b"x-request-id", request_id.encode())
        )
        response = await call_next(request)
        response.headers["x-request-id"] = request_id
        return response

    # Add custom exception handlers
    @fast_app.exception_handler(AIAPIException)
    async def aiapi_exception_handler(request: Request, exc: AIAPIException):
        """Handle custom AI API exceptions"""
        return await handle_aiapi_exception(request, exc)

    @fast_app.exception_handler(ValueError)
    async def validation_exception_handler(request: Request, exc: ValueError):
        """Handle validation errors"""
        return await handle_validation_error(request, exc)

    @fast_app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        """Handle all other exceptions"""
        return await handle_generic_exception(request, exc)

    # Include API router
    fast_app.include_router(api_router, prefix=API_PREFIX)

    # Add startup and shutdown event handlers
    fast_app.add_event_handler("startup", start_app_handler(fast_app))
    fast_app.add_event_handler("shutdown", stop_app_handler(fast_app))

    return fast_app


app = get_app()


def run_server() -> None:
    """Run the API server using config settings with improved configuration"""

    # Use localhost for development, configure via config for production
    host = "127.0.0.1"  # Default to localhost
    allow_external = (
        hasattr(config.services.ai_api, "allow_external")
        and config.services.ai_api.allow_external
    )
    if allow_external:
        host = "0.0.0.0"  # nosec B104 # Explicitly allowed in config

    # Configure uvicorn with production-ready settings
    uvicorn_config = {
        "app": "eda_ai_api.main:app",
        "host": host,
        "port": config.ports.ai_api,
        "reload": config.services.ai_api.debug,
        "log_level": "warning",  # Set to warning to avoid conflicts with loguru
        "access_log": False,  # Disable uvicorn access logs since we use loguru
        "workers": 1,  # Single worker for development, increase for production
    }

    # Add production settings when not in debug mode
    if not config.services.ai_api.debug:
        uvicorn_config.update(
            {
                "workers": 4,  # Multiple workers for production
                "worker_class": "uvicorn.workers.UvicornWorker",
                "limit_concurrency": 1000,
                "limit_max_requests": 10000,
                "timeout_keep_alive": 30,
            }
        )

    logger.info(f"Starting server on {host}:{config.ports.ai_api}")
    uvicorn.run(**uvicorn_config)


if __name__ == "__main__":
    run_server()
