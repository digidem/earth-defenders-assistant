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


class GoogleCloudKeys(BaseModel):
    service_account_path: str


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
    google_ai_studio: str  # Added Google AI Studio API key
    google_cloud: GoogleCloudKeys  # Added Google Cloud credentials


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
    enable_tts: bool  # Add TTS enable flag
    reactions: WhatsappReactions
    puppeteer_path: str
    ignore_messages_warning: bool
    mongodb_uri: str

    # API Configuration
    ai_api_base_url: str = "http://localhost"
    api_timeout_seconds: int = 600  # 10 minutes
    reconnection_delay_seconds: int = 5

    # Language and Localization
    default_language: str = "pt"
    transcription_language: str = "pt"

    # Document Processing
    private_document_ttl_days: int = 1
    group_document_ttl_days: int = 7

    # Message Processing
    max_message_length: int = 10000
    min_tts_length: int = 10
    max_tts_length: int = 500

    # File Processing
    max_filename_length: int = 255
    allowed_file_types: List[str] = ["pdf", "csv"]

    # Audio Processing
    audio_mime_type: str = "audio/ogg; codecs=opus"
    audio_filename: str = "audio.ogg"

    # Error Messages
    error_messages: Dict[str, str] = {
        "NO_RESPONSE": "Desculpe, não consegui gerar uma resposta. Tente novamente.",
        "HTTP_ERROR": "Ops, tive um problema técnico. Pode tentar novamente?",
        "TIMEOUT": "Desculpe, demorei muito para responder. Pode tentar novamente?",
        "UNKNOWN": "Ocorreu um erro inesperado. Pode tentar novamente?",
        "AUDIO_DOWNLOAD_FAILED": "Não consegui baixar o áudio.",
        "AUDIO_TRANSCRIPTION_FAILED": "Erro ao transcrever o áudio.",
        "DOCUMENT_DOWNLOAD_FAILED": "Não foi possível baixar o arquivo.",
        "DOCUMENT_PROCESSING_FAILED": "Erro ao processar o arquivo. Por favor, tente novamente.",
    }

    # Success Messages
    success_messages: Dict[str, str] = {
        "DOCUMENT_PROCESSED": "✅ {file_type} processado com sucesso!\n\nAgora você pode fazer perguntas sobre o conteúdo deste arquivo diretamente por mensagem.\n\n⏰ O arquivo será mantido por {ttl_days} dia(s).",
        "AUDIO_TRANSCRIPTION_COMPLETE": "Áudio transcrito com sucesso",
    }

    # Status Messages
    status_messages: Dict[str, str] = {
        "WAITING": "Estou analisando sua mensagem... Como preciso pensar com cuidado, pode demorar alguns minutos.",
        "TOO_MANY_UNREAD_GROUP": "Too many unread messages ({count}) since I've last seen this chat. I'm ignoring them. If you need me to respond, please @mention me or quote my last completion in this chat.",
        "TOO_MANY_UNREAD_PRIVATE": "Too many unread messages ({count}) since I've last seen this chat. I'm ignoring them. If you need me to respond, please message me again.",
    }


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


# Add TTSConfig class
class TTSConfig(BaseModel):
    provider: str
    language_code: str
    voice_name: str
    audio_encoding: str
    effects_profile_id: List[str]
    pitch: float
    speaking_rate: float
    output_format: str


# Update AIApiConfig class to include all constants from constants.py
class AIApiConfig(BaseModel):
    debug: bool
    conversation_history_limit: Optional[int] = 5
    relevant_history_limit: Optional[int] = 3

    # File Processing Constants
    max_file_size_mb: int = 50
    allowed_image_types: List[str] = ["image/jpeg", "image/png", "image/webp"]
    allowed_audio_types: List[str] = [
        "audio/mpeg",
        "audio/mp4",
        "audio/mpga",
        "audio/wav",
        "audio/webm",
        "audio/ogg",
        "application/octet-stream",
    ]
    allowed_document_types: List[str] = [
        "application/pdf",
        "text/csv",
        "application/csv",
    ]

    # Audio Processing Constants
    audio_timeout_seconds: int = 300
    transcription_timeout_seconds: int = 60
    audio_chunk_size: int = 8192

    # Memory and Storage Constants
    default_ttl_days: int = 30
    max_conversation_history: int = 50
    max_relevant_history: int = 10
    max_document_chunks: int = 1000
    vector_similarity_threshold: float = 0.7

    # Agent Constants
    max_agent_steps: int = 10
    agent_timeout_seconds: int = 600
    max_retries: int = 3
    retry_delay_seconds: int = 1

    # Security Constants
    max_filename_length: int = 255
    allowed_file_extensions: List[str] = [
        ".pdf",
        ".csv",
        ".txt",
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
    ]
    temp_dir_prefix: str = "/tmp/"

    # API Constants
    max_request_size: int = 100 * 1024 * 1024  # 100MB
    rate_limit_requests: int = 100
    rate_limit_window_seconds: int = 3600  # 1 hour

    # Platform Constants
    supported_platforms: List[str] = ["whatsapp", "telegram", "website", "api"]
    default_platform: str = "whatsapp"

    # Media Type Mappings
    media_type_map: Dict[str, str] = {
        ".wav": "audio/wav",
        ".mp3": "audio/mpeg",
        ".ogg": "audio/ogg",
        ".pdf": "application/pdf",
        ".csv": "text/csv",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }

    # Error Messages
    error_messages: Dict[str, str] = {
        "FILE_TOO_LARGE": "File size exceeds maximum allowed size of 50MB",
        "INVALID_FILE_TYPE": "File type not supported",
        "FILE_NOT_FOUND": "File not found",
        "PROCESSING_ERROR": "Error processing file",
        "AUTHENTICATION_FAILED": "Authentication failed",
        "INVALID_REQUEST": "Invalid request data",
        "SERVICE_UNAVAILABLE": "Service temporarily unavailable",
        "TIMEOUT_ERROR": "Request timed out",
        "RATE_LIMIT_EXCEEDED": "Rate limit exceeded",
    }

    # Success Messages
    success_messages: Dict[str, str] = {
        "FILE_UPLOADED": "File uploaded successfully",
        "AUDIO_GENERATED": "Audio generated successfully",
        "TRANSCRIPTION_COMPLETE": "Transcription completed successfully",
        "DOCUMENT_PROCESSED": "Document processed successfully",
    }

    # Logging Constants
    log_levels: Dict[str, str] = {
        "DEBUG": "DEBUG",
        "INFO": "INFO",
        "WARNING": "WARNING",
        "ERROR": "ERROR",
        "CRITICAL": "CRITICAL",
    }


# Update ServicesConfig class to include TTS
class ServicesConfig(BaseModel):
    ai_api: AIApiConfig  # Change from Dict to AIApiConfig
    whatsapp: WhatsappConfig
    trigger: TriggerConfig
    resend: ResendConfig
    langtrace: LangTraceConfig
    dashboard: DashboardConfig
    upstash: UpstashConfig
    tts: TTSConfig  # Add TTS configuration


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
