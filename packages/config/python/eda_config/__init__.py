from .config import ConfigLoader
from .types import Config

config = ConfigLoader.get_config()

__all__ = ["Config", "config"]