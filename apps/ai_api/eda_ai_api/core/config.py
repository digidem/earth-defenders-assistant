from starlette.config import Config
from starlette.datastructures import Secret

APP_VERSION = "0.0.1"
APP_NAME = "AI API for Earth Defenders Assistant"
API_PREFIX = "/api"

config = Config(".env")

API_KEY: Secret = config("API_KEY", cast=Secret)
IS_DEBUG: bool = config("IS_DEBUG", cast=bool, default=False)
