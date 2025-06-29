import { z } from "zod";

// Database Schemas
export const DatabaseConfigSchema = z.object({
  host: z.string(),
  port: z.number().optional(),
  user: z.string(),
  password: z.string(),
  database: z.string(),
});

export const Neo4jAuthSchema = z.object({
  user: z.string(),
  password: z.string(),
});

const Neo4jConfigSchema = z.object({
  host: z.string(),
  auth: Neo4jAuthSchema,
  plugins: z.array(z.string()),
  healthcheck: z.object({
    interval: z.number(),
    timeout: z.number(),
    retries: z.number(),
  }),
});

const RedisConfigSchema = z.object({
  host: z.string(),
  port: z.number().optional(), // Make port optional
  tls_disabled: z.boolean(),
});

const PocketBaseAdminSchema = z.object({
  email: z.string(),
  password: z.string(),
});

const PocketBaseConfigSchema = z.object({
  url: z.string(),
  admin: PocketBaseAdminSchema,
});

// Service Configs
const WhatsAppConfigSchema = z.object({
  bot_prefix: z.string(),
  cmd_prefix: z.string(),
  bot_name: z.string(),
  enable_reactions: z.boolean(),
  enable_tts: z.boolean(), // Add TTS enable flag
  reactions: z.object({
    queued: z.string(),
    working: z.string(),
    done: z.string(),
    error: z.string(),
  }),
  puppeteer_path: z.string(),
  ignore_messages_warning: z.boolean(),
  mongodb_uri: z.string(),

  // API Configuration
  ai_api_base_url: z.string().default("http://localhost"),
  api_timeout_seconds: z.number().default(600), // 10 minutes
  reconnection_delay_seconds: z.number().default(5),

  // Language and Localization
  default_language: z.string().default("pt"),
  transcription_language: z.string().default("pt"),

  // Document Processing
  private_document_ttl_days: z.number().default(1),
  group_document_ttl_days: z.number().default(7),

  // Message Processing
  max_message_length: z.number().default(10000),
  min_tts_length: z.number().default(10),
  max_tts_length: z.number().default(500),

  // File Processing
  max_filename_length: z.number().default(255),
  allowed_file_types: z.array(z.string()).default(["pdf", "csv"]),

  // Audio Processing
  audio_mime_type: z.string().default("audio/ogg; codecs=opus"),
  audio_filename: z.string().default("audio.ogg"),

  // Error Messages
  error_messages: z.record(z.string(), z.string()).default({
    NO_RESPONSE: "Desculpe, não consegui gerar uma resposta. Tente novamente.",
    HTTP_ERROR: "Ops, tive um problema técnico. Pode tentar novamente?",
    TIMEOUT: "Desculpe, demorei muito para responder. Pode tentar novamente?",
    UNKNOWN: "Ocorreu um erro inesperado. Pode tentar novamente?",
    AUDIO_DOWNLOAD_FAILED: "Não consegui baixar o áudio.",
    AUDIO_TRANSCRIPTION_FAILED: "Erro ao transcrever o áudio.",
    DOCUMENT_DOWNLOAD_FAILED: "Não foi possível baixar o arquivo.",
    DOCUMENT_PROCESSING_FAILED:
      "Erro ao processar o arquivo. Por favor, tente novamente.",
  }),

  // Success Messages
  success_messages: z.record(z.string(), z.string()).default({
    DOCUMENT_PROCESSED:
      "✅ {file_type} processado com sucesso!\n\nAgora você pode fazer perguntas sobre o conteúdo deste arquivo diretamente por mensagem.\n\n⏰ O arquivo será mantido por {ttl_days} dia(s).",
    AUDIO_TRANSCRIPTION_COMPLETE: "Áudio transcrito com sucesso",
  }),

  // Status Messages
  status_messages: z.record(z.string(), z.string()).default({
    WAITING:
      "Estou analisando sua mensagem... Como preciso pensar com cuidado, pode demorar alguns minutos.",
    TOO_MANY_UNREAD_GROUP:
      "Too many unread messages ({count}) since I've last seen this chat. I'm ignoring them. If you need me to respond, please @mention me or quote my last completion in this chat.",
    TOO_MANY_UNREAD_PRIVATE:
      "Too many unread messages ({count}) since I've last seen this chat. I'm ignoring them. If you need me to respond, please message me again.",
  }),
});

const TriggerConfigSchema = z.object({
  project_id: z.string(),
  api_url: z.string(),
  environment: z.string(),
  runtime: z.string(),
  v3_enabled: z.boolean(),
  concurrency: z.object({
    org_execution_limit: z.number(),
    env_execution_limit: z.number(),
  }),
  auth: z.object({
    magic_link_secret: z.string(),
    session_secret: z.string(),
    encryption_key: z.string(),
    provider_secret: z.string(),
    coordinator_secret: z.string(),
  }),
  deployment: z.object({
    worker: z.object({
      http_port: z.number(),
      coordinator_host: z.string(),
      coordinator_port: z.number(),
    }),
    docker: z.object({
      publish_ip: z.string(),
    }),
  }),
  sentry: z.object({
    auth_token: z.string(),
    dsn: z.string(),
    org: z.string(),
    project: z.string(),
  }),
});

const ResendConfigSchema = z.object({
  from_email: z.string(),
  reply_to: z.string(),
});

const LangTraceConfigSchema = z.object({
  api: z.object({
    host: z.string(),
  }),
  admin: z.object({
    email: z.string(),
    password: z.string(),
    enable_login: z.boolean(),
  }),
  telemetry: z.object({
    enabled: z.boolean(),
  }),
  posthog: z.object({
    host: z.string(),
  }),
});

const DashboardAuthConfigSchema = z.object({
  nextauth_secret: z.string(),
  azure: z.object({
    client_id: z.string(),
    client_secret: z.string(),
    tenant_id: z.string(),
  }),
  google: z.object({
    client_id: z.string(),
    secret: z.string(),
  }),
});

const DashboardConfigSchema = z.object({
  auth: DashboardAuthConfigSchema,
});

const UpstashConfigSchema = z.object({
  redis_url: z.string(),
  redis_token: z.string(),
});

// Add TTS Config Schema
const TTSConfigSchema = z.object({
  provider: z.string(),
  language_code: z.string(),
  voice_name: z.string(),
  audio_encoding: z.string(),
  effects_profile_id: z.array(z.string()),
  pitch: z.number(),
  speaking_rate: z.number(),
  output_format: z.string(),
});

// API Keys
export const ApiKeysSchema = z.object({
  groq: z.string(),
  huggingface: z.string(),
  serper: z.string(),
  langtrace: z.string(),
  trigger: z.string(),
  resend: z.string(),
  openai: z.string(),
  openrouter: z.string(),
  dub: z.string(),
  sentry: z.object({
    auth_token: z.string(),
  }),
  deepseek: z.string(),
  google_ai_studio: z.string(), // Added Google AI Studio API key
  google_cloud: z.object({
    service_account_path: z.string(),
  }),
});

// AI Models
const AIModelConfigSchema = z.object({
  provider: z.string(),
  model: z.string(),
  temperature: z.number(),
  description: z.string(),
});

// Update the AIApiConfig schema
const AIApiConfigSchema = z.object({
  debug: z.boolean(),
  allow_external: z.boolean().default(false), // Allow external connections (production setting)
  conversation_history_limit: z.number().default(5),
  relevant_history_limit: z.number().default(3),

  // File Processing Constants
  max_file_size_mb: z.number().default(50),
  allowed_image_types: z
    .array(z.string())
    .default(["image/jpeg", "image/png", "image/webp"]),
  allowed_audio_types: z
    .array(z.string())
    .default([
      "audio/mpeg",
      "audio/mp4",
      "audio/mpga",
      "audio/wav",
      "audio/webm",
      "audio/ogg",
      "application/octet-stream",
    ]),
  allowed_document_types: z
    .array(z.string())
    .default(["application/pdf", "text/csv", "application/csv"]),

  // Audio Processing Constants
  audio_timeout_seconds: z.number().default(300),
  transcription_timeout_seconds: z.number().default(60),
  audio_chunk_size: z.number().default(8192),

  // Memory and Storage Constants
  default_ttl_days: z.number().default(30),
  max_conversation_history: z.number().default(50),
  max_relevant_history: z.number().default(10),
  max_document_chunks: z.number().default(1000),
  vector_similarity_threshold: z.number().default(0.7),

  // Agent Constants
  max_agent_steps: z.number().default(10),
  agent_timeout_seconds: z.number().default(600),
  max_retries: z.number().default(3),
  retry_delay_seconds: z.number().default(1),

  // Security Constants
  max_filename_length: z.number().default(255),
  allowed_file_extensions: z
    .array(z.string())
    .default([".pdf", ".csv", ".txt", ".jpg", ".jpeg", ".png", ".webp"]),
  temp_dir_prefix: z.string().default("/tmp/"),

  // API Constants
  max_request_size: z.number().default(100 * 1024 * 1024), // 100MB
  rate_limit_requests: z.number().default(100),
  rate_limit_window_seconds: z.number().default(3600), // 1 hour

  // Platform Constants
  supported_platforms: z
    .array(z.string())
    .default(["whatsapp", "telegram", "website", "api"]),
  default_platform: z.string().default("whatsapp"),

  // Media Type Mappings
  media_type_map: z.record(z.string(), z.string()).default({
    ".wav": "audio/wav",
    ".mp3": "audio/mpeg",
    ".ogg": "audio/ogg",
    ".pdf": "application/pdf",
    ".csv": "text/csv",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
  }),

  // Error Messages
  error_messages: z.record(z.string(), z.string()).default({
    FILE_TOO_LARGE: "File size exceeds maximum allowed size of 50MB",
    INVALID_FILE_TYPE: "File type not supported",
    FILE_NOT_FOUND: "File not found",
    PROCESSING_ERROR: "Error processing file",
    AUTHENTICATION_FAILED: "Authentication failed",
    INVALID_REQUEST: "Invalid request data",
    SERVICE_UNAVAILABLE: "Service temporarily unavailable",
    TIMEOUT_ERROR: "Request timed out",
    RATE_LIMIT_EXCEEDED: "Rate limit exceeded",
  }),

  // Success Messages
  success_messages: z.record(z.string(), z.string()).default({
    FILE_UPLOADED: "File uploaded successfully",
    AUDIO_GENERATED: "Audio generated successfully",
    TRANSCRIPTION_COMPLETE: "Transcription completed successfully",
    DOCUMENT_PROCESSED: "Document processed successfully",
  }),

  // Logging Constants
  log_levels: z.record(z.string(), z.string()).default({
    DEBUG: "DEBUG",
    INFO: "INFO",
    WARNING: "WARNING",
    ERROR: "ERROR",
    CRITICAL: "CRITICAL",
  }),
});

export const ConfigSchema = z.object({
  ports: z.object({
    messaging: z.number(),
    ai_api: z.number(),
    langtrace: z.number(),
    trigger: z.number(),
    remix: z.number(),
    whatsapp: z.number(),
    dashboard: z.number(),
    landingpage: z.number(),
    docs: z.number(),
    db: z.object({
      postgres: z.number(),
      trigger_postgres: z.number(), // Add new port
      langtrace_postgres: z.number(), // Add new port
      redis: z.number(),
      neo4j: z.object({
        http: z.number(),
        bolt: z.number(),
      }),
      clickhouse: z.number(),
    }),
  }),
  api_keys: ApiKeysSchema,
  databases: z.object({
    pocketbase: PocketBaseConfigSchema,
    langtrace_postgres: DatabaseConfigSchema,
    langtrace_clickhouse: z.object({
      host: z.string(),
      user: z.string(),
      password: z.string(),
      database: z.string(),
    }),
    trigger_postgres: DatabaseConfigSchema,
    redis: RedisConfigSchema,
    neo4j: Neo4jConfigSchema,
  }),
  services: z.object({
    ai_api: AIApiConfigSchema, // Use the schema defined above
    whatsapp: WhatsAppConfigSchema,
    trigger: TriggerConfigSchema,
    resend: ResendConfigSchema,
    langtrace: LangTraceConfigSchema,
    dashboard: DashboardConfigSchema,
    upstash: UpstashConfigSchema,
    tts: TTSConfigSchema, // Add TTS configuration
  }),
  ai_models: z.object({
    premium: AIModelConfigSchema,
    standard: AIModelConfigSchema,
    basic: AIModelConfigSchema,
  }),
  access: z.object({
    allowed_users: z.array(z.string()),
    blocked_users: z.array(z.string()),
  }),
});

export type Config = z.infer<typeof ConfigSchema>;
