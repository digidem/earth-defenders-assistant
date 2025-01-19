from pathlib import Path
from typing import Optional, Union
import yaml
from pydantic import BaseModel

class ApiKeys(BaseModel):
    groq: str
    huggingface: str
    serper: str
    langtrace: str
    trigger: str

class SupabaseConfig(BaseModel):
    url: str
    service_key: str

class DatabaseConfig(BaseModel):
    host: str
    port: int
    user: str
    password: str
    database: str

class AIModelConfig(BaseModel):
    provider: str
    model: str
    temperature: float
    description: str

class Reactions(BaseModel):
    queued: str
    working: str
    done: str
    error: str

class WhatsApp(BaseModel):
    bot_prefix: str
    cmd_prefix: str
    bot_name: str
    enable_reactions: bool
    reactions: Reactions

class Config(BaseModel):
    ports: dict[str, int]
    api_keys: ApiKeys
    databases: dict[str, Union[SupabaseConfig, DatabaseConfig]]
    ai_models: dict[str, AIModelConfig]
    whatsapp: WhatsApp

class ConfigLoader:
    _instance: Optional[Config] = None
    
    @classmethod
    def get_config(cls) -> Config:
        if cls._instance is None:
            config_path = Path(__file__).parents[4] / "config.yaml"
            with open(config_path) as f:
                config_data = yaml.safe_load(f)
            cls._instance = Config(**config_data)
        return cls._instance

# Usage example:
# from eda_config import ConfigLoader
# config = ConfigLoader.get_config()
# groq_key = config.api_keys.groq