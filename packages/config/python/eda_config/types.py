from typing import List, Optional, Union, Dict
from pydantic import BaseModel


class Neo4jAuth(BaseModel):
    user: str
    password: str


class Neo4jHealthcheck(BaseModel):
    interval: int
    timeout: int
    retries: int


class Neo4jConfig(BaseModel):
    host: str
    auth: Neo4jAuth
    plugins: List[str]
    healthcheck: Neo4jHealthcheck


class RedisConfig(BaseModel):
    host: str
    port: Optional[int] = None  # Make port optional
    tls_disabled: bool


class DatabaseConfig(BaseModel):
    host: str
    port: Optional[int] = None  # Make port optional
    user: str
    password: str
    database: str


class OpenPanelKeys(BaseModel):
    client_id: str
    secret: str


class SentryKeys(BaseModel):
    auth_token: str


class ApiKeys(BaseModel):
    groq: str
    huggingface: str
    serper: str
    langtrace: str
    trigger: str
    resend: str
    openai: str
    openrouter: str  # Added OpenRouter API key
    dub: str
    sentry: SentryKeys
    deepseek: str  # Added DeepSeek API key


class DbPorts(BaseModel):
    postgres: int
    trigger_postgres: int  # Add new port
    langtrace_postgres: int  # Add new port
    redis: int
    neo4j: Dict[str, int]
    clickhouse: int


class Ports(BaseModel):
    messaging: int
    ai_api: int
    langtrace: int
    trigger: int
    remix: int
    whatsapp: int
    dashboard: int
    landingpage: int
    docs: int
    db: DbPorts


class AIModelConfig(BaseModel):
    provider: str
    model: str
    temperature: float
    description: str


class WhatsappReactions(BaseModel):
    queued: str
    working: str
    done: str
    error: str


class WhatsappConfig(BaseModel):
    bot_prefix: str
    cmd_prefix: str
    bot_name: str
    enable_reactions: bool
    reactions: WhatsappReactions
    puppeteer_path: str
    ignore_messages_warning: bool
    mongodb_uri: str


class TriggerAuth(BaseModel):
    magic_link_secret: str
    session_secret: str
    encryption_key: str
    provider_secret: str
    coordinator_secret: str


class TriggerWorker(BaseModel):
    http_port: int
    coordinator_host: str
    coordinator_port: int


class TriggerDeployment(BaseModel):
    worker: TriggerWorker
    docker: Dict[str, str]


class TriggerConfig(BaseModel):
    project_id: str
    api_url: str
    environment: str
    runtime: str
    v3_enabled: bool
    concurrency: Dict[str, int]
    auth: TriggerAuth
    deployment: TriggerDeployment
    sentry: Dict[str, str]


class ResendConfig(BaseModel):
    from_email: str
    reply_to: str


class LangTraceApiConfig(BaseModel):
    host: str


class LangTraceAdminConfig(BaseModel):
    email: str
    password: str
    enable_login: bool


class LangTraceTelemetryConfig(BaseModel):
    enabled: bool


class LangTracePosthogConfig(BaseModel):
    host: str


class LangTraceConfig(BaseModel):
    api: LangTraceApiConfig
    admin: LangTraceAdminConfig
    telemetry: LangTraceTelemetryConfig
    posthog: LangTracePosthogConfig


class DashboardAuthAzure(BaseModel):
    client_id: str
    client_secret: str
    tenant_id: str


class DashboardAuthGoogle(BaseModel):
    client_id: str
    secret: str


class DashboardAuth(BaseModel):
    nextauth_secret: str
    azure: DashboardAuthAzure
    google: DashboardAuthGoogle


class DashboardConfig(BaseModel):
    auth: DashboardAuth


class UpstashConfig(BaseModel):
    redis_url: str
    redis_token: str


# Update AIApiConfig class to include conversation_history_limit and relevant_history_limit
class AIApiConfig(BaseModel):
    debug: bool
    conversation_history_limit: Optional[int] = 5 
    relevant_history_limit: Optional[int] = 3 


# Update ServicesConfig class
class ServicesConfig(BaseModel):
    ai_api: AIApiConfig  # Change from Dict to AIApiConfig
    whatsapp: WhatsappConfig
    trigger: TriggerConfig
    resend: ResendConfig
    langtrace: LangTraceConfig
    dashboard: DashboardConfig
    upstash: UpstashConfig


# Add PocketBaseAdmin class
class PocketBaseAdmin(BaseModel):
    email: str
    password: str


# Add PocketBaseConfig class after DatabaseConfig class
class PocketBaseConfig(BaseModel):
    url: str
    admin: PocketBaseAdmin


# Update DatabasesConfig class to include PocketBase
class DatabasesConfig(BaseModel):
    pocketbase: PocketBaseConfig  # Add this line
    langtrace_postgres: DatabaseConfig
    langtrace_clickhouse: DatabaseConfig
    trigger_postgres: DatabaseConfig
    redis: RedisConfig
    neo4j: Neo4jConfig


# Update the main Config class to use the new DatabasesConfig
class Config(BaseModel):
    ports: Ports
    api_keys: ApiKeys
    databases: DatabasesConfig  # Changed from Dict to DatabasesConfig
    services: ServicesConfig
    ai_models: Dict[str, AIModelConfig]
    access: Dict[str, List[str]]
