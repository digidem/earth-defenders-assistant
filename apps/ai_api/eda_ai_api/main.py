from eda_config import ConfigLoader
from fastapi import FastAPI

from eda_ai_api.api.routes.router import api_router
from eda_ai_api.core.config import API_PREFIX, APP_NAME, APP_VERSION
from eda_ai_api.core.event_handlers import start_app_handler, stop_app_handler

config = ConfigLoader.get_config()


def get_app() -> FastAPI:
    fast_app = FastAPI(
        title=APP_NAME,
        version=APP_VERSION,
        debug=config.services.ai_api.debug,
    )
    fast_app.include_router(api_router, prefix=API_PREFIX)

    fast_app.add_event_handler("startup", start_app_handler(fast_app))
    fast_app.add_event_handler("shutdown", stop_app_handler(fast_app))

    return fast_app


app = get_app()


def run_server() -> None:
    """Run the API server using config settings"""
    import uvicorn

    # Use localhost for development, configure via config for production
    host = "127.0.0.1"  # Default to localhost
    if (
        hasattr(config.services.ai_api, "allow_external")
        and config.services.ai_api.allow_external
    ):
        host = "0.0.0.0"  # nosec B104 # Explicitly allowed in config

    uvicorn.run(
        "eda_ai_api.main:app", host=host, port=config.ports.ai_api, reload=True
    )


if __name__ == "__main__":
    run_server()
